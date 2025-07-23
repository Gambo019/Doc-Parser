from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional


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
    
    # Storage settings (S3-compatible - works with AWS S3 and MinIO)
    S3_ENDPOINT_URL: Optional[str] = None  # Set for MinIO, leave None for AWS S3
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    # Legacy AWS settings (for backward compatibility)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    
    # Local development flags
    RUNNING_IN_LAMBDA: bool = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
    USE_LOCAL_STORAGE: bool = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # For backward compatibility, map AWS credentials to S3 credentials if S3 ones are not set
        if not hasattr(self, 'S3_ACCESS_KEY_ID') or not self.S3_ACCESS_KEY_ID:
            if self.AWS_ACCESS_KEY_ID:
                self.S3_ACCESS_KEY_ID = self.AWS_ACCESS_KEY_ID
                
        if not hasattr(self, 'S3_SECRET_ACCESS_KEY') or not self.S3_SECRET_ACCESS_KEY:
            if self.AWS_SECRET_ACCESS_KEY:
                self.S3_SECRET_ACCESS_KEY = self.AWS_SECRET_ACCESS_KEY
                
        if not hasattr(self, 'S3_REGION') or not self.S3_REGION:
            if self.AWS_REGION:
                self.S3_REGION = self.AWS_REGION

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables not defined in the model


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()