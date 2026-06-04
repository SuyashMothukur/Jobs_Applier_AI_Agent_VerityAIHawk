#!/usr/bin/env python3
"""Validate data_folder configuration before running AIHawk or the API."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from main import ConfigError, ConfigValidator, FileManager  # noqa: E402
from src.resume_schemas.resume import Resume  # noqa: E402


def main() -> int:
    data_folder = ROOT / "data_folder"
    print(f"Checking configuration in {data_folder} ...")

    try:
        secrets_file, config_file, resume_file, output_folder = (
            FileManager.validate_data_folder(data_folder)
        )
        ConfigValidator.validate_config(config_file)
        ConfigValidator.validate_secrets(secrets_file)
        Resume(resume_file.read_text(encoding="utf-8"))
        output_folder.mkdir(parents=True, exist_ok=True)
    except (ConfigError, FileNotFoundError, Exception) as exc:
        print(f"FAIL: {exc}")
        return 1

    print("OK: data_folder is valid and ready to use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
