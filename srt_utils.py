import re
from datetime import timedelta

def timecode_a_timedelta(tc):
    h, m, s_ms = tc.split(":")
    s, ms = s_ms.split(",")
    return timedelta(
        hours=int(h),
        minutes=int(m),
        seconds=int(s),
        milliseconds=int(ms)
    )

def timedelta_a_timecode(td):
    total_seconds = int(td.total_seconds())
    ms = int(td.microseconds / 1000)

    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60

    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def leer_srt(path):
    with open(path, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = re.split(r"\n\s*\n", contenido.strip())
    entradas = []

    for bloque in bloques:
        lineas = bloque.split("\n")
        if len(lineas) >= 3:
            tiempo = lineas[1]
            texto = "\n".join(lineas[2:])
            inicio, fin = tiempo.split(" --> ")
            entradas.append((inicio.strip(), fin.strip(), texto))

    return entradas

def unir_srts(lista_srts, lista_duraciones_segundos, output_path):

    acumulado = timedelta(0)
    indice_global = 1
    resultado = []

    for srt_path, duracion_seg in zip(lista_srts, lista_duraciones_segundos):

        entradas = leer_srt(srt_path)

        for inicio, fin, texto in entradas:
            nuevo_inicio = timecode_a_timedelta(inicio) + acumulado
            nuevo_fin = timecode_a_timedelta(fin) + acumulado

            resultado.append(
                f"{indice_global}\n"
                f"{timedelta_a_timecode(nuevo_inicio)} --> {timedelta_a_timecode(nuevo_fin)}\n"
                f"{texto}\n"
            )

            indice_global += 1

        acumulado += timedelta(seconds=duracion_seg)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(resultado))

    print("SRT combinado generado correctamente.")