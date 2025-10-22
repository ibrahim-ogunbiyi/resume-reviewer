import asyncio
import logging

import aiohttp
import numpy as np
import torch
from sentence_transformers.util import cos_sim

from core.config import settings
from services.schema import ATSSchema

logger = logging.getLogger("ats_checker")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def extract_phrases(text: list[str] | str, session: aiohttp.ClientSession) -> list:
    try:
        logger.info("Beginning Extracting Phrases from Text")
        async with session.post(
            settings.KEYWORD_EXTRACTION_SERVICE_URL, json={"text": text}
        ) as url_response:
            response = await url_response.json()

        logger.info("Finished Extracting Text from Text")

        return response
    except aiohttp.ClientTimeout:
        logger.warning("Unable to Extract Phrases: request timed out")
    except aiohttp.ClientHttpProxyError as e:
        logger.warning(f"Unable to Extract Phrases: HTTP error {e.response.status_code}")
    except aiohttp.ClientResponseError as e:
        logger.warning(f"Unable to Extract Phrases: request failed - {e}")
    except Exception:
        logger.exception("Unexpected error during phrase extraction")


async def encode_text(text: list[str] | str, session: aiohttp.ClientSession) -> list:
    try:
        logger.info("Beginning Encoding Text")
        async with session.post(settings.ENCODING_SERVICE_URL, json={"text": text}) as url_response:
            response = await url_response.json()
        logger.info("Finished Encoding Text")
        return response
    except Exception as e:
        logger.warning(f"Unable to Encode Phrases: {e}")
        return None, None


async def extract_resume_and_job_description(
    job_description_text: str, resume_text: str
) -> tuple[list, list]:
    try:
        async with aiohttp.ClientSession() as session:
            jd_task = extract_phrases(job_description_text, session=session)
            resume_task = extract_phrases(resume_text, session=session)
            jd_phrases, resume_phrases = await asyncio.gather(jd_task, resume_task)

        return jd_phrases, resume_phrases
    except Exception as e:
        logger.warning(f"Unable to Extract Phrases from Resume and JD: {e}")
        return None, None


async def encode_resume_and_jd_phrases(
    job_description_phrases: str, resume_phrases: str
) -> tuple[list, list]:
    try:
        async with aiohttp.ClientSession() as session:
            jd_task = encode_text(job_description_phrases, session=session)
            resume_task = encode_text(resume_phrases, session=session)
            jd_embeddings, resume_embeddings = await asyncio.gather(jd_task, resume_task)

        return torch.Tensor(jd_embeddings), torch.Tensor(resume_embeddings)
    except Exception as e:
        logger.warning(f"Unable to Encode Resume and JD Phrases: {e}")


async def ats_checker(job_description: str, resume_text: str) -> ATSSchema:
    try:
        logger.info("Beginning ATS Check")
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

        unmatched_phrases = [phrase for phrase in jd_phrases if phrase not in matched_phrases]
        
        phrases = {
            "job_description_phrases": jd_phrases,
            "resume_phrases": resume_phrases,
            "matched_phrases": matched_phrases,
            "unmatched_phrases": unmatched_phrases
        }

        scores = {
            "mean": (np.mean(all_similarities) * 100),
            "std": (np.std(all_similarities) * 100),
        }

        result = ATSSchema(score=scores, phrases=phrases)

        logger.info("Finished ATS Check")
        return result.model_dump()

    except Exception as e:
        logger.warning(f"Unable to Perform ATS Checker: {e}")
        return None, None
