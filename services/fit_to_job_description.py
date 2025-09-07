import re
import json
import torch
import numpy as np
from sentence_transformers import util
from lib.model import ModelClass
from langchain_core.prompts import PromptTemplate
from prompts.prompt import JOB_DESCRIPTION_CHECK
from .schema import JobDescriptionCheckSchema, FileSchema
from langchain_core.output_parsers import JsonOutputParser
from parser.parser_factory import get_parser


def extract_phrases(text:str, ngram_range:tuple, top_n:int):

    keybert_model = ModelClass().keybert_model


    key_phrases = keybert_model.extract_keywords(docs=text, keyphrase_ngram_range=ngram_range, top_n=top_n)

    result = [phrase[0] for phrase in key_phrases]

    return result


def ats_checker(job_description:str, resume_text:str):

    # initialize model
    keybert_model = ModelClass().keybert_model
    encoding_model = ModelClass().encoding_model

    # extract keyword phrases
    job_description_phrases = extract_phrases(text=job_description, ngram_range=(1, 3), top_n=-1)


    # get embeddings.
    job_description_embeddings = encoding_model.encode(job_description_phrases)
    
    resume_phrases = extract_phrases(text=resume_text, ngram_range=(1, 3), top_n=-1)

    all_similarities = []

    for resume_phrase in resume_phrases:

        phrase_embedding = encoding_model.encode(resume_phrase)
        similarities = util.cos_sim(phrase_embedding, job_description_embeddings)

        highest_similary = torch.max(similarities)

        all_similarities.append(highest_similary)

    phrases = {"job_description_phrases": job_description_phrases, "resume_phrases":resume_phrases}

    return np.mean(all_similarities), phrases




def fit_to_job_description(file:FileSchema, job_description:str):

    with get_parser(doc_bytes=file.doc_bytes, ext=file.ext) as parser:
        extracted_text = parser.extract_text()

    parser = JsonOutputParser(pydantic_object=JobDescriptionCheckSchema)

    prompt = PromptTemplate(
        template=JOB_DESCRIPTION_CHECK,
        input_variables=["user_resume_or_cv", "job_description"],
        partial_variables={"output_format":parser.get_format_instructions()}
    )

    llm = ModelClass().llm

    chain =  prompt | llm

    result = chain.invoke(

        {
            "user_resume_or_cv": extracted_text,
            "job_description": job_description
        }
    )

    result = re.sub(r'^```json|```', '', result.content.strip(), flags=re.MULTILINE)

    result = json.loads(result)

    ats_checker_result = ats_checker(job_description=job_description, resume_text=extracted_text)
    return result, ats_checker_result



