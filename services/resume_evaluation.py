import json
import re

import numpy as np
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from lib.model import ModelClass
from prompts.prompt import JOB_DESCRIPTION_CHECK
from services.schema import JobDescriptionCheckSchema

ModelClass.load_models()

async def compare_resume_to_job_description(
    resume_text:str, job_description: str
) -> JobDescriptionCheckSchema:
    
    parser = JsonOutputParser(pydantic_object=JobDescriptionCheckSchema)

    prompt = PromptTemplate(
        template=JOB_DESCRIPTION_CHECK,
        input_variables=["user_resume_or_cv", "job_description"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )

    llm = ModelClass().llm

    chain = prompt | llm

    result = await chain.ainvoke(
        {"user_resume_or_cv": resume_text, "job_description": job_description}
    )

    result = re.sub(r"^```json|```", "", result.content.strip(), flags=re.MULTILINE)

    result = json.loads(result)

    return result
