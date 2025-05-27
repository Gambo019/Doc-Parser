from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import Dict, Any
from tempfile import NamedTemporaryFile
import tempfile
from pydantic import BaseModel

# Import the DocumentProcessor from your existing code
from app.services.document_processor import DocumentProcessor
from app.services.pbm_document_processor import PBMDocumentProcessor
from app.utils.file_utils import calculate_file_hash
from app.core.database import Database
from app.core.logger import logger
from app.core.task_manager import TaskManager, TaskStatus
from app.core.storage import S3Storage

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set Lambda's temp directory
tempfile.tempdir = '/tmp'

# Initialize task manager
task_manager = TaskManager()

# Add this model for the internal endpoint
class InternalProcessRequest(BaseModel):
    s3_key: str
    file_hash: str
    original_filename: str
    task_id: str

# Add this new model for PBM internal processing
class InternalProcessPBMRequest(BaseModel):
    s3_key: str
    file_hash: str
    original_filename: str
    task_id: str

@app.post("/api/process-document")
async def process_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    # Create temporary file in Lambda's writable /tmp directory
    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1], dir='/tmp') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Calculate file hash
        file_hash = calculate_file_hash(tmp_path)
        if not file_hash:
            raise ValueError("Failed to calculate file hash")
        
        # Check if document already exists in database
        db = Database()
        existing_doc = db.get_document_by_hash(file_hash)
        
        if existing_doc:
            # Document already processed, create a new task linked to the existing document
            logger.info(f"Document with hash {file_hash} already exists, creating task with existing document ID")
            
            # Create a new task with the existing document ID
            task_id = task_manager.create_task(document_id=existing_doc["id"])
            
            # Update task status to completed since the document is already processed
            task_manager.update_task_status(task_id, TaskStatus.COMPLETED, document_id=existing_doc["id"])
            
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
            return {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED,
                "message": "Document already processed"
            }
        
        # Upload file to S3
        storage = S3Storage()
        s3_key = f"documents/{file_hash}{os.path.splitext(file.filename)[1]}"
        
        if not storage.upload_file(tmp_path, s3_key):
            raise Exception(f"Failed to upload file to S3")
        
        # Clean up temp file after upload
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Create a new task
        task_id = task_manager.create_task()
        
        # Invoke Lambda function asynchronously (self-invocation)
        import boto3
        import json
        
        lambda_client = boto3.client('lambda')
        
        # Get current Lambda function name from environment
        function_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
        
        # Prepare payload for internal endpoint - API Gateway v2 format
        payload = {
            "version": "2.0",
            "routeKey": "POST /internal/process-document",
            "rawPath": "/internal/process-document",
            "rawQueryString": "",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": os.environ.get('API_KEY')  # Pass API key for authentication
            },
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": "/internal/process-document",
                    "sourceIp": "127.0.0.1",
                    "userAgent": "boto3/lambda"
                }
            },
            "body": json.dumps({
                "s3_key": s3_key,
                "file_hash": file_hash,
                "original_filename": file.filename,
                "task_id": task_id
            }),
            "isBase64Encoded": False
        }
        
        # Invoke Lambda asynchronously
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps(payload)
        )
        
        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "message": "Document processing started"
        }
    except Exception as e:
        # Clean up on error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"Error starting document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting document processing: {str(e)}")

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a task"""
    task_data = task_manager.get_task_status(task_id)
    
    if not task_data:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    response = {
        "task_id": task_data["task_id"],
        "status": task_data["status"],
        "created_at": task_data["created_at"],
        "updated_at": task_data["updated_at"],
        "error": task_data.get("error")
    }
    
    # Include document details if task is completed and has associated document
    if task_data["status"] == TaskStatus.COMPLETED and task_data.get("document_id"):
        response.update({
            "document_id": task_data["document_id"],
            "extracted_data": task_data.get("extracted_data"),
            "validation_status": task_data.get("validation_status"),
            "s3_key": task_data.get("s3_key")
        })
    
    return response

@app.get("/api/welcome")
async def welcome() -> Dict[str, Any]:
    return {
        "message": "Welcome to AI Doc Parser API",
        "status": "active",
        "version": "1.0.1"
    }

@app.post("/internal/process-document", include_in_schema=False)
async def internal_process_document(request: InternalProcessRequest = Body(...)) -> Dict[str, Any]:
    """Internal endpoint for processing documents from S3"""
    tmp_path = None
    try:
        # Process document from S3
        processor = DocumentProcessor()
        logger.info(f"Processing document from S3: {request.s3_key}")
        
        # Download file from S3 to temp location
        storage = S3Storage()
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(request.original_filename)[1], dir='/tmp') as tmp:
            tmp_path = tmp.name
        
        if not storage.download_file(request.s3_key, tmp_path):
            raise Exception(f"Failed to download file from S3: {request.s3_key}")
        
        # Update task status to processing
        task_manager.update_task_status(request.task_id, TaskStatus.PROCESSING)
        
        # Process the document
        result = processor.process_document(tmp_path)
        
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Store result in database
        db = Database()
        file_size = 0
        if os.path.exists(tmp_path):
            file_size = os.path.getsize(tmp_path)
            
        document_id = db.save_document(
            file_hash=request.file_hash,
            file_name=request.original_filename,
            file_size=file_size,
            s3_key=request.s3_key,
            extracted_data=result.get("extracted_data", {}),
            validation_status=result.get("validation_status", {})
        )
        
        # Update task status to completed with document_id
        task_manager.update_task_status(request.task_id, TaskStatus.COMPLETED, document_id=document_id)
        
        return result
    except Exception as e:
        # Clean up on error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"Error processing document: {str(e)}")
        
        # Update task status to failed
        task_manager.update_task_status(request.task_id, TaskStatus.FAILED, error=str(e))
        
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/process-pbm-document")
async def process_pbm_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Process PBM contract documents and extract pharmacy benefits management information"""
    # Create temporary file in Lambda's writable /tmp directory
    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1], dir='/tmp') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Calculate file hash
        file_hash = calculate_file_hash(tmp_path)
        if not file_hash:
            raise ValueError("Failed to calculate file hash")
        
        # Check if document already exists in database
        db = Database()
        existing_doc = db.get_document_by_hash(file_hash)
        
        if existing_doc:
            # Document already processed, create a new task linked to the existing document
            logger.info(f"PBM Document with hash {file_hash} already exists, creating task with existing document ID")
            
            # Create a new task with the existing document ID
            task_id = task_manager.create_task(document_id=existing_doc["id"])
            
            # Update task status to completed since the document is already processed
            task_manager.update_task_status(task_id, TaskStatus.COMPLETED, document_id=existing_doc["id"])
            
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
            return {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED,
                "message": "PBM document already processed",
                "document_type": "pbm_contract"
            }
        
        # Upload file to S3
        storage = S3Storage()
        s3_key = f"pbm_documents/{file_hash}{os.path.splitext(file.filename)[1]}"
        
        if not storage.upload_file(tmp_path, s3_key):
            raise Exception(f"Failed to upload PBM file to S3")
        
        # Clean up temp file after upload
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Create a new task
        task_id = task_manager.create_task()
        
        # Invoke Lambda function asynchronously (self-invocation)
        import boto3
        import json
        
        lambda_client = boto3.client('lambda')
        
        # Get current Lambda function name from environment
        function_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
        
        # Prepare payload for internal PBM endpoint - API Gateway v2 format
        payload = {
            "version": "2.0",
            "routeKey": "POST /internal/process-pbm-document",
            "rawPath": "/internal/process-pbm-document",
            "rawQueryString": "",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": os.environ.get('API_KEY')  # Pass API key for authentication
            },
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": "/internal/process-pbm-document",
                    "sourceIp": "127.0.0.1",
                    "userAgent": "boto3/lambda"
                }
            },
            "body": json.dumps({
                "s3_key": s3_key,
                "file_hash": file_hash,
                "original_filename": file.filename,
                "task_id": task_id
            }),
            "isBase64Encoded": False
        }
        
        # Invoke Lambda asynchronously
        lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',  # Asynchronous invocation
            Payload=json.dumps(payload)
        )
        
        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "message": "PBM document processing started",
            "document_type": "pbm_contract"
        }
    except Exception as e:
        # Clean up on error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"Error starting PBM document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting PBM document processing: {str(e)}")

@app.post("/internal/process-pbm-document", include_in_schema=False)
async def internal_process_pbm_document(request: InternalProcessPBMRequest = Body(...)) -> Dict[str, Any]:
    """Internal endpoint for processing PBM documents from S3"""
    tmp_path = None
    try:
        # Process PBM document from S3
        processor = PBMDocumentProcessor()
        logger.info(f"Processing PBM document from S3: {request.s3_key}")
        
        # Download file from S3 to temp location
        storage = S3Storage()
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(request.original_filename)[1], dir='/tmp') as tmp:
            tmp_path = tmp.name
        
        if not storage.download_file(request.s3_key, tmp_path):
            raise Exception(f"Failed to download PBM file from S3: {request.s3_key}")
        
        # Update task status to processing
        task_manager.update_task_status(request.task_id, TaskStatus.PROCESSING)
        
        # Process the PBM document
        result = processor.process_document(tmp_path)
        
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Store result in database
        db = Database()
        file_size = 0
        if os.path.exists(tmp_path):
            file_size = os.path.getsize(tmp_path)
            
        document_id = db.save_document(
            file_hash=request.file_hash,
            file_name=request.original_filename,
            file_size=file_size,
            s3_key=request.s3_key,
            extracted_data=result.get("extracted_data", {}),
            validation_status=result.get("validation_status", {})
        )
        
        # Update task status to completed with document_id
        task_manager.update_task_status(request.task_id, TaskStatus.COMPLETED, document_id=document_id)
        
        return result
    except Exception as e:
        # Clean up on error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"Error processing PBM document: {str(e)}")
        
        # Update task status to failed
        task_manager.update_task_status(request.task_id, TaskStatus.FAILED, error=str(e))
        
        raise HTTPException(status_code=500, detail=f"Error processing PBM document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)