# yt_downloader

Este repositorio contiene un programa que permite descargar contenido multimedia de YouTube. Su objetivo es ofrecer a los usuarios una forma sencilla de conservar videos o audios con fines personales o académicos.

## Características

- Descarga de contenido de YouTube (video y audio).
- Múltiples formas de uso:
  - **Script para consola** (Python).
  - **Extensión de Chrome** conectada a un *endpoint* (Python/Flask).
- Interfaz simple e intuitiva.
- Pensado para ser accesible incluso para usuarios sin conocimientos técnicos.

## Objetivo del proyecto

Este programa fue creado con la intención de:
- Proveer una herramienta sencilla y funcional para uso personal.
- Construir una solución portable, ligera y cada vez más sencilla.
- Experimentar y aprender.

Planeo continuar actualizando este repositorio para:
- Reducir dependencias.
- Mejorar la experiencia del usuario.
- Hacer la herramienta más fácil de instalar y ejecutar.

## Instalación y uso (próximamente)

✦ *Instrucciones detalladas en construcción...*

Como crear el archivo .exe

pyinstaller --noconfirm --onefile --windowed --name "YoutubeServerDownloader" --icon "youtube_icon.ico" --add-data "ffmpeg_audio.exe:." --add-data "youtube_icon.png:." "app.py"