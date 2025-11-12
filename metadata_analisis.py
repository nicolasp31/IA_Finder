# metadata_analisis.py
import sys
import os
import subprocess
import json

from typing import Any
from datetime import datetime
from config import (
    etiquetas_excluidas, PALABRAS_CLAVE_IA, PALABRAS_POSIBLES_IA, NUMEROS_FECHAS_CLAVE,
    ETIQUETAS_MODELO, ETIQUETAS_APLICACION, ETIQUETAS_POSIBLE_APLICACION
)


def obtener_ruta_exiftool() -> str:
    #Devuelve la ruta absoluta del ejecutable exiftool.exe
    nombre_exec = "exiftool.exe"

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))

    ruta_exiftool = os.path.join(base_path, "exiftool", nombre_exec)

    if not os.path.isfile(ruta_exiftool):
        raise FileNotFoundError(f"ExifTool no encontrado en: {ruta_exiftool}")

    return ruta_exiftool

def ejecutar_exiftool(ruta_archivo: str) -> dict[str, Any]:
    #Ejecuta ExifTool sobre un archivo y devuelve los metadatos como diccionario.
    #Usa la variable EXIFTOOL_HOME para asegurar que funcione el entorno
    ruta_exiftool = obtener_ruta_exiftool()
    exiftool_dir = os.path.dirname(ruta_exiftool)

    #se asegura que ExifTool encuentre su carpeta exiftool_files
    env = os.environ.copy()
    env["EXIFTOOL_HOME"] = exiftool_dir

    try:
        resultado = subprocess.run(
            [ruta_exiftool, "-json", ruta_archivo],
            capture_output=True,
            text=True,
            check=True,
            env=env  
        )

        metadata_lista = json.loads(resultado.stdout)
        if metadata_lista:
            return metadata_lista[0]
        else:
            return {}

    except subprocess.CalledProcessError as e:
        print("Error ejecutando ExifTool:", e)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise RuntimeError(
            f"Error al ejecutar ExifTool sobre '{ruta_archivo}'. "
            f"STDERR: {e.stderr.strip()}"
        )

def es_fecha(val):
    formatos = ["%Y:%m:%d %H:%M:%S", "%Y-%m-%d", "%Y:%m:%d"]
    for fmt in formatos:
        try:
            datetime.strptime(val, fmt)
            return True
        except:
            continue
    return False

def contiene_numero(val):
    return any(c.isdigit() for c in val)

def verificar_archivo_ia(metadata):
    coincidencias = []
    etiquetas_detectadas = set()

    for clave, valor in metadata.items():
        if clave in etiquetas_excluidas:
            continue
        if clave in etiquetas_detectadas:
            continue
        valor_str = str(valor).lower()

        for palabra in PALABRAS_CLAVE_IA:
            if palabra and palabra.lower() in valor_str:
                coincidencias.append(f"Patrón detectado en '{clave}': {valor}")
                etiquetas_detectadas.add(clave)
                break

    if coincidencias:
        mensaje = "\n".join(coincidencias)
        return True, mensaje

    coincidencias_posibles = []
    etiquetas_detectadas.clear()

    for clave, valor in metadata.items():
        if clave in etiquetas_excluidas:
            continue
        if clave in etiquetas_detectadas:
            continue
        valor_str = str(valor).lower()

        encontrado = False
        for palabra in PALABRAS_POSIBLES_IA:
            if palabra and palabra.lower() in valor_str:
                coincidencias_posibles.append(f"Patrón sospechoso detectado en '{clave}': {valor}")
                etiquetas_detectadas.add(clave)
                encontrado = True
                break

        if not encontrado:
            for patron_num_fecha in NUMEROS_FECHAS_CLAVE:
                if patron_num_fecha.lower() in valor_str:
                    coincidencias_posibles.append(f"Patrón numérico o fecha sospechosa en '{clave}': {valor}")
                    etiquetas_detectadas.add(clave)
                    break


    if coincidencias_posibles:
        mensaje = "\n".join(coincidencias_posibles)
        aviso = "\nNo es posible confirmar generación por IA, pero contiene metadatos sospechosos."
        return None, f"{mensaje}{aviso}"

    return False, "\nNo se encontraron patrones típicos de IA ni metadatos sospechosos."

def detectar_modelo(metadata):
    for clave, valor in metadata.items():
        valor_str = str(valor).lower()
        for etiqueta, nombre_modelo in ETIQUETAS_MODELO.items():
            if etiqueta.lower() in valor_str:
                return nombre_modelo
    return "Desconocido"

def detectar_aplicacion(metadata):
    for clave, valor in metadata.items():
        valor_str = str(valor).lower()
        for etiqueta, aplicaciones in ETIQUETAS_APLICACION.items():
            if etiqueta.lower() in valor_str:
                return aplicaciones if len(aplicaciones) > 1 else aplicaciones[0]

    aplicaciones_posibles = set()
    for clave, valor in metadata.items():
        valor_str = str(valor).lower()
        for etiqueta, aplicaciones in ETIQUETAS_POSIBLE_APLICACION.items():
            if etiqueta.lower() in valor_str:
                aplicaciones_posibles.update(aplicaciones)

    if not aplicaciones_posibles:
        return "Desconocido"
    elif len(aplicaciones_posibles) == 1:
        return aplicaciones_posibles.pop()
    else:
        return list(aplicaciones_posibles)



def analizar_imagen(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_video(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_docx(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_pdf(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_xlsx(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_pptx(ruta_archivo):
    metadata = ejecutar_exiftool(ruta_archivo)
    es_ia, mensaje = verificar_archivo_ia(metadata)
    return metadata, es_ia, mensaje

def analizar_metadata_por_tipo(ruta_archivo):
    ext = ruta_archivo.lower().split('.')[-1]
    if ext in ["png", "jpg", "jpeg"]:
        return analizar_imagen(ruta_archivo)
    elif ext == "mp4":
        return analizar_video(ruta_archivo)
    elif ext == "docx":
        return analizar_docx(ruta_archivo)
    elif ext == "pdf":
        return analizar_pdf(ruta_archivo)
    elif ext == "xlsx":
        return analizar_xlsx(ruta_archivo)
    elif ext == "pptx":
        return analizar_pptx(ruta_archivo)
    else:
        raise ValueError(f"Extensión no soportada para análisis: {ext}")