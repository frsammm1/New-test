import os
import logging

# --- TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION") 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

# --- OPTIMIZED SETTINGS FOR RENDER FREE TIER ---
# Reduced from 32MB to 8MB chunks (better for 512MB RAM limit)
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks
QUEUE_SIZE = 10  # 80MB buffer (8MB × 2) - Much safer for free tier
UPLOAD_PART_SIZE = 8192  # 8MB upload parts (was 32MB)
UPDATE_INTERVAL = 5  # Progress update interval (seconds)
MAX_RETRIES = 3  # Retry attempts per file (reduced from 4)
FLOOD_SLEEP_THRESHOLD = 120
REQUEST_RETRIES = 10  # Reduced from 20

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- RUNTIME STATE ---
pending_requests = {}
active_sessions = {}
is_running = False
status_message = None
last_update_time = 0
current_task = None
stop_flag = False  # NEW: Global stop flag
