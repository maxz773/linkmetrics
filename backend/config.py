import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(provider: str = "aihubmix") -> str:
    key = os.getenv(f"{provider.upper()}_API_KEY")      
    if not key:
        raise ValueError(f"ERROR: Unable to find the API key for {provider}，Please check the spelling.")
    return key