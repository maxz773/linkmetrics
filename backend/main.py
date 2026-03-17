from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
import uvicorn
import json
import os
import traceback

from config import get_api_key
from schemas import EvaluationResult, UserRequest, UserResponse
from llm_interface import AihubmixClient
from services import analyze_post_potential, CommentAnalyzer, ICPScorer, DataExtractor

def create_app() -> FastAPI:
   api_key = get_api_key()
   
   print("Initializing global AI models and clients...")
   # Global singleton initialization
   ai_client = AihubmixClient(api_key=api_key)
   comment_analyzer = CommentAnalyzer()
   icp_scorer = ICPScorer()
   print("Initialization complete.")

   app = FastAPI(title="LinkedIn Post Analyzer API")

   # Encapsulate synchronous scraping logic to put into the thread pool later
   def extract_data_sync(url_str: str, cookie_str: str):
      # Strong recommendation: Revert data_extractor.py to the auto-login version that receives cookie_str, otherwise the API will hang at input()
      with DataExtractor(headless=True) as extractor:
         # Assuming your scrape_post has been reverted to receive cookie_str:
         # post_data, comments_data = extractor.scrape_post(url_str, cookie_str) 
         post_data, comments_data = extractor.scrape_post(url_str) # If you are still using the manual version, pass the url temporarily here
         
         profiles_data = extractor.scrape_profiles(comments_data)
         
         output_dir = 'data'
         extractor.save_data(post_data, comments_data, profiles_data, output_dir=output_dir)
         return post_data, comments_data

   @app.post("/api/analyze", response_model=UserResponse)
   async def analyze_post(request: UserRequest):
      try:
         url_str = str(request.post_url)
         cookie_str = request.li_at_cookie

         # ==========================================
         # Step 1: Asynchronously schedule the scraper to extract data (prevent blocking the main thread)
         # ==========================================
         post_data, comments_data = await run_in_threadpool(extract_data_sync, url_str, cookie_str)
         
         if not post_data or not post_data.get('post_text'):
               raise HTTPException(status_code=400, detail="Scraping failed, could not retrieve post text.")
         
         post_text = post_data['post_text']

         # ==========================================
         # Step 2: Call the LLM to analyze the post's potential (Post Score)
         # ==========================================
         llm_response_str = analyze_post_potential(ai_client, post_text)
         try:
               # Strip potential markdown code block wrappers (e.g., ```json ... ```)
               clean_json_str = llm_response_str.strip().strip('```json').strip('```')
               llm_result = json.loads(clean_json_str)
               
               post_score = int(llm_result.get('score', 0))
               advice = llm_result.get('reason', 'No specific advice provided by LLM.')
         except Exception as e:
               print(f"Failed to parse LLM response: {llm_response_str}\nError: {e}")
               post_score = 0
               advice = "Analysis completed, but failed to parse LLM strict JSON output."

         # ==========================================
         # Step 3: Batch sentiment analysis to calculate comment quality (Comment Score)
         # ==========================================
         comment_texts = [c.get('text') for c in comments_data if c.get('text')]
         if comment_texts:
               # analyze returns a mean score (Float), convert to Int as per your Schema requirements
               comment_score = int(comment_analyzer.analyze(comment_texts))
         else:
               comment_score = 0

         # ==========================================
         # Step 4: Calculate ICP match score (ICP Score)
         # ==========================================
         comments_csv_path = 'data/comments_data.csv'
         if os.path.exists(comments_csv_path) and comments_data:
               # evaluate_batch returns a mean score out of 100, divide by 10 to match your schema (0-10)
               raw_icp_score = icp_scorer.evaluate_batch(comments_csv_path)
               icp_score_final = int(raw_icp_score / 10) 
         else:
               icp_score_final = 0

         # ==========================================
         # Step 5: Aggregate results and return according to Schema
         # ==========================================
         return UserResponse(
               post_score=post_score,
               comment_score=comment_score,
               ICP_score=icp_score_final,
               advice=advice
         )

      except Exception as e:
         # Print the complete error stack in the console for easy debugging
         traceback.print_exc() 
         raise HTTPException(status_code=500, detail=f"Error occurred during analysis: {str(e)}")

   return app

app = create_app()

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)