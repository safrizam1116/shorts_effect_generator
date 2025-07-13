import os
import json
import subprocess

INPUT_PATH = "input/source.mp4"
OUTPUT_PATH = "output/clip.mp4"
LOG_PATH = "logs/uploaded_log.json"
CLIP_DURATION = 28  # detik

def cut_video(source_path, output_path, start_time, duration):
    try:
        command = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel", "error",
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
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg gagal: {e}")
        return False

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

def main():
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

if __name__ == "__main__":
    main()
