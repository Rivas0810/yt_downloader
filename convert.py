import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class MP4ToMP3Converter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.label = QLabel("Selecciona un archivo MP4 para convertir a MP3", self)
        self.select_button = QPushButton("Seleccionar archivo MP4", self)
        self.convert_button = QPushButton("Convertir a MP3", self)
        
        self.select_button.clicked.connect(self.select_file)
        self.convert_button.clicked.connect(self.convert_to_mp3)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.convert_button)

        self.setLayout(self.layout)
        self.setWindowTitle("MP4 a MP3 Converter")
        self.setGeometry(300, 300, 400, 150)
        self.selected_file = None

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo MP4", "", "Archivos MP4 (*.mp4);;Todos los archivos (*)", options=options)
        if file_path:
            self.selected_file = file_path
            self.label.setText(f"Archivo seleccionado: {file_path}")

    def convert_to_mp3(self):
        if not self.selected_file:
            self.label.setText("Por favor, selecciona un archivo MP4 primero.")
            return

        mp3_file = self.selected_file.rsplit('.', 1)[0] + '.mp3'
        command = [
            'C:/ffmpeg/bin/ffmpeg.exe',  # Usa la ruta completa del ejecutable FFmpeg
            '-i', self.selected_file,
            '-q:a', '0',
            '-map', 'a',
            mp3_file
        ]

        try:
            subprocess.run(command, check=True)
            self.label.setText(f"Archivo convertido exitosamente a: {mp3_file}")
        except subprocess.CalledProcessError as e:
            self.label.setText("Error al convertir el archivo.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = MP4ToMP3Converter()
    converter.show()
    sys.exit(app.exec_())

