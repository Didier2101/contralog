# app/utils/file_manager.py

import os
import shutil
from fastapi import UploadFile
from PyPDF2 import PdfReader
from app.core.errors import ErrorOperacion
import io

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def validar_y_guardar_pdf(archivo: UploadFile, subcarpeta: str) -> str:
    # 1. Validar extensión
    if not archivo.filename.lower().endswith(".pdf"):
        raise ErrorOperacion("El archivo debe ser un PDF.")

    # Leer el contenido en memoria para validar páginas sin guardarlo aún
    contenido = await archivo.read()
    pdf_reader = PdfReader(io.BytesIO(contenido))
    numero_paginas = len(pdf_reader.pages)

    # 2. Validar número de páginas (Máximo 3)
    if numero_paginas > 3:
        raise ErrorOperacion(f"El PDF es demasiado largo ({numero_paginas} páginas). Máximo permitido: 3.")

    # 3. Crear ruta de guardado
    ruta_destino = os.path.join(UPLOAD_DIR, subcarpeta)
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)

    nombre_archivo = f"{archivo.filename}"
    path_final = os.path.join(ruta_destino, nombre_archivo)

    # 4. Guardar archivo físicamente
    with open(path_final, "wb") as f:
        f.write(contenido)

    # Devolvemos la "URL" o ruta relativa para la DB
    return f"{subcarpeta}/{nombre_archivo}"