import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = "Atlas"

ENVIRONMENT = os.getenv("ATLAS_ENV", "development")

FINANCIAL_API_KEY = os.getenv("FINANCIAL_API_KEY")

FINANCIAL_API_BASE_URL = os.getenv(
    "FINANCIAL_API_BASE_URL",
    "",
)
