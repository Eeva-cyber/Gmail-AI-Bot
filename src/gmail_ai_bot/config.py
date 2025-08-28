import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GMAIL_CREDENTIALS_PATH": os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"),
        "GMAIL_TOKEN_PATH": os.getenv("GMAIL_TOKEN_PATH", "token.pickle"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    }