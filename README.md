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
- **Callback mechanism for automatic result notifications**
- Asynchronous task processing with status tracking

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

## Running the Application

Start the server locally:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Process Document

**Endpoint:** `POST /api/process-document`

Processes a document and extracts structured information. Supports both callback notifications and polling approaches.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body parameters:
  - `file` (required): Document file to process
  - `callback_url` (optional): URL to receive processing results via HTTP POST

### Process PBM Document

**Endpoint:** `POST /api/process-pbm-document`

Processes PBM (Pharmacy Benefits Management) contract documents with specialized extraction.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body parameters:
  - `file` (required): PBM contract document file
  - `callback_url` (optional): URL to receive processing results via HTTP POST

### Get Task Status

**Endpoint:** `GET /api/task/{task_id}`

Retrieves the current status of a processing task.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "pending|processing|completed|failed",
  "created_at": "2025-07-02T12:28:29.547060",
  "updated_at": "2025-07-02T12:29:19.872379",
  "error": null,
  "document_id": 1,
  "extracted_data": {...},
  "validation_status": {...},
  "s3_key": "documents/..."
}
```

## Processing Approaches

### 1. Callback Approach (Recommended)

**Benefits:**
- No need for consistent polling
- Immediate notification when processing completes
- Reduces API calls and server load
- More efficient for real-time applications

**Example using curl:**
```bash
curl -X POST "https://your-api.com/api/process-document" \
  -F "file=@document.pdf" \
  -F "callback_url=https://your-app.com/webhook"
```

**Example using Python:**
```python
import requests

url = "https://your-api.com/api/process-document"
callback_url = "https://your-app.com/webhook"

with open("document.pdf", "rb") as file:
    files = {"file": ("document.pdf", file, "application/pdf")}
    data = {"callback_url": callback_url}
    response = requests.post(url, files=files, data=data)

task_data = response.json()
print(f"Task ID: {task_data['task_id']}")
print("Processing started - results will be sent to callback URL")
```

**Callback Payload:**
When processing completes successfully, your callback URL will receive a POST request with the extracted data directly:
```json
{
  "CustomerName": "Acme Corporation",
  "AccountId": "AC123456789",
  "Quote": "Q-2025-07-03-001",
  "CommitmentTerms": "12 months fixed",
  "BuyingProgram": "Enterprise Plan",
  "CommitmentFee": 15000.00,
  "SavingsPlanCredit": 2000.00,
  "NetPayableFee": 13000.00,
  "ContactName": "John Doe",
  "TermStartDate": "2025-07-01T00:00:00Z",
  "RenewalDate": "2026-07-01T00:00:00Z",
  "BillingTerms": "Net 30",
  "PaymentTerms": "Credit Card",
  "PaymentMethod": "Visa",
  "VatId": "VAT123456789",
  "PurchaseOrderNumber": "PO-987654321",
  "CompanyAddress1": "123 Main St.",
  "CompanyAddress2": "Suite 400",
  "City": "Metropolis",
  "State": "NY",
  "ZipCode": "10101",
  "Country": "USA",
  "EmailInvoiceTo": "billing@acme.com",
  "CustomerTitle": "Mr.",
  "DateSigned": "2025-06-30T15:30:00Z",
  "Filename": "contract_document.pdf",
  "S3FilePath": "https://your-bucket.s3.us-east-1.amazonaws.com/documents/abc123.pdf"
}
```

**For failed processing**, the callback will receive:
```json
{
  "error": "Error description",
  "status": "failed"
}
```

### 2. Polling Approach (Legacy)

**For cases where callbacks are not available:**

```python
import requests
import time

# 1. Submit document for processing
url = "https://your-api.com/api/process-document"
with open("document.pdf", "rb") as file:
    files = {"file": ("document.pdf", file, "application/pdf")}
    response = requests.post(url, files=files)

task_id = response.json()["task_id"]

# 2. Poll for completion
while True:
    status_response = requests.get(f"https://your-api.com/api/task/{task_id}")
    status_data = status_response.json()
    
    if status_data["status"] == "completed":
        print("Processing completed!")
        print(status_data["extracted_data"])
        break
    elif status_data["status"] == "failed":
        print(f"Processing failed: {status_data['error']}")
        break
    else:
        print(f"Status: {status_data['status']}")
        time.sleep(5)  # Wait 5 seconds before next check
```

## Examples

### PBM Document Processing with Callback

```python
import requests

url = "https://your-api.com/api/process-pbm-document"
callback_url = "https://your-app.com/pbm-webhook"

with open("pbm_contract.pdf", "rb") as file:
    files = {"file": ("pbm_contract.pdf", file, "application/pdf")}
    data = {"callback_url": callback_url}
    response = requests.post(url, files=files, data=data)

print(f"PBM processing started: {response.json()}")
```

### Setting up a Callback Endpoint

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def process_callback(request: Request):
    """Handle document processing results"""
    result = await request.json()
    
    # Check if it's an error response
    if "error" in result and result.get("status") == "failed":
        print(f"Processing failed: {result['error']}")
        return {"received": True}
    
    # Handle successful extraction - data comes directly
    customer_name = result.get("CustomerName")
    account_id = result.get("AccountId")
    filename = result.get("Filename")
    s3_path = result.get("S3FilePath")
    
    print(f"Document processed successfully!")
    print(f"Customer: {customer_name}")
    print(f"Account: {account_id}")
    print(f"File: {filename}")
    print(f"S3 Path: {s3_path}")
    
    # Process your extracted data here
    # ...
    
    return {"received": True}
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

Callback notifications are sent for both successful and failed processing attempts.

## Development

The project structure:
```
.
├── app/
│ ├── core/
│ │ ├── task_manager.py    # Async task management
│ │ └── database.py        # Database operations
│ ├── models/
│ ├── services/
│ │ ├── callback_service.py # HTTP callback handling
│ │ └── document_processor.py
│ └── ...
├── main.py               # FastAPI application and routes
├── requirements.txt
├── lambda_handler.py
├── deploy.sh
└── README.md
```

Key components:
- `main.py`: FastAPI application and routes with callback support
- `app/services/`: Document processing and callback logic
- `app/models/`: Data models and schemas
- `app/core/`: Core configurations, task management, and database utilities