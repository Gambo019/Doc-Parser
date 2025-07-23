# Local Development with Docker Compose

This guide explains how to run the Document Processing Engine locally using Docker Compose with MinIO (S3-compatible storage) instead of AWS S3.

## Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd document-processing-engine
```

2. **Environment Configuration:**
The `.env` file will be automatically created when you run `./start-local.sh`. 
You can also create it manually using this template:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# API Authentication (change this to a secure random string)
API_KEY=your-secure-api-key-here

# Database Configuration (using default PostgreSQL port)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=docparser
DB_USER=docparser
DB_PASSWORD=docparser123

# Storage Configuration (S3-compatible - MinIO for local development)
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin123
S3_BUCKET_NAME=documents
S3_REGION=us-east-1

# Local Development Flags
RUNNING_IN_LAMBDA=false
USE_LOCAL_STORAGE=true

# Docker Compose Configuration (these are used by docker-compose.yml, not the app)
APP_PORT=8000
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
```

**Note:** All configuration is now centralized in the `.env` file. The startup script will create this file automatically if it doesn't exist.

3. **Start the services:**
```bash
# Using the startup script (recommended)
./start-local.sh

# Or manually with Docker Compose
docker compose up -d
# (use 'docker-compose' if you have the older version)
```

4. **Access the application:**
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (login: minioadmin/minioadmin123)
- **Database**: localhost:5432

## Services

### MinIO (Object Storage)
- **Purpose**: S3-compatible object storage for document files
- **Console**: http://localhost:9001
- **API**: http://localhost:9000
- **Credentials**: minioadmin / minioadmin123
- **Bucket**: `documents` (auto-created)

### PostgreSQL (Database)
- **Purpose**: Stores task status, document metadata, and extracted data
- **Host**: localhost:5432
- **Database**: docparser
- **Credentials**: docparser / docparser123

### Document Processing App
- **Purpose**: Main FastAPI application
- **Port**: 8000
- **Auto-reload**: Enabled for development
- **Volume mounted**: Current directory is mounted for live code changes

## API Usage

The local deployment works exactly like the AWS version, but uses MinIO for storage:

### Process Document
```bash
curl -X POST "http://localhost:8000/api/process-document" \
  -F "file=@document.pdf" \
  -F "callback_url=http://your-app.com/webhook"
```

### Get Task Status
```bash
curl -X GET "http://localhost:8000/api/task/{task_id}"
```

### Process PBM Document
```bash
curl -X POST "http://localhost:8000/api/process-pbm-document" \
  -F "file=@pbm_contract.pdf" \
  -F "callback_url=http://your-app.com/webhook"
```

## File Storage

Files are stored in MinIO with the following structure:
- Regular documents: `documents/{file_hash}.{extension}`
- PBM documents: `pbm_documents/{file_hash}.{extension}`

Access URLs in responses will use MinIO format:
- `http://localhost:9000/documents/{file_hash}.pdf`

## Development

### Live Code Changes
The application container mounts the current directory, so code changes are automatically reflected without rebuilding:

```bash
# Edit any Python file
# Changes are automatically reloaded in the container
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f postgres
docker compose logs -f minio
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart app
```

## Database Management

### Connect to PostgreSQL
```bash
# Using docker
docker compose exec postgres psql -U docparser -d docparser

# Using local client
psql -h localhost -p 5432 -U docparser -d docparser
```

### View Tables
```sql
-- List all tables
\dt

-- View documents
SELECT * FROM documents LIMIT 10;

-- View tasks
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10;
```

## MinIO Management

### Access MinIO Console
1. Go to http://localhost:9001
2. Login with: minioadmin / minioadmin123
3. Browse the `documents` bucket

### MinIO CLI (mc)
```bash
# Configure MinIO client
docker run --rm -it --network doc-parser-network minio/mc:latest \
  mc config host add local http://minio:9000 minioadmin minioadmin123

# List buckets
docker run --rm -it --network doc-parser-network minio/mc:latest \
  mc ls local

# List files in documents bucket
docker run --rm -it --network doc-parser-network minio/mc:latest \
  mc ls local/documents
```

## Troubleshooting

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
services:
  app:
    ports:
      - "8001:8000"  # Change 8000 to 8001
  postgres:
    ports:
      - "5432:5432"  # Change 5432 to 5432
  minio:
    ports:
      - "9002:9000"  # Change 9000 to 9002
      - "9003:9001"  # Change 9001 to 9003
```

### Database Connection Issues
```bash
# Check if PostgreSQL is ready
docker compose exec postgres pg_isready -U docparser

# Reset database
docker compose down
docker volume rm doc-parser_postgres_data
docker compose up -d
```

### MinIO Connection Issues
```bash
# Check MinIO health
curl http://localhost:9000/minio/health/live

# Reset MinIO data
docker compose down
docker volume rm doc-parser_minio_data
docker compose up -d
```

### App Startup Issues
```bash
# Check app logs
docker compose logs app

# Rebuild app container
docker compose build app
docker compose up -d app
```

## Cleanup

### Stop Services
```bash
docker compose down
```

### Complete Cleanup
```bash
# Interactive cleanup script (recommended)
./cleanup.sh

# Manual cleanup (removes everything)
docker compose down -v
docker system prune -f
```

## Production Considerations

This local setup is for development only. For production:

1. **Security**: Change default passwords and credentials
2. **Persistence**: Use named volumes or host mounts for data persistence
3. **Networking**: Configure proper network security
4. **SSL**: Add SSL/TLS certificates for HTTPS
5. **Monitoring**: Add monitoring and logging solutions
6. **Backup**: Implement backup strategies for PostgreSQL and MinIO data

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for document processing | - | Yes |
| `API_KEY` | Internal API authentication key | - | Yes |
| `DB_HOST` | PostgreSQL host | localhost | Yes |
| `DB_PORT` | PostgreSQL port | 5432 | Yes |
| `DB_NAME` | PostgreSQL database name | docparser | Yes |
| `DB_USER` | PostgreSQL username | docparser | Yes |
| `DB_PASSWORD` | PostgreSQL password | docparser123 | Yes |
| `S3_ENDPOINT_URL` | MinIO endpoint URL | http://localhost:9000 | Yes |
| `S3_ACCESS_KEY_ID` | MinIO access key | minioadmin | Yes |
| `S3_SECRET_ACCESS_KEY` | MinIO secret key | minioadmin123 | Yes |
| `S3_BUCKET_NAME` | Storage bucket name | documents | Yes |
| `S3_REGION` | S3/MinIO region | us-east-1 | Yes |
| `RUNNING_IN_LAMBDA` | Lambda execution flag | false | No |
| `USE_LOCAL_STORAGE` | Local storage flag | true | No | 