from pydantic import BaseModel, Field

# Define the structrue of the LLM response
class EvaluationResult(BaseModel):
    score: int = Field(description="Produce a score strictly between 0 and 10")
    reason: str = Field(description="Provide a comprehensive reason for the scoring")