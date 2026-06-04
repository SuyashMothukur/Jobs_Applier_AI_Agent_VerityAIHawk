"""Pydantic response models for the AIHawk API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    llm_model: str
    llm_provider: str
    resume_configured: bool


class ServiceInfoResponse(BaseModel):
    status: str
    service: str
    version: str
    backend_url: str
    llm_model: str
    llm_provider: str
    resume_configured: bool
    endpoints: dict[str, str] = Field(
        description="Map of logical names to API paths"
    )
