import httpx
import asyncio
from typing import Dict, Any, Optional
from app.core.logger import logger
import json
from datetime import datetime

def serialize_datetimes(obj):
    if isinstance(obj, dict):
        return {k: serialize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetimes(v) for v in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

class CallbackService:
    """Service for handling HTTP callbacks when tasks complete"""
    
    def __init__(self):
        self.timeout = 30.0  # 30 second timeout
        
    async def send_callback(self, callback_url: str, payload: Dict[str, Any]) -> bool:
        """Send HTTP POST callback with task result"""
        if not callback_url or not callback_url.strip():
            logger.debug("No callback URL provided, skipping callback")
            return True
            
        try:
            logger.info(f"Sending callback to: {callback_url}")
            logger.debug(f"Callback payload: {json.dumps(payload, indent=2, default=str)}")
            
            payload = serialize_datetimes(payload)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    callback_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "AI-API-Parser/1.0"
                    }
                )
                
                logger.info(f"Callback response: {response.status_code}")
                
                # Consider 2xx status codes as successful
                if 200 <= response.status_code < 300:
                    logger.info(f"Callback sent successfully to {callback_url}")
                    return True
                else:
                    logger.warning(f"Callback failed with status {response.status_code}: {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Callback timeout to {callback_url}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Callback request error to {callback_url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending callback to {callback_url}: {str(e)}")
            return False
    
    def send_callback_sync(self, callback_url: str, payload: Dict[str, Any]) -> bool:
        """Synchronous wrapper for sending callbacks"""
        try:
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                # We're in an event loop (e.g., FastAPI, Lambda)
                asyncio.create_task(self.send_callback(callback_url, payload))
                return True  # Can't get result synchronously, but task is scheduled
            else:
                # No event loop, safe to run synchronously
                return asyncio.run(self.send_callback(callback_url, payload))
        except Exception as e:
            logger.error(f"Error in sync callback wrapper: {str(e)}")
            return False 