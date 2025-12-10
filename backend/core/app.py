import sys
import threading
from waitress import serve
from PyQt5.QtWidgets import QApplication

from utils import safe_log_to_file
from downloader import worker_logic
from server import app_flask
from gui import ServerGUI

def main():
    safe_log_to_file("=== Server Iniciado ===")
    t_worker = threading.Thread(target=worker_logic, daemon=True); t_worker.start()
    t_server = threading.Thread(target=lambda: serve(app_flask, host='127.0.0.1', port=5000), daemon=True); t_server.start()
    qt_app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    sys.exit(qt_app.exec_())

main()