from langchain_groq import ChatGroq
from core.config import settings
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer



class ModelClass:

    keybert_model = None
    encoding_model = None
    llm = None

    @classmethod
    def get_keybert_model(cls):

        if cls.keybert_model is None:

            cls.keybert_model = KeyBERT(settings.EMBEDDING_MODEL)

            # warmup model
            _ = cls.keybert_model.extract_keywords("Dummy testing to warmup model")
    
    @classmethod
    def get_encoding_model(cls):

        if cls.encoding_model is None:

            cls.encoding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

            # warmup encoding model
            _ = cls.encoding_model.encode("Dummy testing to warm up model")

    @classmethod
    def get_llm(cls):

        if cls.llm is None:
            llm_model = ChatGroq(
                model=settings.MODEL_NAME,
                api_key=settings.LLM_API_KEY,
            )

            # warmup llm model
            _ = llm_model.invoke("Dummy testing to warm up model")

            cls.llm = llm_model
        
    @classmethod
    def load_models(cls):
        cls.get_encoding_model()
        cls.get_llm()
        cls.get_keybert_model()
        
    



