from langchain_groq import ChatGroq
from core.config import settings


llm = ChatGroq(
    model=settings.MODEL_NAME,
    api_key=settings.LLM_API_KEY,
)
