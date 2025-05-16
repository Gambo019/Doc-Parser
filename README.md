# Document Processing Engine

A FastAPI-based document processing engine that can extract structured information from various document types including PDF, Word, and Excel files.

## Features

- Support for multiple document formats:
  - PDF files (.pdf)
  - Word documents (.doc, .docx)
  - Excel spreadsheets (.xlsx, .xls)
  - CSV files (.csv)
- Automatic document type classification
- Structured information extraction using LLM
- Metadata extraction
- Full-text content extraction
- OCR support for scanned PDFs
- Data validation and business rules enforcement

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd document-processing-engine
```

2. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=<your-openai-api-key>
```

## AWS Lambda Deployment

1. Install Docker and AWS CLI

2. Configure AWS credentials:
```bash
aws configure
```

3. Update deploy.sh with your AWS details:
```bash
# Edit deploy.sh
AWS_ACCOUNT_ID="your-account-id"
AWS_REGION="your-region"
ECR_REPOSITORY="your-repo-name"
```

4. Run deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

5. Configure Lambda:
   - Create new Lambda function using the ECR image
   - Set memory to at least 4096 MB
   - Set timeout to at least 60 seconds
   - Configure environment variables (OPENAI_API_KEY)

## Testing Lambda Deployment

Save this code as `test_lambda.py`:
```python
import boto3
import json
import base64
import os
from urllib.parse import quote

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='your-region')  # Replace with your region

filename = "example.pdf"
file_path = os.path.join(os.path.dirname(__file__), filename)

# Read the file
with open(file_path, 'rb') as file:
    file_content = file.read()

# Create multipart form-data boundary
boundary = "boundary123"

# Create form-data content
form_data = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="{quote(filename)}"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + file_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')

# Base64 encode the form data
encoded_form_data = base64.b64encode(form_data).decode('utf-8')

# Prepare the payload to mimic API Gateway v2 event
payload = {
    "version": "2.0",
    "routeKey": "POST /api/process-document",
    "rawPath": "/api/process-document",
    "rawQueryString": "",
    "headers": {
        "content-type": f"multipart/form-data; boundary={boundary}"
    },
    "requestContext": {
        "http": {
            "method": "POST",
            "path": "/api/process-document",
            "sourceIp": "127.0.0.1",
            "userAgent": "boto3/lambda"
        }
    },
    "body": encoded_form_data,
    "isBase64Encoded": True
}

# Invoke Lambda function
response = lambda_client.invoke(
    FunctionName='your-lambda-function-name',  # Replace with your Lambda function name
    InvocationType='RequestResponse',
    Payload=json.dumps(payload)
)

# Parse and print the response
response_payload = json.loads(response['Payload'].read())
print(response_payload)
```

## Running the Application

Start the server locally:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Process Document

**Endpoint:** `POST /api/process-document`

Processes a document and extracts structured information.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body parameter: `file` (document file)

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/process-document \
-H "Content-Type: multipart/form-data" \
-F "file=@path/to/your/document.pdf"
```

**Example Response:**
```json
{
    "extracted_data": {
        "CustomerName": "Example Corp",
        "AccountID": "ACC123456",
        "Quote": "Q789",
        "CommitmentTerms": "12 months",
        "BuyingProgram": "Enterprise",
        "CommitmentFee": 5000.00,
        "SavingsPlanCredit": 500.00,
        "NetPayableFee": 4500.00,
        ...
    }
}
```

## Testing

To test the document processing:

1. Ensure the server is running
2. Use the sample files in the `sample` directory or your own documents
3. Send a POST request to the processing endpoint
4. Check the response for extracted information

Example using Python requests:
```python
import requests
url = "http://localhost:8000/api/process-document"
files = {"file": open("path/to/document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Supported Document Types

- PDF files (.pdf)
- Microsoft Word documents (.doc, .docx)
- Microsoft Excel spreadsheets (.xlsx, .xls)
- CSV files (.csv)

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Successful processing
- 400: Invalid request or file format
- 422: Validation error
- 500: Server error

Error responses include a message explaining the error.

## Development

The project structure:
```
.
├── app/
│ ├── core/
│ ├── models/
│ └── services/
├── main.py
├── requirements.txt
├── lambda_handler.py
├── deploy.sh
└── README.md
```

Key components:
- `main.py`: FastAPI application and routes
- `app/services/`: Document processing logic
- `app/models/`: Data models and schemas
- `app/core/`: Core configurations and utilities
- `lambda_handler.py`: AWS Lambda handler
- `deploy.sh`: Deployment script for AWS