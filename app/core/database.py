import psycopg2
from psycopg2.extras import RealDictCursor, Json
from app.core.config import settings
from app.core.logger import logger
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            self.create_tables()
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            # Don't raise the exception, just log it
            # This allows the application to continue even if DB connection fails
            self.conn = None
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.conn:
            return
            
        try:
            with self.conn.cursor() as cursor:
                # Create documents table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    file_hash VARCHAR(64) UNIQUE NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size BIGINT NOT NULL,
                    s3_key VARCHAR(255),
                    extracted_data JSONB,
                    validation_status JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Create tasks table with callback_url field
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id VARCHAR(36) PRIMARY KEY,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    document_id INTEGER REFERENCES documents(id),
                    error TEXT,
                    callback_url TEXT
                )
                """)
                
                # Add callback_url column if it doesn't exist (for existing installations)
                cursor.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='tasks' AND column_name='callback_url') THEN
                        ALTER TABLE tasks ADD COLUMN callback_url TEXT;
                    END IF;
                END $$;
                """)
                
                self.conn.commit()
                logger.info("Database tables created or already exist")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            # Don't raise the exception, just log it
            # This allows the application to continue even if table creation fails
            
    def get_document_by_hash(self, file_hash):
        """Get document by file hash"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM documents WHERE file_hash = %s",
                    (file_hash,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching document: {str(e)}")
            return None
            
    def save_document(self, file_hash, file_name, file_size, s3_key, extracted_data, validation_status):
        """Save document to database"""
        try:
            # Convert data to JSON strings with custom encoder for datetime objects
            extracted_data_json = json.dumps(extracted_data, cls=DateTimeEncoder)
            validation_status_json = json.dumps(validation_status, cls=DateTimeEncoder)
            
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO documents 
                    (file_hash, file_name, file_size, s3_key, extracted_data, validation_status)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb)
                    ON CONFLICT (file_hash) 
                    DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                    """,
                    (file_hash, file_name, file_size, s3_key, 
                     extracted_data_json, 
                     validation_status_json)
                )
                document_id = cursor.fetchone()[0]
                self.conn.commit()
                return document_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving document: {str(e)}")
            # Return None instead of raising an exception
            return None
    
    def save_task(self, task_data):
        """Save task to database"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks 
                    (task_id, status, created_at, updated_at, document_id, error, callback_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        task_data["task_id"],
                        task_data["status"],
                        task_data["created_at"],
                        task_data["updated_at"],
                        task_data.get("document_id"),
                        task_data.get("error"),
                        task_data.get("callback_url")
                    )
                )
                self.conn.commit()
                return task_data["task_id"]
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving task: {str(e)}")
            raise
    
    def update_task(self, task_id, task_data):
        """Update task in database"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks 
                    SET status = %s, updated_at = %s, document_id = %s, error = %s, callback_url = %s
                    WHERE task_id = %s
                    """,
                    (
                        task_data["status"],
                        task_data["updated_at"],
                        task_data.get("document_id"),
                        task_data.get("error"),
                        task_data.get("callback_url"),
                        task_id
                    )
                )
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating task: {str(e)}")
            raise
    
    def get_task(self, task_id):
        """Get task by ID"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM tasks WHERE task_id = %s",
                    (task_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching task: {str(e)}")
            return None
            
    def get_task_with_document(self, task_id):
        """Get task and associated document details"""
        logger.info(f"Getting task with document: {task_id}")
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        t.*,
                        d.extracted_data,
                        d.validation_status,
                        d.s3_key
                    FROM tasks t
                    LEFT JOIN documents d ON t.document_id = d.id
                    WHERE t.task_id = %s
                """, (task_id,))
                logger.debug(f"Executing query: {cursor.query.decode('utf-8')}")
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error fetching task with document: {str(e)}")
            return None
            
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close() 