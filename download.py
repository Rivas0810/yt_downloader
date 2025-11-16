import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from pytubefix import YouTube

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Video Downloader')

        self.layout = QVBoxLayout()

        self.label = QLabel('Introduce la URL del video de YouTube:')
        self.layout.addWidget(self.label)

        self.url_input = QLineEdit()
        self.layout.addWidget(self.url_input)

        self.download_button = QPushButton('Descargar Video')
        self.download_button.clicked.connect(self.descargar_video)
        self.layout.addWidget(self.download_button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.setLayout(self.layout)

    def descargar_video(self):
        url = self.url_input.text()
        if url:
            self.output.append(f'Intentando descargar el video de: {url}')
            try:
                yt = YouTube(url)
                stream = yt.streams.get_highest_resolution()
                stream.download()
                self.output.append("Descarga completada!")
            except Exception as e:
                self.output.append(f"Ha ocurrido un error: {e}")
        else:
            self.output.append("Por favor, introduce una URL válida.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
