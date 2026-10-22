import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(override=True)

GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY      = os.getenv("TAVILY_API_KEY", "")
AVIATION_API_KEY    = os.getenv("AVIATION_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
SUPABASE_URL        = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY        = os.getenv("SUPABASE_KEY", "")
DATABASE_URL        = os.getenv("DATABASE_URL", "")
GROQ_MODEL          = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_llm(temperature: float = 0.3) -> ChatGroq:
    return ChatGroq(model=GROQ_MODEL, temperature=temperature)
