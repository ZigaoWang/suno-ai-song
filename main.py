import os
import requests
import time
import dotenv
import json
from flask import Flask, render_template, request, jsonify, stream_with_context, Response, send_from_directory

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
key = API_KEY

app = Flask(__name__)

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
            "tags": "energetic pop",
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
                    yield f"data: {json.dumps({'result': task_data['data']})}\n\n"
                    return

                # Random delay between 1 and 2 seconds
                time.sleep(1 + (retries % 2))
                retries += 1

            yield f"data: {json.dumps({'error': '歌曲生成超时'})}\n\n"

        return Response(stream_with_context(generate_status_updates()), content_type='text/event-stream')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pre_generated', methods=['GET'])
def pre_generated():
    try:
        pre_generated_folder = 'pre_generated_songs'
        files = os.listdir(pre_generated_folder)
        if not files:
            raise Exception("没有预生成的歌曲文件")

        import random
        file = random.choice(files)
        return send_from_directory(pre_generated_folder, file)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)