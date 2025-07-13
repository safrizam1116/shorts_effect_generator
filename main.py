
import os
import math
from ffmpeg_effect import apply_effects
from utils import ensure_folders, get_video_duration

SOURCE_VIDEO = "input/source.mp4"
OUTPUT_FOLDER = "output"
CLIP_DURATION = 28  # seconds

def process_video():
    ensure_folders([OUTPUT_FOLDER])
    duration = get_video_duration(SOURCE_VIDEO)
    total_clips = math.ceil(duration / CLIP_DURATION)
    print(f"🎞️ Durasi video: {duration:.2f} detik, akan dipotong jadi {total_clips} clip.")

    for i in range(total_clips):
        start = i * CLIP_DURATION
        output_path = os.path.join(OUTPUT_FOLDER, f"short_{i+1:03}.mp4")
        print(f"⚙️ Clip {i+1}/{total_clips} → mulai detik {start} → {output_path}")
        apply_effects(SOURCE_VIDEO, output_path, start_time=start, duration=CLIP_DURATION)
    print("✅ Semua clip selesai diproses!")

if __name__ == "__main__":
    process_video()
