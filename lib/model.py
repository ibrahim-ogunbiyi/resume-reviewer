import requests
from langchain_groq import ChatGroq

from core.config import settings


class ModelClass:
    llm = None

    @classmethod
    def warm_phrase_extraction_endpoint(cls) -> None:

        _ = requests.post(settings.KEYWORD_EXTRACTION_SERVICE_URL, json={"text": "Dummy testing to warm up endpoint"})
    
    @classmethod
    def warm_phrase_encoding_endpoint(cls) -> None:
         _ = requests.post(settings.ENCODING_SERVICE_URL, json={"text": "Dummy testing to warm up endpoint"})
    

    @classmethod
    def get_llm(cls) -> None:

        if cls.llm is None:
            llm_model = ChatGroq(
                model=settings.MODEL_NAME,
                api_key=settings.LLM_API_KEY,
            )

            # warmup llm model
            _ = llm_model.invoke("Dummy testing to warm up model")

            cls.llm = llm_model
        
    @classmethod
    def load_models(cls) -> None:
        cls.get_llm()   
        cls.warm_phrase_encoding_endpoint()
        cls.warm_phrase_extraction_endpoint()     
    



