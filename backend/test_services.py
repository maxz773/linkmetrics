# ================= Testing =================
if __name__ == "__main__":
    from llm_interface import AihubmixClient
    from config import get_api_key
    from services import analyze_post_potential, CommentAnalyzer, ICPScorer
    from utils import load_post_text, load_comments_text
    import pandas as pd

    aihubmix_client = AihubmixClient(api_key=get_api_key())

    print("Loading post...")
    post_text = load_post_text('data/post_data.csv')

    print("Analyzing post...")
    print(analyze_post_potential(client=aihubmix_client, post_text=post_text, model="gemini-2.0-flash-lite"))

    print("Loading comments...")
    comment_text = load_comments_text('data/comments_data.csv')

    print("Analyzing comments...")
    analyzer = CommentAnalyzer()
    print(analyzer.analyze(comment_text))
    

    print("Invoking ICP Scorer...")
    # 1. Set our ideal customer baseline (Reference ICP)
    REFERENCE_ICP = "Director, Chief, or Lead decision maker in Sustainability, AI, Software, or Technology."
    
    # 2. Instantiate the scorer
    scorer = ICPScorer(reference_icp_text=REFERENCE_ICP)
    
    # 3. Run scoring (assuming the file is in the data directory)
    result_df = scorer.evaluate_batch("data/comments_data.csv")
    