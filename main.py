import os
from config import FPS_PERMITIDOS
from video_utils import obtener_info_video
from xml_resolve import generar_xml_fcp7
from srt_utils import unir_srts


def pedir_fps():
    print("FPS disponibles:")
    for fps in FPS_PERMITIDOS:
        print(f"- {fps}")

    while True:
        try:
            fps = float(input("Elegí el FPS: "))
            if fps in FPS_PERMITIDOS:
                return fps
            else:
                print("FPS no permitido.")
        except:
            print("Valor inválido.")


def pedir_audio():
    print("Tipo de audio:")
    print("1 - Stereo (2 canales)")
    print("2 - 4 canales")
    print("3 - 8 canales")

    opcion = input("Elegí opción: ")

    if opcion == "1":
        return 2
    elif opcion == "2":
        return 4
    elif opcion == "3":
        return 8
    else:
        return 2


def pedir_timecode():
    return input("Ingresá el timecode inicial (HH:MM:SS:FF): ")


def main():

    carpeta = input("Ruta de la carpeta con videos y SRT: ")

    fps = pedir_fps()
    canales_audio = pedir_audio()
    timecode_inicio = pedir_timecode()

    archivos = os.listdir(carpeta)

    videos = sorted([
        os.path.join(carpeta, f)
        for f in archivos
        if f.lower().endswith((".mp4", ".mov", ".mxf"))
    ])

    if not videos:
        print("No se encontraron videos.")
        return

    xml_output = os.path.join(carpeta, "timeline_generado.xml")

    generar_xml_fcp7(
        videos,
        fps,
        timecode_inicio,
        xml_output,
        canales_audio
    )

    print("Proceso finalizado.")


if __name__ == "__main__":
    main()