import boto3
from botocore.client import Config
from app.core.config import settings
from app.core.logger import logger

class S3Storage:
    def __init__(self):
        # Configure S3 client for MinIO or AWS S3
        if hasattr(settings, 'S3_ENDPOINT_URL') and settings.S3_ENDPOINT_URL:
            # MinIO configuration
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION,
                config=Config(signature_version='s3v4')
            )
            logger.info(f"Initialized MinIO storage with endpoint: {settings.S3_ENDPOINT_URL}")
        elif settings.RUNNING_IN_LAMBDA:
            # AWS Lambda configuration
            self.s3_client = boto3.client('s3')
            logger.info("Initialized AWS S3 storage for Lambda")
        else:
            # Local development with AWS S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION
            )
            logger.info("Initialized AWS S3 storage for local development")
            
        self.bucket_name = settings.S3_BUCKET_NAME
        
    def upload_file(self, file_path, s3_key):
        """Upload file to S3 bucket or MinIO"""
        try:
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                s3_key
            )
            logger.info(f"File uploaded to storage: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file to storage: {str(e)}")
            return False
            
    def download_file(self, s3_key, local_path):
        """Download file from S3 bucket or MinIO"""
        try:
            self.s3_client.download_file(
                self.bucket_name, 
                s3_key, 
                local_path
            )
            logger.info(f"File downloaded from storage: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file from storage: {str(e)}")
            return False 
            
    def get_file_url(self, s3_key, expiration=3600):
        """Generate a presigned URL for file access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None
            
    def get_public_url(self, s3_key):
        """Get public URL for file (works with MinIO and public S3 buckets)"""
        if hasattr(settings, 'S3_ENDPOINT_URL') and settings.S3_ENDPOINT_URL:
            # MinIO public URL
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"
        else:
            # AWS S3 public URL
            return f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}" 