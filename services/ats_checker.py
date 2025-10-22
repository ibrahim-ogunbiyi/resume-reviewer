import asyncio
import logging

import httpx
import numpy as np
import torch
from sentence_transformers.util import cos_sim

from core.config import settings
from services.schema import ATSSchema

logger = logging.getLogger("ats_checker")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def extract_phrases(text: list[str] | str) -> list:
    print(settings.KEYWORD_EXTRACTION_SERVICE_URL)

    try:
        timeout = httpx.Timeout(15.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url=settings.KEYWORD_EXTRACTION_SERVICE_URL, json={"text": text}
            )

        return response.json()
    except Exception as e:
        logger.warning(f"Unable to Extract Phrases: {e}")


async def encode_text(text: list[str] | str) -> list:
    try:
        timeout = httpx.Timeout(15.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url=settings.ENCODING_SERVICE_URL, json={"text": text})

        return response.json()
    except Exception as e:
        logger.warning(f"Unable to Encode Phrases: {e}")
        return None, None


async def extract_resume_and_job_description(
    job_description_text: str, resume_text: str
) -> tuple[list, list]:
    try:
        jd_task = extract_phrases(job_description_text)
        resume_task = extract_phrases(resume_text)
        jd_phrases, resume_phrases = await asyncio.gather(jd_task, resume_task)

        return jd_phrases, resume_phrases
    except Exception as e:
        logger.warning(f"Unable to Extract Phrases from Resume and JD: {e}")
        return None, None


async def encode_resume_and_jd_phrases(
    job_description_phrases: str, resume_phrases: str
) -> tuple[list, list]:
    try:
        jd_task = encode_text(job_description_phrases)
        resume_task = encode_text(resume_phrases)
        jd_embeddings, resume_embeddings = await asyncio.gather(jd_task, resume_task)

        return torch.Tensor(jd_embeddings), torch.Tensor(resume_embeddings)
    except Exception as e:
        logger.warning(f"Unable to Encode Resume and JD Phrases: {e}")


async def ats_checker(job_description: str, resume_text: str) -> ATSSchema:
    try:
        # extract keyword phrases from JD and Resume
        jd_phrases, resume_phrases = await extract_resume_and_job_description(
            job_description_text=job_description, resume_text=resume_text
        )

        jd_embeddings, resume_embeddings = await encode_resume_and_jd_phrases(
            job_description_phrases=jd_phrases, resume_phrases=resume_phrases
        )

        all_similarities = []

        matched_phrases = []

        for i, phrase_embedding in enumerate(resume_embeddings):
            similarities = cos_sim(phrase_embedding, jd_embeddings)

            highest_similary = torch.max(similarities)

            all_similarities.append(highest_similary)

            if highest_similary >= 0.6:
                matched_phrases.append(resume_phrases[i])

        phrases = {
            "job_description_phrases": jd_phrases,
            "resume_phrases": resume_phrases,
            "matched_phrases": matched_phrases,
        }

        scores = {
            "mean": (np.mean(all_similarities) * 100),
            "std": (np.std(all_similarities) * 100),
        }

        return scores, phrases

    except Exception as e:
        logger.warning(f"Unable to Perform ATS Checker: {e}")
        return None, None
