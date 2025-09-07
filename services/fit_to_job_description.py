import re
import json
import torch
from sentence_transformers import util, SentenceTransformer
from keybert import KeyBERT
from lib.llm import llm
from langchain_core.prompts import PromptTemplate
from prompts.prompt import JOB_DESCRIPTION_CHECK
from .schema import JobDescriptionCheckSchema, FileSchema
from langchain_core.output_parsers import JsonOutputParser
from parser.parser_factory import get_parser



def fit_to_job_description(file:FileSchema, job_description:str):

    with get_parser(doc_bytes=file.doc_bytes, ext=file.ext) as parser:
        extracted_text = parser.extract_text()

    parser = JsonOutputParser(pydantic_object=JobDescriptionCheckSchema)

    prompt = PromptTemplate(
        template=JOB_DESCRIPTION_CHECK,
        input_variables=["user_resume_or_cv", "job_description"],
        partial_variables={"output_format":parser.get_format_instructions()}
    )

    chain =  prompt | llm

    result = chain.invoke(

        {
            "user_resume_or_cv": extracted_text,
            "job_description": job_description
        }
    )

    result = re.sub(r'^```json|```', '', result.content.strip(), flags=re.MULTILINE)

    result = json.loads(result)
    return result



def ats_checker(job_description:str, resume_text:str):

    keybert_model = KeyBERT("all-MiniLM-L6-v2")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    job_description_phrases = keybert_model.extract_keywords(docs=job_description, keyphrase_ngram_range=(1, 3))

    job_description_embeddings = embedding_model.encode(job_description_phrases)
    
    resume_phrases = keybert_model.extract_keywords(docs=resume_text, keyphrase_ngram_range=(1, 3))

    all_similarities = []

    for resume_phrase in resume_phrases:

        phrase_embedding = embedding_model.encode(resume_phrase)
        similarities = util.cos_sim(phrase_embedding, job_description_embeddings)

        highest_similary = torch.max(similarities)

        all_similarities.append(highest_similary)

    return torch.mean(all_similarities)







