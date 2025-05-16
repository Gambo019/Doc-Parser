import boto3
from app.core.config import settings
from app.core.logger import logger

class S3Storage:
    def __init__(self):
        # When running in Lambda, we don't need to provide credentials
        # The Lambda execution role will provide access
        if settings.RUNNING_IN_LAMBDA:
            self.s3_client = boto3.client('s3')
        else:
            # For local development, use credentials from settings
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        self.bucket_name = settings.S3_BUCKET_NAME
        
    def upload_file(self, file_path, s3_key):
        """Upload file to S3 bucket"""
        try:
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                s3_key
            )
            logger.info(f"File uploaded to S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return False
            
    def download_file(self, s3_key, local_path):
        """Download file from S3 bucket"""
        try:
            self.s3_client.download_file(
                self.bucket_name, 
                s3_key, 
                local_path
            )
            logger.info(f"File downloaded from S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            return False 