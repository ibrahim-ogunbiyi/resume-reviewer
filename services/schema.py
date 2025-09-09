from pydantic import BaseModel, Field


class JobDescriptionCheck(BaseModel):
    pillar: str = Field(description="The pillar being evaluated")
    problem: str = Field(
            description="The identified issue(s) in the resume relative to the job description. Be specific.")  # noqa: E501
    recommendation: str = Field(
        description="Actionable steps to revamp or improve this section so it better matches the job description.")  # noqa: E501


class JobDescriptionCheckSchema(BaseModel):
    checks: list[JobDescriptionCheck]


class FileSchema(BaseModel):
    doc_bytes: bytes
    ext: str