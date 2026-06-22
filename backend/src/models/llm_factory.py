import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(temperature=0.7, streaming=True):
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please set it in your .env file or as an environment variable."
        )

    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=os.getenv("MODEL_NAME", "gemini-2.5-flash-lite"),
        temperature=temperature,
        streaming=streaming,
    )