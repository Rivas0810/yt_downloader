import re
import time
from config import LOG_FILE, file_lock

def clean_url(url):
    patron = r'[?&]v=([^&]+)'
    match = re.search(patron, url)
    return f"https://www.youtube.com/watch?v={match.group(1)}" if match else url

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def safe_log_to_file(msg):
    try:
        with file_lock:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{time.ctime()} - {msg}\n")
    except Exception as e:
        print(f"Error escribiendo log: {e}")