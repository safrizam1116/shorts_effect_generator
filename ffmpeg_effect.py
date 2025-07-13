
import subprocess

def apply_effects(input_path, output_path, start_time=0, duration=28):
    filter_chain = (
        "crop='ih*9/16:ih',"
        "zoompan=z='min(zoom+0.0015,1.05)':d=25:s=1080x1920,"
        "eq=saturation=1.6,"
        "gblur=sigma=3,"
        "fps=30,"
        "format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", input_path,
        "-vf", filter_chain,
        "-preset", "fast",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    subprocess.run(command, check=True)
