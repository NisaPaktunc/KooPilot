import os
from dotenv import load_dotenv
load_dotenv(override=True)

from integrations.whatsapp import send_whatsapp_message
import logging

logging.basicConfig(level=logging.INFO)

success = send_whatsapp_message("whatsapp:+905458107959", "Test message from script")
print(f"Sent: {success}")
