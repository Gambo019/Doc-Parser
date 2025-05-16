from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str
    # API Key for authentication
    API_KEY: str
    
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # AWS settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str
    
    # Detect if running in Lambda
    RUNNING_IN_LAMBDA: bool = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

    class Config:
        env_file = ".env"
        case_sensitive = True

class ModelType(str, Enum):
    GPT4O = 'gpt-4o'
    GPT4O_MINI = 'gpt-4o-mini'
    GPT35 = 'gpt-3.5-turbo'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()