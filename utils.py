
import os
import subprocess

def ensure_folders(folders):
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def get_video_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout.decode().strip())
