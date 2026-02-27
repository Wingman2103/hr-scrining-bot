import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH")

ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x}
HOT_THRESHOLD = float(os.getenv("HOT_THRESHOLD", 8.0))