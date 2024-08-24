import os
import requests
import time
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
key = API_KEY


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


def main():
    prompt = "An upbeat, energetic song about different types of technology gadgets or tools."
    try:
        lyrics_task_id = submit_lyrics(prompt)
        print("歌词任务ID:" + lyrics_task_id)
        time.sleep(2)
        lyrics = fetch(lyrics_task_id)
        print("歌词内容:" + lyrics['data']['text'])

        # 组装歌曲生成请求
        payload = {
            "prompt": lyrics['data']['text'],
            "tags": "energetic pop",
            "mv": "chirp-v3-5",
            "title": "Technology Gadgets"
        }

        # 提交歌曲生成请求
        song_task_id = submit_song(payload)
        print("歌曲任务ID:" + song_task_id)

        # 轮询查询歌曲生成状态
        while True:
            task_data = fetch(song_task_id)
            task_status = task_data["status"]

            if task_status == "FAILURE":
                raise Exception("歌曲生成失败")

            if task_status == "SUCCESS":
                break

            print(f"歌曲生成状态： {task_status}，请等待10s...")

            time.sleep(10)
        # 打印歌曲信息
        for song in task_data["data"]:
            print(f"歌曲名称: {song['title']}")
            print(f"歌曲封面: {song['image_url']}")
            print(f"音频地址: {song['audio_url']}")
            print(f"视频地址: {song['video_url']}")
            print("-" * 40)

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
