import logging
import os


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s\n%(message)s' 
)

logger = logging.getLogger("ArchimedesApp")
