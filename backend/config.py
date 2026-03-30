import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(provider: str = "aihubmix") -> str:
    secret_file = f"/run/secrets/{provider}_api_key"    
    if os.path.exists(secret_file):
        with open(secret_file, "r") as f:
            key = f.read().strip()
            return key
        
    key = os.getenv(f"{provider.upper()}_API_KEY")

    if not key:
        raise ValueError(f"Missing API Key: Checked both {secret_file} and ENV")
    
    return key