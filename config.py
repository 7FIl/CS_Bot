import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID', 0))
PREFIX = os.getenv('PREFIX', '!')

# Google Sheets Configuration
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')

# Channel Configuration
SUPPORT_CHANNEL_ID = int(os.getenv('SUPPORT_CHANNEL_ID', 0))
STAFF_NOTIFICATION_CHANNEL_ID = int(os.getenv('STAFF_NOTIFICATION_CHANNEL_ID', 0))
LOGS_CHANNEL_ID = int(os.getenv('LOGS_CHANNEL_ID', 0))

# Spreadsheet Tab Names
FAQ_TAB_NAME = os.getenv('FAQ_TAB_NAME', 'FAQ')
LEADS_TAB_NAME = os.getenv('LEADS_TAB_NAME', 'Leads')
ANALYTICS_TAB_NAME = os.getenv('ANALYTICS_TAB_NAME', 'Analytics')

# Bot Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
