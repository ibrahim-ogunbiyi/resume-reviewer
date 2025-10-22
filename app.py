import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile

from lib.model import ModelClass
from parser.parser_factory import get_parser
from services.ats_checker import ats_checker
from services.resume_evaluation import compare_resume_to_job_description
from services.schema import ATSSchema, FileSchema, JobDescriptionCheckSchema, ResumeReviewSchema

ModelClass().load_models()

logger = logging.getLogger("ats_checker")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = FastAPI()


@app.post("/api/analyse-resume")
async def analyze_resume_against_description(
    job_description: str = Form(...), file: UploadFile = File(...)
) -> ResumeReviewSchema:
    logger.info("Beginning Extracting text from PDF")
    # read content
    content = await file.read()
    ext = Path(file.filename).suffix

    # extract text
    with get_parser(doc_bytes=content, ext=ext) as parser:
        extracted_text = parser.extract_text()
    logger.info(f"Finished Extracting text from PDF: {extracted_text[:100]}")

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

    result = ResumeReviewSchema(
        ats_checker_result=ats_checker_result, resume_evaluation_result=resume_evaluation_result
    )
    return result.model_dump()


@app.get("/health")
async def wake_up_app() -> None:
    ModelClass().load_models()

    logger.info("Application Ready to Serve Traffic")

    return None
