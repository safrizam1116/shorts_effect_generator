import os
import json
import subprocess
from flask import Flask
import threading

# ==== Konfigurasi file dan path ====
INPUT_PATH = "input/source.mp4"
OUTPUT_PATH = "output/clip.mp4"
LOG_PATH = "logs/uploaded.json"
output_file = os.path.abspath("output/clip.mp4")
CLIP_DURATION = 28  # detik
os.makedirs("output", exist_ok=True)
# ==== Fungsi potong video ====
def cut_video(source_path, output_path, start_time, duration):
    try:
        command = [
            "ffmpeg", "-y", "-i", input_file,
    "-t", "28",  # potong 28 detik pertama (bisa disesuaikan)
    "-vf", "scale=1440:2560",  # pastikan resolusi 9:16
    output_file
            "-nostdin",
            "-hide_banner",
            "-loglevel", "info",      # UBAH dari "error" → "info"
            "-ss", str(start_time),
            "-i", source_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "32",
            "-c:a", "aac",
            "-b:a", "64k",
            "-y",
            output_path
        ]
        print(f"[DEBUG] Menjalankan ffmpeg: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # CEK apakah file berhasil dibuat
if os.path.exists(output_file):
    print("[SUCCESS] Output video berhasil dibuat:", output_file)
else:
    print("[ERROR] Gagal membuat output video.")
        print("[DEBUG] STDOUT:\n", result.stdout)
        print("[DEBUG] STDERR:\n", result.stderr)
        result.check_returncode()
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg gagal: {e}")
        return False

        if os.path.exists(output_file):
    print("[SUCCESS] Output video berhasil dibuat:", output_file)
else:
    print("[ERROR] Gagal membuat output video.")


def get_next_clip_start_index(log_path):
    if not os.path.exists(log_path):
        return 0
    with open(log_path, "r") as f:
        logs = json.load(f)
    return len(logs) * CLIP_DURATION

def mark_as_cut(log_path):
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append("cut")
    with open(log_path, "w") as f:
        json.dump(logs, f)

def ensure_directories():
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

# ==== Fungsi utama proses potong ====
def process_clip():
    ensure_directories()

    if not os.path.exists(INPUT_PATH):
        print(f"[ERROR] File tidak ditemukan: {INPUT_PATH}")
        return

    start_time = get_next_clip_start_index(LOG_PATH)
    print(f"[INFO] Memotong dari detik {start_time}...")

    success = cut_video(INPUT_PATH, OUTPUT_PATH, start_time, CLIP_DURATION)
    if success:
        mark_as_cut(LOG_PATH)
        print("[OK] Berhasil potong: output/clip.mp4")
    else:
        print("[GAGAL] Gagal potong, mungkin durasi sudah habis.")

# ==== Flask Dummy Web Server (agar tetap hidup di Render) ====
app = Flask(__name__)

@app.route('/')
def home():
    return "🟢 Clip Generator Running"

# ==== Mulai thread pemotongan saat startup ====
if __name__ == "__main__":
    threading.Thread(target=process_clip).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
