import sys
import os
import queue
import threading

if getattr(sys, 'frozen', False):
    INTERNAL_PATH = sys._MEIPASS 
    EXTERNAL_PATH = os.path.dirname(sys.executable)
else:
    INTERNAL_PATH = os.path.dirname(os.path.abspath(__file__))
    EXTERNAL_PATH = INTERNAL_PATH

FILES_DIR = os.path.join(EXTERNAL_PATH, "..", "files") 
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR, exist_ok=True)

ICON_PATH = os.path.join(INTERNAL_PATH, "..", "assets", "youtube_icon.png")
QSS_PATH = os.path.join(INTERNAL_PATH, "..", "..", "assets", "styles.css")
FFMPEG_PATH = os.path.join(INTERNAL_PATH,"..", "bin", "ffmpeg_audio.exe") 
LOG_FILE = os.path.join(FILES_DIR, "history_log.txt")
OUTPUT_AUDIO = os.path.join(FILES_DIR, "mp3")
OUTPUT_VIDEO = os.path.join(FILES_DIR, "mp4")

task_queue = queue.Queue()
gui_queue = queue.Queue()
file_lock = threading.Lock()