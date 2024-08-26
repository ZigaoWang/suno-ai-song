import os
import requests
import time
import dotenv
import json
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
key = API_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    audio_url = db.Column(db.String(500), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'title': self.title,
            'image_url': self.image_url,
            'audio_url': self.audio_url,
            'video_url': self.video_url,
            'lyrics': self.lyrics,
            'created_at': self.created_at.isoformat()
        }

def get_headers():
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

def submit_lyrics(prompt):
    url = "https://api.turboai.io/suno/submit/lyrics"
    data = {
        "prompt": prompt
    }

    response = requests.post(url, headers=get_headers(), json=data)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")

    response_data = response.json()
    if response_data.get("code") != "success":
        raise Exception(f"提交失败，响应信息: {response_data}")

    return response_data["data"]

def fetch(task_id):
    url = f"https://api.turboai.io/suno/fetch/{task_id}"

    response = requests.get(url, headers=get_headers())
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码: {response.status_code}")

    response_data = response.json()
    if response_data.get("code") != "success":
        raise Exception(f"查询失败，响应信息: {response_data}")

    return response_data["data"]

def submit_song(payload):
    response = requests.post("https://api.turboai.io/suno/submit/music", headers=get_headers(), json=payload)
    response_data = response.json()
    if response_data["code"] != "success":
        raise Exception("提交歌曲生成请求失败")
    return response_data["data"]

def cache_songs(songs_data):
    for song_data in songs_data:
        print("Caching song data:", song_data)  # Debugging line
        song = Song(
            title=song_data['title'],
            image_url=song_data['image_url'],
            audio_url=song_data['audio_url'],
            video_url=song_data['video_url'],
            lyrics=song_data['metadata']['prompt']
        )
        db.session.add(song)
    db.session.commit()

def get_cached_songs():
    songs = Song.query.order_by(Song.created_at.desc()).all()  # Order by created_at descending
    return [song.to_dict() for song in songs]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']
    try:
        lyrics_task_id = submit_lyrics(prompt)
        time.sleep(2)
        lyrics = fetch(lyrics_task_id)
        if lyrics['data'] is None:
            raise Exception("歌词生成失败")

        payload = {
            "prompt": lyrics['data']['text'],
            "mv": "chirp-v3-5",
            "title": prompt
        }

        song_task_id = submit_song(payload)

        max_retries = 100  # 设置最大重试次数（2秒检查一次，总计3分钟20秒）
        retries = 0

        def generate_status_updates():
            nonlocal retries
            progress = 0

            while retries < max_retries:
                task_data = fetch(song_task_id)
                task_status = task_data["status"]
                task_progress = task_data.get("progress", "0%")

                # Progress increment logic
                if task_status != "SUCCESS" and task_status != "FAILURE":
                    if progress < 90:
                        progress = min(progress + 2, 90)  # Fast progress to 90%
                    else:
                        progress = min(progress + 1, 95)  # Slow progress from 90% to 95%
                    task_progress = f"{progress}%"

                yield f"data: {json.dumps({'status': task_status, 'progress': task_progress})}\n\n"

                if task_status == "FAILURE":
                    yield f"data: {json.dumps({'error': '歌曲生成失败'})}\n\n"
                    return

                if task_status == "SUCCESS":
                    print("Task data:", task_data)  # Debugging line
                    cache_songs(task_data['data'])
                    yield f"data: {json.dumps({'result': task_data['data']})}\n\n"
                    return

                # Random delay between 1 and 2 seconds
                time.sleep(1 + (retries % 2))
                retries += 1

            yield f"data: {json.dumps({'error': '歌曲生成超时'})}\n\n"

        return Response(stream_with_context(generate_status_updates()), content_type='text/event-stream')

    except Exception as e:
        # Log the full stack trace for better debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/cached_songs', methods=['GET'])
def cached_songs():
    try:
        songs = get_cached_songs()
        print("Cached songs fetched:", songs)  # Debugging line
        return jsonify(songs)
    except Exception as e:
        # Log the full stack trace for better debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Recreate tables with new schema
    app.run(debug=True)