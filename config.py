# In this file, you can set the configurations of the app.

import os

from src.utils.constants import DEBUG, ERROR, LLM_MODEL, OPENAI

# HTTP API (used by Verity hosted audit and external clients)
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "")
BACKEND_URL = BACKEND_PUBLIC_URL or f"http://localhost:{BACKEND_PORT}"

#config related to logging must have prefix LOG_
LOG_LEVEL = 'ERROR'
LOG_SELENIUM_LEVEL = ERROR
LOG_TO_FILE = False
LOG_TO_CONSOLE = False

MINIMUM_WAIT_TIME_IN_SECONDS = 60

JOB_APPLICATIONS_DIR = "job_applications"
JOB_SUITABILITY_SCORE = 7

JOB_MAX_APPLICATIONS = 5
JOB_MIN_APPLICATIONS = 1

LLM_MODEL_TYPE = 'openai'
LLM_MODEL = 'gpt-4o-mini'
# Only required for OLLAMA models
LLM_API_URL = ''
