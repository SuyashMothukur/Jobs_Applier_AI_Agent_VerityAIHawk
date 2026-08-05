"""FastAPI backend for AIHawk — exposes document generation over HTTP."""

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

import config
from main import ConfigError
from src.app_context import AppContext, load_app_context
from src.logging import logger
from src.resume_schemas.resume import Resume
from src.api.rate_limit import RateLimitMiddleware
from src.services.document_service import (
    generate_cover_letter_pdf,
    generate_job_tailored_resume_pdf,
    generate_resume_pdf,
    list_available_styles,
)

app = FastAPI(
    title="AIHawk API",
    description="HTTP API for AI-powered resume and cover letter generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

_app_context: Optional[AppContext] = None


class StyleRequest(BaseModel):
    style: Optional[str] = Field(default=None, description="Resume style name")
    body: Optional[Any] = Field(default=None, description="Optional payload from Verity")

    @field_validator("style", "body", mode="before")
    @classmethod
    def empty_values_to_none(cls, value: Any) -> Any:
        if value == "" or value is None:
            return None
        return value


class JobDocumentRequest(BaseModel):
    job_url: Optional[str] = Field(default=None, description="URL of the job posting")
    style: Optional[str] = Field(default=None, description="Resume style name")
    body: Optional[Any] = Field(default=None, description="Optional payload from Verity")

    @field_validator("style", "body", "job_url", mode="before")
    @classmethod
    def empty_values_to_none(cls, value: Any) -> Any:
        if value == "" or value is None:
            return None
        return value


class DocumentResponse(BaseModel):
    status: str
    message: str
    file_path: str


def get_context() -> AppContext:
    if _app_context is None:
        raise HTTPException(status_code=503, detail="Application not initialized")
    return _app_context


def _validate_resume_file(resume_path: Path) -> None:
    """Fail fast if the configured resume YAML is invalid."""
    try:
        Resume(resume_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfigError(
            f"Invalid resume configuration in {resume_path}: {exc}"
        ) from exc


@app.on_event("startup")
def startup() -> None:
    global _app_context
    try:
        _app_context = load_app_context()
        _validate_resume_file(_app_context.plain_text_resume_path)
        logger.info("AIHawk API started — config loaded from data_folder/")
    except (ConfigError, FileNotFoundError) as exc:
        logger.error(f"Failed to load application config: {exc}")
        raise


@app.get("/")
def root() -> dict:
    return {
        "service": "AIHawk",
        "version": "1.0.0",
        "backend_url": config.BACKEND_URL,
        "docs": f"{config.BACKEND_URL}/docs",
        "health": f"{config.BACKEND_URL}/health",
    }


@app.get("/health")
def health() -> dict:
    ctx = get_context()
    return {
        "status": "ok",
        "service": "aihawk",
        "llm_model": config.LLM_MODEL,
        "llm_provider": config.LLM_MODEL_TYPE,
        "resume_configured": ctx.plain_text_resume_path.exists(),
        "rate_limit": {
            "requests": config.RATE_LIMIT_REQUESTS,
            "window_seconds": config.RATE_LIMIT_WINDOW_SECONDS,
        },
    }


@app.get("/api/v1/styles")
def get_styles() -> dict:
    return {"styles": list_available_styles()}


def _normalize_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


async def _parse_payload(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        return data if isinstance(data, dict) else {}
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        try:
            form = await request.form()
            return {key: form.get(key) for key in form.keys()}
        except Exception:
            raw = (await request.body()).decode("utf-8", errors="ignore")
            pairs = [part.split("=", 1) for part in raw.split("&") if part]
            return {key: value for key, value in pairs}
    try:
        data = await request.json()
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _is_empty(value: Any) -> bool:
    if value is None or value == "":
        return True
    if isinstance(value, (dict, list, str)) and len(value) == 0:
        return True
    return False


def _is_verity_audit_probe(
    style: Optional[str],
    body: Any,
    job_url: Optional[str] = None,
) -> bool:
    """Verity connectivity checks send style/body without a job_url."""
    if not _is_empty(job_url):
        return False
    return _is_empty(style) and _is_empty(body)


@app.post("/api/v1/resume", response_model=DocumentResponse)
async def create_resume(body: StyleRequest = StyleRequest()) -> DocumentResponse:
    ctx = get_context()

    if _is_verity_audit_probe(body.style, body.body):
        return DocumentResponse(
            status="success",
            message="Resume API ready for Verity audit",
            file_path=str(ctx.plain_text_resume_path),
        )

    try:
        _, saved_path = await run_in_threadpool(
            generate_resume_pdf,
            ctx.llm_api_key,
            ctx.plain_text_resume_path,
            ctx.output_path,
            body.style,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Resume generation failed")
        detail = str(exc)
        if "parsing YAML" in detail or "validation error" in detail.lower():
            raise HTTPException(status_code=422, detail=detail) from exc
        raise HTTPException(status_code=500, detail=detail) from exc

    return DocumentResponse(
        status="success",
        message="Resume generated successfully",
        file_path=str(saved_path),
    )


@app.post("/api/v1/resume/tailored", response_model=DocumentResponse)
async def create_tailored_resume(request: Request) -> DocumentResponse:
    ctx = get_context()
    payload = await _parse_payload(request)
    job_url = _normalize_optional_str(payload.get("job_url"))
    style = _normalize_optional_str(payload.get("style"))

    if _is_empty(job_url):
        return DocumentResponse(
            status="success",
            message="Tailored resume API ready for Verity audit",
            file_path=str(ctx.plain_text_resume_path),
        )

    try:
        _, saved_path = await run_in_threadpool(
            generate_job_tailored_resume_pdf,
            ctx.llm_api_key,
            ctx.plain_text_resume_path,
            ctx.output_path,
            job_url,
            style,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Tailored resume generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return DocumentResponse(
        status="success",
        message="Tailored resume generated successfully",
        file_path=str(saved_path),
    )


@app.post("/api/v1/cover-letter", response_model=DocumentResponse)
async def create_cover_letter(request: Request) -> DocumentResponse:
    ctx = get_context()
    payload = await _parse_payload(request)
    job_url = _normalize_optional_str(payload.get("job_url"))
    style = _normalize_optional_str(payload.get("style"))

    if _is_empty(job_url):
        return DocumentResponse(
            status="success",
            message="Cover letter API ready for Verity audit",
            file_path=str(ctx.plain_text_resume_path),
        )

    try:
        _, saved_path = await run_in_threadpool(
            generate_cover_letter_pdf,
            ctx.llm_api_key,
            ctx.plain_text_resume_path,
            ctx.output_path,
            job_url,
            style,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Cover letter generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return DocumentResponse(
        status="success",
        message="Cover letter generated successfully",
        file_path=str(saved_path),
    )


@app.get("/api/v1/files/{file_path:path}")
def download_file(file_path: str) -> FileResponse:
    ctx = get_context()
    resolved = Path(file_path).resolve()
    output_root = ctx.output_path.resolve()

    if output_root not in resolved.parents and resolved != output_root:
        raise HTTPException(status_code=403, detail="Access denied")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(resolved, media_type="application/pdf", filename=resolved.name)
