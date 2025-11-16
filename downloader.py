import argparse
import sys
import os
import subprocess
import re 
from pytubefix import YouTube
from pytubefix import exceptions

FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe' 

if len(sys.argv) > 1 and sys.argv[1] == "help":
    print("""
    Uso: python downloader.py [opciones]

    Opciones:
    -u, --url       URL del video de YouTube a descargar (obligatorio)
    -a, --audio     Descargar solo audio (opcional). Si se incluye, descarga y CONVIERTE a MP3.
    -o, --output    Ruta de salida para el archivo (opcional). Por defecto: ./mp4 o ./mp3
    -v, --verbose   Modo verboso (opcional)

    Ejemplo:
    python downloader.py -u https://youtu.be/ejemplo-url -a -o /home/usuario/musica
    """)
    sys.exit(0)

parser = argparse.ArgumentParser(description="YouTube Multimedia Downloader")
parser.add_argument("-u", "--url", help="URL del video de YouTube a descargar", required=True)
parser.add_argument("-a", "--audio", help="Descargar solo audio (modo por defecto es video)", action="store_true")
parser.add_argument("-o", "--output", help="Ruta de salida para el archivo", default="./mp4")
parser.add_argument("-v", "--verbose", help="Modo verboso", action="store_true")
args = parser.parse_args()

url = args.url
output_path = args.output
download_type = "Audio" if args.audio else "Video"

if args.verbose:
    print("Modo verboso activado: Mostrando detalles del proceso.")

if args.audio and output_path == "./mp4":
    output_path = "./mp3"
    if args.verbose:
        print("Ruta por defecto ajustada a './mp3' para la descarga de audio.")

try:
    if args.verbose:
        print("Intentando inicializar el objeto YouTube...")
        
    yt = YouTube(url)
    titulo = yt.title
    print(f"Video encontrado: '{titulo}'")
    
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    if download_type == "Audio":
        stream = yt.streams.get_audio_only()
    else:
        stream = yt.streams.get_highest_resolution()

    if stream is None:
        raise ValueError("No se encontró un stream adecuado para la descarga.")

    print(f"Iniciando descarga de '{stream.default_filename}'...")
    download_file_path = stream.download(output_path)
    print(f"Descarga completada (Formato inicial). Archivo en: **{download_file_path}**")

    if download_type == "Audio":
        base, ext = os.path.splitext(download_file_path)
        mp3_file_path = base + ".mp3"
        print("Iniciando conversión y adición de metadatos con FFmpeg...")

        artist_name = yt.author.strip()

        sufijos_a_eliminar = [' - Topic', 'VEVO', 'VEVO - Topic', 'VEVO', ' Official']
        for sufijo in sufijos_a_eliminar:
            if artist_name.endswith(sufijo):
                artist_name = artist_name[:-len(sufijo)].strip()
                break 
        
        if artist_name != artist_name.upper():
            artist_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', artist_name)

        command = [
            FFMPEG_PATH, 
            '-i', download_file_path,  # Archivo de entrada (M4A)
            '-map', '0:a',
            '-c:a', 'libmp3lame', 
            '-q:a', '0',
            '-metadata', f"title={yt.title}",
            '-metadata', f"artist={artist_name}",
            mp3_file_path
        ]

        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(download_file_path)
        
        print(f"Proceso de audio completado. Archivo final: **{mp3_file_path}**")
        
    else:
        print(f"Descarga de video finalizada. Archivo guardado en: **{download_file_path}**")

except FileNotFoundError:
    print(f"ERROR FATAL: FFmpeg no encontrado en la ruta: '{FFMPEG_PATH}'.")
    print("Por favor, instala FFmpeg y actualiza la variable 'FFMPEG_PATH' en el script.")
except subprocess.CalledProcessError as e:
    print(f"ERROR: La conversión con FFmpeg falló. Código de error: {e.returncode}")
    print("Verifica si el archivo M4A se descargó correctamente o si FFmpeg tiene permisos.")
except exceptions.RegexMatchError:
    print("ERROR: El enlace proporcionado no coincide con ningún patrón de URL conocido de YouTube.")
except exceptions.VideoUnavailable:
    print("ERROR: El video no está disponible (fue borrado, es privado o está geobloqueado).")
except exceptions.AgeRestrictedError:
    print("ERROR: El video tiene restricciones de edad. No se puede descargar sin autenticación.")
except ValueError as ve:
    print(f"ERROR de procesamiento: {ve}")
except Exception as e:
    print(f"ERROR inesperado: {type(e).__name__}: {e}")