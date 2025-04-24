import os
from dotenv import load_dotenv

load_dotenv()

CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_SWAGGER_PORT = 3000

LOG_FORMAT = '%(message)s'
API_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

MAX_CONNECTIONS = 10

API_TITLE = "ClickUp Webhook Manager"
API_DESCRIPTION = "API for managing ClickUp webhooks"
API_VERSION = "1.0.0"