import os
import re


def extraer_numero(nombre):
    match = re.search(r'\d+', nombre)
    if match:
        return int(match.group())
    return float("inf")


def obtener_preview_renombrado(carpeta, extensiones):

    archivos = [
        f for f in os.listdir(carpeta)
        if f.lower().endswith(extensiones)
    ]

    if not archivos:
        return []

    # Orden natural por número detectado
    archivos.sort(key=lambda x: extraer_numero(x))

    cantidad = len(archivos)

    # Detectar cantidad de dígitos necesarios (01, 002, etc)
    digitos = len(str(cantidad))

    preview = []

    for i, archivo in enumerate(archivos):
        extension = os.path.splitext(archivo)[1]
        nuevo_nombre = f"{str(i+1).zfill(digitos)}{extension}"
        preview.append((archivo, nuevo_nombre))

    return preview


def aplicar_renombrado(carpeta, preview):

    temporales = []

    # Paso 1: renombrar a nombres temporales (evita conflictos)
    for i, (original, _) in enumerate(preview):
        ruta_original = os.path.join(carpeta, original)
        extension = os.path.splitext(original)[1]
        tmp_nombre = f"__tmp__{i}{extension}"
        ruta_tmp = os.path.join(carpeta, tmp_nombre)

        os.rename(ruta_original, ruta_tmp)
        temporales.append(ruta_tmp)

    # Paso 2: renombrar a nombres finales
    for i, ruta_tmp in enumerate(temporales):
        _, nuevo_nombre = preview[i]
        ruta_final = os.path.join(carpeta, nuevo_nombre)
        os.rename(ruta_tmp, ruta_final)

    return len(preview)