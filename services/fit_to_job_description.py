import re
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

    return result

