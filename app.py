import sys
import os
import time
import threading
import queue
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from pytubefix import YouTube
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y CARPETAS
# ==========================================

if getattr(sys, 'frozen', False):
    INTERNAL_PATH = sys._MEIPASS 
    EXTERNAL_PATH = os.path.dirname(sys.executable)
else:
    INTERNAL_PATH = os.path.dirname(os.path.abspath(__file__))
    EXTERNAL_PATH = INTERNAL_PATH

FILES_DIR = os.path.join(EXTERNAL_PATH, "files")
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR, exist_ok=True)

ICON_FILE = "youtube_icon.png"
ICON_PATH = os.path.join(INTERNAL_PATH, ICON_FILE)
FFMPEG_BINARY = 'ffmpeg_audio.exe' 
FFMPEG_PATH = os.path.join(INTERNAL_PATH, FFMPEG_BINARY)
OUTPUT_AUDIO = os.path.join(FILES_DIR, "mp3")
OUTPUT_VIDEO = os.path.join(FILES_DIR, "mp4")
LOG_FILE = os.path.join(FILES_DIR, "history_log.txt")

# ==========================================
# 2. VARIABLES GLOBALES
# ==========================================
task_queue = queue.Queue()
gui_queue = queue.Queue()
file_lock = threading.Lock()

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

safe_log_to_file("=== Server Iniciado ===")

# ==========================================
# 3. LÓGICA DEL WORKER
# ==========================================
def worker_logic():
    if not os.path.exists(FFMPEG_PATH):
        gui_queue.put(f"ERROR: No se encuentra {FFMPEG_BINARY} en:\n{FFMPEG_PATH}")
    else:
        gui_queue.put(f"Sistema listo. Guardando en: files/\nHecho por Fernando Rivas." )

    while True:
        try:
            task = task_queue.get()
            start_time = time.time()
            url, c_type, metadata = task
            
            gui_queue.put(f"Procesando: {url}...")

            try:
                yt = YouTube(url)
                raw_title = yt.title
                safe_title = sanitize_filename(raw_title)
            except Exception as e:
                raise Exception(f"Error obteniendo info video: {e}")
            
            if c_type == "audio":
                folder = OUTPUT_AUDIO
                stream = yt.streams.get_audio_only()
            else:
                folder = OUTPUT_VIDEO
                stream = yt.streams.get_highest_resolution()

            if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
            gui_queue.put(f"Descargando: {safe_title}")
            file_path = stream.download(output_path=folder, filename=f"{safe_title}.{stream.subtype}")

            if c_type == "audio":
                base, _ = os.path.splitext(file_path)
                mp3_path = base + ".mp3"
                
                f_title = metadata[0] if metadata and metadata[0] else raw_title
                f_artist = metadata[1] if metadata and metadata[1] else yt.author
                f_album = metadata[2] if metadata and metadata[2] else ""

                cmd = [
                    FFMPEG_PATH, '-y', '-i', file_path, '-map', '0:a',
                    '-c:a', 'libmp3lame', '-q:a', '0',
                    '-metadata', f"title={f_title}",
                    '-metadata', f"artist={f_artist}",
                    '-metadata', f"album={f_album}",
                    mp3_path
                ]
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                gui_queue.put(f"Convirtiendo a MP3...")

                result = subprocess.run(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True, 
                    startupinfo=startupinfo,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg falló: {result.stderr[-300:]}")

                if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 100:
                    raise Exception("FFmpeg terminó pero no creó el archivo MP3 válido.")

                if os.path.exists(file_path): 
                    try:
                        os.remove(file_path)
                    except:
                        pass

            duration = round(time.time() - start_time, 2)
            msg_final = f"Completado ({duration}s): {safe_title}"            
            gui_queue.put(msg_final)
            
            # --- CORRECCIÓN DE LA LÍNEA DE SEPARACIÓN ---
            gui_queue.put(f"\n{'-' * 62}") 

            safe_log_to_file(f"Tiempo: {duration}s | {safe_title}")
            task_queue.task_done()

        except Exception as e:
            err_msg = f"ERROR: {str(e)}"
            gui_queue.put(err_msg)
            safe_log_to_file(f"ERROR: {err_msg}")
            if 'task' in locals(): task_queue.task_done()

# ==========================================
# 4. SERVIDOR FLASK
# ==========================================
app = Flask(__name__)
CORS(app)

@app.route('/download_audio', methods=['POST'])
def route_audio():
    data = request.json
    if data and 'url' in data:
        meta = [data.get('title',''), data.get('artist',''), data.get('album',''), data.get('art_url','')]
        task_queue.put((clean_url(data['url']), "audio", meta))
        return jsonify({"status": "queued", "msg": "Audio en cola"})
    return jsonify({"error": "No data"}), 400

@app.route('/download_video', methods=['POST'])
def route_video():
    data = request.json
    if data and 'url' in data:
        task_queue.put((clean_url(data['url']), "video", None))
        return jsonify({"status": "queued", "msg": "Video en cola"})
    return jsonify({"error": "No data"}), 400

# ==========================================
# 5. INTERFAZ GRÁFICA
# ==========================================
class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(100)

    def init_ui(self):
        self.setWindowTitle("Servidor Descargador de Youtube")
        self.setFixedSize(600, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) 
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()
        lbl_title = QLabel("Servidor Activo")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(lbl_title)

        if os.path.exists(ICON_PATH):
            try:
                app_icon = QIcon(ICON_PATH)
                self.setWindowIcon(app_icon)
                print("Icono cargado con éxito.")
            except Exception as e:
                print(f"Error de carga: No se pudo establecer el icono '{ICON_FILE}'. Detalles: {e}")


        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10pt;")
        layout.addWidget(self.txt_log)
        
        buttons_layout = QHBoxLayout()

        btn_clear = QPushButton("Limpiar pantalla")
        btn_clear.setStyleSheet("background-color: orange; color: white; padding: 10px; font-weight: bold;")
        btn_clear.clicked.connect(self.clear_log)
        buttons_layout.addWidget(btn_clear)

        btn_close = QPushButton("Cerrar")
        btn_close.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; font-weight: bold;")
        btn_close.clicked.connect(self.close_app)
        buttons_layout.addWidget(btn_close)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def check_queue(self):
        try:
            while True:
                msg = gui_queue.get_nowait()
                self.txt_log.append(msg)
                sb = self.txt_log.verticalScrollBar()
                sb.setValue(sb.maximum())
        except queue.Empty:
            pass

    def clear_log(self):
        self.txt_log.clear()

    def close_app(self):
        self.close()

# ==========================================
# 6. INNIT DEL PROGRAMA
# ==========================================
if __name__ == '__main__':
    t_worker = threading.Thread(target=worker_logic, daemon=True)
    t_worker.start()
    t_server = threading.Thread(target=lambda: serve(app, host='127.0.0.1', port=5000), daemon=True)
    t_server.start()
    qt_app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    sys.exit(qt_app.exec_())