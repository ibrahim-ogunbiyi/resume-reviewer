import json
import re
from parser.parser_factory import get_parser

import numpy as np
import requests
import torch
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from sentence_transformers import util

from lib.model import ModelClass
from prompts.prompt import JOB_DESCRIPTION_CHECK

from .schema import FileSchema, JobDescriptionCheckSchema


def extract_phrases(text:list[str] | str) -> list:
    
    url = "https://ibrahim-geek-encode-and-extract-phrases.hf.space/extract_keyword_phrases"

    response = requests.post(url=url, json={"text":text})

    return response.json()

def encode_text(text:list[str] | str) -> list:
    
    url = "https://ibrahim-geek-encode-and-extract-phrases.hf.space/get_encoding"

    response = requests.post(url=url, json={"text":text})

    return response.json()


def ats_checker(job_description: str, resume_text: str) -> tuple[dict, dict]:

    # extract keyword phrases
    job_description_phrases = extract_phrases(text=job_description)

    resume_phrases = extract_phrases(text=resume_text)

    # get embeddings.
    job_description_embeddings = torch.Tensor(encode_text(job_description_phrases))

    phrases_embeddings = torch.Tensor(encode_text(resume_phrases))

    all_similarities = []

    matched_phrases = []

    for i, phrase_embedding in enumerate(phrases_embeddings):
        similarities = util.cos_sim(phrase_embedding, job_description_embeddings)

        highest_similary = torch.max(similarities)

        all_similarities.append(highest_similary)

        if highest_similary >=0.6:
            matched_phrases.append(resume_phrases[i])

    phrases = {
        "job_description_phrases": job_description_phrases,
        "resume_phrases": resume_phrases, "matched_phrases": matched_phrases
    }
    
    scores = {"mean": (np.mean(all_similarities)*100), "std":(np.std(all_similarities)*100)}

    return scores, phrases


def fit_to_job_description(file: FileSchema, job_description: str) -> tuple[dict, tuple[dict, dict]]:
    with get_parser(doc_bytes=file.doc_bytes, ext=file.ext) as parser:

        extracted_text = parser.extract_text()

    parser = JsonOutputParser(pydantic_object=JobDescriptionCheckSchema)

    prompt = PromptTemplate(
        template=JOB_DESCRIPTION_CHECK,
        input_variables=["user_resume_or_cv", "job_description"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )

    llm = ModelClass().llm

    chain = prompt | llm

    result = chain.invoke({"user_resume_or_cv": extracted_text, "job_description": job_description})

    result = re.sub(r"^```json|```", "", result.content.strip(), flags=re.MULTILINE)

    result = json.loads(result)

    ats_checker_result = ats_checker(job_description=job_description, resume_text=extracted_text)
    
    return result, ats_checker_result
