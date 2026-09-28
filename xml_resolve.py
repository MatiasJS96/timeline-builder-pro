import os
import xml.etree.ElementTree as ET
from video_utils import obtener_info_video


def timecode_a_frames(tc, fps):
    hh, mm, ss, ff = map(int, tc.split(":"))
    return int((hh * 3600 + mm * 60 + ss) * fps + ff)


def generar_xml_fcp7(videos, fps, timecode_inicio, output_path, canales_audio):

    xmeml = ET.Element("xmeml", version="5")
    sequence = ET.SubElement(xmeml, "sequence")
    ET.SubElement(sequence, "name").text = "Timeline Generado"

    rate = ET.SubElement(sequence, "rate")
    ET.SubElement(rate, "timebase").text = str(int(fps))
    ET.SubElement(rate, "ntsc").text = "FALSE"

    media = ET.SubElement(sequence, "media")

    # ================= VIDEO =================
    video = ET.SubElement(media, "video")

    format_tag = ET.SubElement(video, "format")
    sc = ET.SubElement(format_tag, "samplecharacteristics")
    ET.SubElement(sc, "width").text = "1920"
    ET.SubElement(sc, "height").text = "1080"
    ET.SubElement(sc, "pixelaspectratio").text = "square"
    ET.SubElement(sc, "fielddominance").text = "none"

    video_track = ET.SubElement(video, "track")

    # ================= AUDIO =================
    audio = ET.SubElement(media, "audio")

    timeline_cursor = timecode_a_frames(timecode_inicio, fps)
    total_duration = 0

    for idx, video_path in enumerate(videos):

        duracion_seg, _ = obtener_info_video(video_path)
        duracion_frames = int(duracion_seg * fps)
        total_duration += duracion_frames

        file_id = f"file-{idx+1}"

        ruta = os.path.abspath(video_path).replace("\\", "/")
        ruta = f"file:///{ruta}"

        # VIDEO CLIP
        clip_v = ET.SubElement(video_track, "clipitem", id=f"clipitem-v-{idx+1}")
        ET.SubElement(clip_v, "name").text = os.path.basename(video_path)
        ET.SubElement(clip_v, "start").text = str(timeline_cursor)
        ET.SubElement(clip_v, "end").text = str(timeline_cursor + duracion_frames)
        ET.SubElement(clip_v, "in").text = "0"
        ET.SubElement(clip_v, "out").text = str(duracion_frames)

        file_tag = ET.SubElement(clip_v, "file", id=file_id)
        ET.SubElement(file_tag, "name").text = os.path.basename(video_path)
        ET.SubElement(file_tag, "pathurl").text = ruta
        ET.SubElement(file_tag, "duration").text = str(duracion_frames)

        sourcetrack_v = ET.SubElement(clip_v, "sourcetrack")
        ET.SubElement(sourcetrack_v, "mediatype").text = "video"

        # AUDIO
        for canal in range(1, canales_audio + 1):

            if len(audio.findall("track")) < canal:
                audio_track = ET.SubElement(audio, "track")
            else:
                audio_track = audio.findall("track")[canal - 1]

            clip_a = ET.SubElement(audio_track, "clipitem", id=f"clipitem-a-{idx+1}-{canal}")
            ET.SubElement(clip_a, "name").text = os.path.basename(video_path)
            ET.SubElement(clip_a, "start").text = str(timeline_cursor)
            ET.SubElement(clip_a, "end").text = str(timeline_cursor + duracion_frames)
            ET.SubElement(clip_a, "in").text = "0"
            ET.SubElement(clip_a, "out").text = str(duracion_frames)

            file_ref = ET.SubElement(clip_a, "file", id=file_id)

            sourcetrack_a = ET.SubElement(clip_a, "sourcetrack")
            ET.SubElement(sourcetrack_a, "mediatype").text = "audio"
            ET.SubElement(sourcetrack_a, "trackindex").text = str(canal)

        timeline_cursor += duracion_frames

    ET.SubElement(sequence, "duration").text = str(total_duration)

    tree = ET.ElementTree(xmeml)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)