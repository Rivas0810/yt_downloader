import sys
import queue
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

from config import gui_queue, ICON_PATH, QSS_PATH

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(100)

    def init_ui(self):
        self.setWindowTitle("Servidor Descargador de Youtube")
        self.setFixedSize(600, 450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        try:
            with open(QSS_PATH, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"ADVERTENCIA: No se encontró el archivo de estilos en {QSS_PATH}")
        except Exception as e:
            print(f"Error cargando estilos: {e}")        

        layout = QVBoxLayout()
        layout.setSpacing(14)   
        layout.setContentsMargins(20, 20, 20, 25) 

        if os.path.exists(ICON_PATH):
            try:
                self.setWindowIcon(QIcon(ICON_PATH))
            except: pass

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.txt_log)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        btn_clear = QPushButton("Limpiar pantalla")
        btn_clear.setObjectName("BtnClear") 
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_log)
        buttons_layout.addWidget(btn_clear)

        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("BtnClose") 
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close_app)
        buttons_layout.addWidget(btn_close)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        self.lbl_footer = QLabel("Hecho por Fernando Rivas", self)
        self.lbl_footer.setObjectName("FooterLabel")
        self.lbl_footer.adjustSize()

    def resizeEvent(self, event):
        padding_right = 10
        padding_bottom = 3
        x = self.width() - self.lbl_footer.width() - padding_right
        y = self.height() - self.lbl_footer.height() - padding_bottom
        self.lbl_footer.move(x, y)
        super().resizeEvent(event)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    
    gui_queue.put("Probando la Interfaz del Servidor")
    gui_queue.put("La ventana se ha cargado correctamente.")
    sys.exit(app.exec_())