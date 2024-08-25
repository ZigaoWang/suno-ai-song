import os
import requests
import time
import dotenv
from flask import Flask, render_template, request, jsonify

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

    # 添加日志以调试问题
    print(f"Fetched data for task_id {task_id}: {response_data}")

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
        print("歌词任务ID:", lyrics_task_id)
        time.sleep(2)
        lyrics = fetch(lyrics_task_id)
        print("歌词内容:", lyrics['data']['text'])

        payload = {
            "prompt": lyrics['data']['text'],
            "tags": "energetic pop",
            "mv": "chirp-v3-5",
            "title": prompt  # Use the user's prompt as the song title
        }

        song_task_id = submit_song(payload)
        print("歌曲任务ID:", song_task_id)

        while True:
            task_data = fetch(song_task_id)
            task_status = task_data["status"]

            print(f"歌曲生成状态： {task_status}，请等待10s...")

            if task_status == "FAILURE":
                raise Exception("歌曲生成失败")

            if task_status == "SUCCESS":
                break

            time.sleep(10)

        print("歌曲生成成功")
        return jsonify(task_data["data"])

    except Exception as e:
        print(f"发生错误: {e}")  # 在终端打印错误信息以便调试
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)