import os
import json
import time
import datetime
import pytz
import subprocess
import gdown
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ====== KONFIGURASI ======
VIDEO_ID = "1QskinABo707mG4dxdzv8Mna8pGS-WBGj"
INPUT_PATH = "input/source.mp4"
CLIP_FOLDER = "output"
LOG_PATH = "logs/uploaded.json"
CLIP_DURATION = 28  # detik

# Load .env untuk YT token
load_dotenv()
TOKEN_PATH = os.getenv("TOKEN_PATH", "/etc/secrets/auth_token.json")

# ====== WAKTU WIB ======
def get_wib_now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone("Asia/Jakarta"))

def current_hour_key():
    return get_wib_now().strftime("%Y-%m-%d-%H")

def is_ganjil_jam():
    return get_wib_now().hour % 2 == 1

# ====== DOWNLOAD GOOGLE DRIVE ======
def download_from_gdrive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# ====== POTONG VIDEO (FFmpeg) ======
def cut_video(input_path, output_path, start_time=0, duration=28):
    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", input_path,
        "-t", str(duration),
        "-vf", "scale=1080:1920",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(command, check=True)

# ====== AUTENTIKASI YOUTUBE ======
def get_authenticated_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes=["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=creds)

# ====== UPLOAD KE YOUTUBE ======
def upload_video(path, title, description):
    youtube = get_authenticated_service()
    media = MediaFileUpload(path, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["shorts", "viral"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=media
    )

    print("📤 Uploading...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⏫ Progress: {int(status.progress() * 100)}%")

    print(f"✅ Uploaded → https://youtu.be/{response['id']}")

# ====== LOGIC ======
def get_offset():
    if not os.path.exists(LOG_PATH):
        return 0
    with open(LOG_PATH) as f:
        data = json.load(f)
    return len(data.get("uploaded", []))

def mark_uploaded():
    key = current_hour_key()
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump({"uploaded": []}, f)
    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        if key not in data["uploaded"]:
            data["uploaded"].append(key)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def already_uploaded():
    if not os.path.exists(LOG_PATH):
        return False
    with open(LOG_PATH) as f:
        data = json.load(f)
    return current_hour_key() in data.get("uploaded", [])

# ====== PROSES UPLOAD ======
def upload_task():
    now = get_wib_now()
    print(f"\n🕐 {now.strftime('%Y-%m-%d %H:%M:%S')} WIB | Cek upload...")

    if not is_ganjil_jam():
        print("⏳ Bukan jam ganjil. Skip.")
        return
    if already_uploaded():
        print("✅ Sudah upload jam ini. Skip.")
        return

    try:
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        print("📥 Download video dari Google Drive...")
        download_from_gdrive(VIDEO_ID, INPUT_PATH)

        offset = get_offset()
        start_sec = offset * CLIP_DURATION
        output_path = os.path.join(CLIP_FOLDER, f"short_{offset:03}.mp4")

        print(f"✂️ Potong dari detik ke-{start_sec}")
        cut_video(INPUT_PATH, output_path, start_time=start_sec, duration=CLIP_DURATION)

        title = f"🔥 Shorts {now.strftime('%H:%M')}"
        upload_video(output_path, title=title, description="#shorts #mlbb")

        mark_uploaded()
        print("✅ Selesai upload!")

    except Exception as e:
        print(f"❌ Gagal: {e}")

# ====== FLASK AGAR PORT TERDETEKSI RENDER ======
app = Flask(__name__)
@app.route("/")
def index():
    return f"🟢 Bot aktif | {get_wib_now().strftime('%H:%M:%S')} WIB"

# ====== MAIN ======
if __name__ == "__main__":
    Thread(target=lambda: app.run(host="0.0.0.0", port=3000)).start()
    time.sleep(3)
    upload_task()
    while True:
        time.sleep(60)
