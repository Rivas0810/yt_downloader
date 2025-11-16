import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error

class MP3MetadataEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Editor de Metadatos MP3")
        self.setGeometry(100, 100, 400, 500)

        # Widgets
        self.layout = QVBoxLayout()

        self.mp3_label = QLabel("Archivo MP3:")
        self.layout.addWidget(self.mp3_label)

        self.mp3_path = QLineEdit()
        self.layout.addWidget(self.mp3_path)

        self.mp3_button = QPushButton("Seleccionar Archivo MP3")
        self.mp3_button.clicked.connect(self.select_mp3)
        self.layout.addWidget(self.mp3_button)

        self.artist_label = QLabel("Artista:")
        self.layout.addWidget(self.artist_label)

        self.artist_input = QLineEdit()
        self.layout.addWidget(self.artist_input)

        self.title_label = QLabel("Título:")
        self.layout.addWidget(self.title_label)

        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        self.album_label = QLabel("Álbum:")
        self.layout.addWidget(self.album_label)

        self.album_input = QLineEdit()
        self.layout.addWidget(self.album_input)

        self.cover_label = QLabel("Portada:")
        self.layout.addWidget(self.cover_label)

        self.cover_path = QLineEdit()
        self.layout.addWidget(self.cover_path)

        self.cover_button = QPushButton("Seleccionar Imagen")
        self.cover_button.clicked.connect(self.select_cover)
        self.layout.addWidget(self.cover_button)

        self.cover_preview = QLabel("Vista previa de la portada")
        self.cover_preview.setFixedHeight(200)
        self.cover_preview.setScaledContents(True)
        self.layout.addWidget(self.cover_preview)

        self.save_button = QPushButton("Guardar Metadatos")
        self.save_button.clicked.connect(self.save_metadata)
        self.layout.addWidget(self.save_button)

        # Set main widget
        main_widget = QWidget()
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

    def select_mp3(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo MP3", "", "MP3 Files (*.mp3)")
        if file_path:
            self.mp3_path.setText(file_path)

    def select_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Image Files (*.jpg *.jpeg *.png)")
        if file_path:
            self.cover_path.setText(file_path)
            pixmap = QPixmap(file_path)
            self.cover_preview.setPixmap(pixmap)

    def save_metadata(self):
        mp3_file = self.mp3_path.text()
        artist = self.artist_input.text()
        title = self.title_input.text()
        album = self.album_input.text()
        cover_image = self.cover_path.text()

        if not mp3_file or not artist or not title or not album or not cover_image:
            self.show_error("Todos los campos son obligatorios.")
            return

        try:
            # Agregar metadatos básicos
            audio = EasyID3(mp3_file)
            audio['artist'] = artist
            audio['title'] = title
            audio['album'] = album
            audio.save()

            # Agregar imagen de portada
            audio = ID3(mp3_file)
            with open(cover_image, 'rb') as img:
                audio.add(APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',  # o 'image/png'
                    type=3,  # Cover
                    desc='Cover',
                    data=img.read()
                ))
            audio.save()

            self.show_message("Metadatos guardados correctamente.")
        except error as e:
            self.show_error(f"Error al guardar los metadatos: {e}")

    def show_message(self, message):
        self.statusBar().showMessage(message)

    def show_error(self, message):
        self.statusBar().showMessage(f"Error: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MP3MetadataEditor()
    editor.show()
    sys.exit(app.exec_())
