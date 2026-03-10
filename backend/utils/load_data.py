import pandas as pd

def load_post_text(csv_path: str) -> str:
    df = pd.read_csv(csv_path)
    return df["post_text"][0]

def load_comments_text(csv_path: str) -> list[str]:
    df = pd.read_csv(csv_path)
    return df['text'].tolist()
