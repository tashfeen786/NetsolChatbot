import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_model_name():
    return os.getenv("MODEL_NAME", "gpt-4o-mini")