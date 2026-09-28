import subprocess
import json

def obtener_info_video(video_path):
    comando = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        video_path
    ]

    resultado = subprocess.run(
    comando,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
    if not resultado.stdout:
        print("Error al obtener información del video")
        print("STDERR:", resultado.stderr)
        return None, None

    info = json.loads(resultado.stdout.decode("utf-8"))

    duracion = float(info["format"]["duration"])

    # Buscar stream de video
    for stream in info["streams"]:
        if stream["codec_type"] == "video":
            fps_str = stream["r_frame_rate"]
            num, den = map(int, fps_str.split("/"))
            fps_real = num / den
            break

    return duracion, fps_real