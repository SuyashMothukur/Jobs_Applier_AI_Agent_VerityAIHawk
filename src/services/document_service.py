"""Shared resume and cover letter generation for CLI and API."""

import base64
from pathlib import Path
from typing import Optional, Tuple

from src.libs.resume_and_cover_builder import ResumeFacade, ResumeGenerator, StyleManager
from src.logging import logger
from src.resume_schemas.resume import Resume
from src.utils.chrome_utils import init_browser


def _resolve_style(style_manager: StyleManager, style_name: Optional[str]) -> None:
    available_styles = style_manager.get_styles()
    if not available_styles:
        raise ValueError("No resume styles are available.")

    if style_name:
        if style_name not in available_styles:
            available = ", ".join(available_styles)
            raise ValueError(f"Unknown style '{style_name}'. Available: {available}")
        style_manager.set_selected_style(style_name)
        return

    default_style = next(iter(available_styles))
    style_manager.set_selected_style(default_style)
    logger.info(f"No style specified; using default: {default_style}")


def _build_resume_facade(
    llm_api_key: str,
    plain_text_resume_path: Path,
    output_path: Path,
    style_name: Optional[str] = None,
) -> ResumeFacade:
    plain_text_resume = plain_text_resume_path.read_text(encoding="utf-8")

    style_manager = StyleManager()
    _resolve_style(style_manager, style_name)

    resume_generator = ResumeGenerator()
    resume_object = Resume(plain_text_resume)
    resume_generator.set_resume_object(resume_object)

    resume_facade = ResumeFacade(
        api_key=llm_api_key,
        style_manager=style_manager,
        resume_generator=resume_generator,
        resume_object=resume_object,
        output_path=output_path,
    )
    resume_facade.set_driver(init_browser())
    return resume_facade


def list_available_styles() -> dict:
    style_manager = StyleManager()
    styles = style_manager.get_styles()
    return {
        name: {"file": file_name, "author": author_link}
        for name, (file_name, author_link) in styles.items()
    }


def generate_resume_pdf(
    llm_api_key: str,
    plain_text_resume_path: Path,
    output_path: Path,
    style_name: Optional[str] = None,
) -> Tuple[bytes, Path]:
    resume_facade = _build_resume_facade(
        llm_api_key, plain_text_resume_path, output_path, style_name
    )
    result_base64 = resume_facade.create_resume_pdf()
    pdf_data = base64.b64decode(result_base64)

    saved_path = output_path / "resume_base.pdf"
    saved_path.parent.mkdir(parents=True, exist_ok=True)
    saved_path.write_bytes(pdf_data)
    logger.info(f"Resume saved at: {saved_path}")
    return pdf_data, saved_path


def generate_job_tailored_resume_pdf(
    llm_api_key: str,
    plain_text_resume_path: Path,
    output_path: Path,
    job_url: str,
    style_name: Optional[str] = None,
) -> Tuple[bytes, Path]:
    resume_facade = _build_resume_facade(
        llm_api_key, plain_text_resume_path, output_path, style_name
    )
    resume_facade.link_to_job(job_url)
    result_base64, suggested_name = resume_facade.create_resume_pdf_job_tailored()
    pdf_data = base64.b64decode(result_base64)

    saved_path = output_path / suggested_name / "resume_tailored.pdf"
    saved_path.parent.mkdir(parents=True, exist_ok=True)
    saved_path.write_bytes(pdf_data)
    logger.info(f"Tailored resume saved at: {saved_path}")
    return pdf_data, saved_path


def generate_cover_letter_pdf(
    llm_api_key: str,
    plain_text_resume_path: Path,
    output_path: Path,
    job_url: str,
    style_name: Optional[str] = None,
) -> Tuple[bytes, Path]:
    resume_facade = _build_resume_facade(
        llm_api_key, plain_text_resume_path, output_path, style_name
    )
    resume_facade.link_to_job(job_url)
    result_base64, suggested_name = resume_facade.create_cover_letter()
    pdf_data = base64.b64decode(result_base64)

    saved_path = output_path / suggested_name / "cover_letter_tailored.pdf"
    saved_path.parent.mkdir(parents=True, exist_ok=True)
    saved_path.write_bytes(pdf_data)
    logger.info(f"Cover letter saved at: {saved_path}")
    return pdf_data, saved_path
