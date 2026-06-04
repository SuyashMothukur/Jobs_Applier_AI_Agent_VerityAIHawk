"""Configuration validation routes for the AIHawk API."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("/validate")
def validate_configuration() -> dict:
    """Report whether local config and resume data are valid (no secrets returned)."""
    from src.api.server import get_context

    ctx = get_context()
    resume_path = ctx.plain_text_resume_path
    resume_ok = resume_path.exists()
    return {
        "status": "ok" if resume_ok else "degraded",
        "checks": {
            "resume_file_exists": resume_ok,
            "resume_file": str(resume_path),
            "output_directory": str(ctx.output_path),
            "work_preferences_loaded": bool(ctx.work_preferences),
        },
        "message": "Configuration is valid" if resume_ok else "Resume file missing",
    }
