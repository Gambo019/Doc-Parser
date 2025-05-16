from mangum import Mangum
from fastapi import HTTPException
from main import app
import json
from app.core.database import Database

def create_api_gateway_response(status_code: int, body: dict) -> dict:
    """Format response for API Gateway"""
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-API-Key",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        }
    }

# Use Mangum for the regular path
asgi_handler = Mangum(app, lifespan="off")

# Create a synchronous handler for AWS Lambda
def handler(event, context):
    """Lambda handler"""
    db = None
    try:
        # Check for API key in the event headers
        headers = event.get('headers', {}) or {}
        
        # Skip API key check for welcome endpoint
        if event.get('rawPath') == '/api/welcome':
            return asgi_handler(event, context)
            
        # Check for API key
        api_key = headers.get('X-API-Key') or headers.get('x-api-key')
        if not api_key:
            return create_api_gateway_response(
                status_code=401,
                body={"detail": "API Key missing"}
            )
        
        # Import settings here to avoid circular imports
        from app.core.config import settings
        if api_key != settings.API_KEY:
            return create_api_gateway_response(
                status_code=403, 
                body={"detail": "Invalid API Key"}
            )
            
        # Process with Mangum
        return asgi_handler(event, context)
        
    except HTTPException as exc:
        return create_api_gateway_response(
            status_code=exc.status_code,
            body={"detail": exc.detail}
        )
    except Exception as exc:
        import traceback
        print(f"Error: {str(exc)}")
        print(traceback.format_exc())
        return create_api_gateway_response(
            status_code=500,
            body={"detail": "Internal server error"}
        )
    finally:
        # Close database connection if it exists
        if db:
            db.close()