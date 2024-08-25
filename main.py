import os
import requests
import time
import dotenv
import json
from flask import Flask, render_template, request, jsonify, stream_with_context, Response

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

    print(f"Fetched data for task_id {task_id}: {response_data}")  # Debugging log

    return response_data["data"]

def submit_song(payload):
    response = requests.post("https://api.turboai.io/suno/submit/music", headers=get_headers(), json=payload)
    response_data = response.json()
    print(f"提交歌曲生成请求响应: {response_data}")  # Debugging log
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
        print("歌词任务ID:", lyrics_task_id)
        time.sleep(2)
        lyrics = fetch(lyrics_task_id)
        if lyrics['data'] is None:
            raise Exception("歌词生成失败")
        print("歌词内容:", lyrics['data']['text'])

        payload = {
            "prompt": lyrics['data']['text'],
            "tags": "energetic pop",
            "mv": "chirp-v3-5",
            "title": prompt
        }

        song_task_id = submit_song(payload)
        print("歌曲任务ID:", song_task_id)

        max_retries = 100  # 设置最大重试次数（3秒检查一次，总计5分钟）
        retries = 0

        def generate_status_updates():
            nonlocal retries
            while retries < max_retries:
                task_data = fetch(song_task_id)
                task_status = task_data["status"]
                progress = task_data.get("progress", "0%")

                print(f"歌曲生成状态: {task_status}, 进度: {progress}")  # Debugging log

                yield f"data: {json.dumps({'status': task_status, 'progress': progress})}\n\n"

                if task_status == "FAILURE":
                    yield f"data: {json.dumps({'error': '歌曲生成失败'})}\n\n"
                    return

                if task_status == "SUCCESS":
                    yield f"data: {json.dumps({'result': task_data['data']})}\n\n"
                    return

                time.sleep(3)
                retries += 1

            yield f"data: {json.dumps({'error': '歌曲生成超时'})}\n\n"

        return Response(stream_with_context(generate_status_updates()), content_type='text/event-stream')

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/pre_generated', methods=['GET'])
def pre_generated():
    try:
        # 从预生成的文件夹中读取一个随机的文件
        pre_generated_folder = 'pre_generated_songs'
        files = os.listdir(pre_generated_folder)
        if not files:
            raise Exception("没有预生成的歌曲文件")

        # 随机选择一个文件
        import random
        file = random.choice(files)
        with open(os.path.join(pre_generated_folder, file), 'r') as f:
            song_data = json.load(f)

        return jsonify([song_data])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)