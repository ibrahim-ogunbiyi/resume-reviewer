import asyncio
import logging
from parser.parser_factory import get_parser
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form

from lib.model import ModelClass
from services.ats_checker import ats_checker
from services.resume_evaluation import compare_resume_to_job_description
from services.schema import ATSSchema, FileSchema, JobDescriptionCheckSchema

ModelClass().load_models()

logger = logging.getLogger("ats_checker")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = FastAPI()


@app.post("/api/analyse-resume")
async def analyze_resume_against_description(
    job_description: str=Form(...), file: UploadFile=File(...)
) -> tuple[JobDescriptionCheckSchema, ATSSchema]:
    
    # read content
    content = await file.read()
    ext = Path(file.filename).suffix

    # extract text
    with get_parser(doc_bytes=content, ext=ext) as parser:
        extracted_text = parser.extract_text()

    # schedule ats checker and resume evaluation task
    resume_evaluation_task = asyncio.create_task(
        compare_resume_to_job_description(
            resume_text=extracted_text, job_description=job_description
        )
    )

    ats_checker_task = asyncio.create_task(
        ats_checker(job_description=job_description, resume_text=extracted_text)
    )

    # execute task
    resume_evaluation_result: JobDescriptionCheckSchema = await resume_evaluation_task

    ats_checker_result: ATSSchema = await ats_checker_task

    return resume_evaluation_result, ats_checker_result


@app.get("/health")
async def wake_up_app() -> None:
    ModelClass().load_models()

    logger.info("Application Ready to Serve Traffic")

    return None