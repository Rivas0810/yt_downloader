from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import argparse
import sys
import os
import subprocess
import re 
from pytubefix import YouTube
from pytubefix import exceptions

FFMPEG_PATH = 'C:/ffmpeg/bin/ffmpeg.exe'

def clean_url(url):
    patron = r'[?&]v=([^&]+)'
    match = re.search(patron, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return url
    
def download_content(url, content_type = "video"):
    if (content_type) == "video":
        output_path = "./mp4"
    elif (content_type == "audio"):
        output_path = "./mp3"
    else:
        output_path = f"./type_{content_type}"
        

    try:    
        yt = YouTube(url)
        titulo = yt.title
        print(f"Video encontrado: '{titulo}'")
        
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        
        if content_type == "audio":
            stream = yt.streams.get_audio_only()
        else:
            stream = yt.streams.get_highest_resolution()

        if stream is None:
            raise ValueError("No se encontró un stream adecuado para la descarga.")

        print(f"Iniciando descarga de '{stream.default_filename}'...")
        download_file_path = stream.download(output_path)
        print(f"Descarga completada (Formato inicial). Archivo en: **{download_file_path}**")

        if content_type == "audio":
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





app = Flask(__name__)
CORS(app)

@app.route('/download_video', methods=['POST'])
def download_video():
    """Ruta para la descarga de video simple."""
    data = request.json
    if data and 'url' in data:

        url_recibida = data['url']
        print("====================================")
        print("SOLICITUD DE VIDEO RECIBIDA 🎬")
        print(f"URL: {url_recibida}")
        print("====================================")
        
        return jsonify({"status": "éxito", "mensaje": "Video request recibido"})
    return jsonify({"status": "error", "mensaje": "No se recibió la URL"}), 400

@app.route('/download_audio', methods=['POST'])
def download_audio():
    """Ruta para la descarga de audio con metadatos."""
    data = request.json
    if data and 'url' in data:

        url_recibida = data['url']
        # Obtenemos los metadatos (pueden venir vacíos)
        title = data.get('title', 'N/A')
        artist = data.get('artist', 'N/A')
        album = data.get('album', 'N/A')
        art_url = data.get('art_url', 'N/A')
        
        print("====================================")
        print("SOLICITUD DE AUDIO RECIBIDA 🎵")
        print(f"URL: {url_recibida}")
        print(f"  Título: {title}")
        print(f"  Artista: {artist}")
        print(f"  Álbum: {album}")
        print(f"  Portada (URL): {art_url}")
        print("====================================")
        
        return jsonify({"status": "éxito", "mensaje": "Audio request recibido"})
    return jsonify({"status": "error", "mensaje": "Datos incompletos"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)