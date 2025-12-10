from flask import Flask, request, jsonify
from flask_cors import CORS
from config import task_queue
from utils import clean_url

app_flask = Flask(__name__)
CORS(app_flask)

@app_flask.route('/download_audio', methods=['POST'])
def route_audio():
    data = request.json
    if data and 'url' in data:
        meta = [data.get('title',''), data.get('artist',''), data.get('album',''), data.get('art_url','')]
        task_queue.put((clean_url(data['url']), "audio", meta))
        return jsonify({"status": "queued", "msg": "Audio en cola"})
    return jsonify({"error": "No data"}), 400

@app_flask.route('/download_video', methods=['POST'])
def route_video():
    data = request.json
    if data and 'url' in data:
        task_queue.put((clean_url(data['url']), "video", None))
        return jsonify({"status": "queued", "msg": "Video en cola"})
    return jsonify({"error": "No data"}), 400