import os
import time
import subprocess
from pytubefix import YouTube
from config import FFMPEG_PATH, OUTPUT_AUDIO, OUTPUT_VIDEO, task_queue, gui_queue
from utils import sanitize_filename, safe_log_to_file

def worker_logic():
    if not os.path.exists(FFMPEG_PATH):
        gui_queue.put(f"ERROR CRÍTICO: No se encuentra ffmpeg en:\n{FFMPEG_PATH}")
    else:
        gui_queue.put(f"Servidor listo. Guardando en: files/")

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
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, startupinfo=startupinfo,
                    encoding='utf-8', errors='replace'
                )
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg falló: {result.stderr[-300:]}")

                if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 100:
                    raise Exception("FFmpeg terminó pero no creó el archivo MP3 válido.")

                if os.path.exists(file_path): 
                    try: os.remove(file_path)
                    except: pass

            duration = round(time.time() - start_time, 2)
            msg_final = f"Completado ({duration}s): {safe_title}"            
            gui_queue.put(msg_final)
            gui_queue.put(f"\n{'-' * 57}") 

            safe_log_to_file(f"Tiempo: {duration}s | {safe_title}")
            task_queue.task_done()

        except Exception as e:
            err_msg = f"ERROR: {str(e)}"
            gui_queue.put(err_msg)
            safe_log_to_file(f"ERROR: {err_msg}")
            if 'task' in locals(): task_queue.task_done()