import os

from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


class Config:
    OPENAI_API_KEY = SecretStr(os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://paint_user:paint_pass@localhost:5432/paint_db"
    )
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8001))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 150))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

    @classmethod
    def validate(cls):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set")


config = Config()
