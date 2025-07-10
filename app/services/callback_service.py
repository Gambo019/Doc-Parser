import requests
from typing import Dict, Any
from app.core.logger import logger
from app.core.config import settings
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
    """Service for handling HTTP callbacks when tasks complete (synchronous version)"""

    def __init__(self):
        self.timeout = 30.0  # seconds

    def send_callback(self, callback_url: str, payload: Dict[str, Any]) -> bool:
        if not callback_url or not callback_url.strip():
            logger.debug("No callback URL provided, skipping callback")
            return True

        try:
            logger.info(f"Sending callback to: {callback_url}")
            payload = serialize_datetimes(payload)
            response = requests.post(
                callback_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "AI-API-Parser/1.0",
                    "apiKey": settings.API_KEY
                },
                timeout=self.timeout
            )
            logger.info(f"Callback response: {response.status_code}")
            if 200 <= response.status_code < 300:
                logger.info(f"Callback sent successfully to {callback_url}")
                return True
            else:
                logger.warning(f"Callback failed with status {response.status_code}: {response.text}")
                return False
        except requests.Timeout:
            logger.error(f"Callback timeout to {callback_url}")
            return False
        except requests.RequestException as e:
            logger.error(f"Callback request error to {callback_url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending callback to {callback_url}: {str(e)}")
            return False 