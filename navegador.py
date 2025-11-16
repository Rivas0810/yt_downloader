import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QWidget, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QGuiApplication  # Para acceder al clipboard

from pytubefix import YouTube


class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navegador Sencillo")
        self.setGeometry(100, 100, 800, 600)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.youtube.com/"))
        self.browser.urlChanged.connect(self.update_url_bar)  # Conectar la señal urlChanged

        # Crear barra de herramientas
        self.navigation_bar = QHBoxLayout()
        
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.browser.back)
        self.navigation_bar.addWidget(self.back_button)
        
        self.forward_button = QPushButton("→")
        self.forward_button.clicked.connect(self.browser.forward)
        self.navigation_bar.addWidget(self.forward_button)
        
        self.refresh_button = QPushButton("⟳")
        self.refresh_button.clicked.connect(self.browser.reload)
        self.navigation_bar.addWidget(self.refresh_button)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.url_bar)
        
        # self.copy_button = QPushButton("Copiar URL")
        # self.copy_button.clicked.connect(self.copy_url_to_clipboard)
        # self.navigation_bar.addWidget(self.copy_button)
        
        self.copy_button = QPushButton("Descargar video")
        self.copy_button.clicked.connect(self.copy_url_to_clipboard)
        self.navigation_bar.addWidget(self.copy_button)

        # Diseño principal
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.navigation_bar)
        self.main_layout.addWidget(self.browser)
        
        # Configuración de contenedor
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))
        
    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())  # Actualizar el texto de la barra de direcciones

    def copy_url_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.url_bar.text())  # Copiar el texto de la barra de direcciones al portapapeles

    def download_video(self):
        url  = self.url_bar.text()
        print(f'Intentando descargar el video de: {url}')
        try:
            yt = YouTube(self.url)
            stream = yt.streams.get_highest_resolution()
            stream.download()
            print("Descarga completada!")
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            
# Correr la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())