import streamlit as st
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
class Settings(BaseSettings):
    try:
        model_config = SettingsConfigDict(env_file=BASE_DIR/".env", env_file_encoding="utf-8")
        LLM_API_KEY: str = Field(validation_alias="groq_api_key")
    except Exception:
        LLM_API_KEY = st.secrets["GROQ_API_KEY"]
    MODEL_NAME: str = "openai/gpt-oss-20b"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L12-v2"
    ENCODING_SERVICE_URL: str = "https://ibrahim-geek-encode-and-extract-phrases.hf.space/get_encoding"
    KEYWORD_EXTRACTION_SERVICE_URL: str = "https://ibrahim-geek-encode-and-extract-phrases.hf.space/extract_keyword_phrases"


settings = Settings()