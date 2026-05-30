"""Load validated application configuration for CLI and API."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from main import ConfigValidator, FileManager


@dataclass
class AppContext:
    llm_api_key: str
    plain_text_resume_path: Path
    output_path: Path
    work_preferences: dict


def load_app_context(data_folder: Optional[Path] = None) -> AppContext:
    folder = data_folder or Path("data_folder")
    secrets_file, config_file, plain_text_resume_file, output_folder = (
        FileManager.validate_data_folder(folder)
    )
    work_preferences = ConfigValidator.validate_config(config_file)
    llm_api_key = ConfigValidator.validate_secrets(secrets_file)

    return AppContext(
        llm_api_key=llm_api_key,
        plain_text_resume_path=plain_text_resume_file,
        output_path=output_folder,
        work_preferences=work_preferences,
    )
