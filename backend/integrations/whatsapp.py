import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

def send_whatsapp_message(to_number: str, message: str) -> bool:
    """
    Sends a WhatsApp message using the Twilio REST API.
    
    Args:
        to_number: The recipient's phone number (must be in 'whatsapp:+...' format)
        message: The text message to send
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, from_number]):
        logger.error("Twilio credentials are not fully set in environment variables.")
        return False
        
    # Ensure recipient starts with 'whatsapp:'
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
        
    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        logger.info(f"WhatsApp message sent to {to_number}. SID: {msg.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Twilio error sending message to {to_number}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending message to {to_number}: {e}")
        return False
