def subir_archivo_s3(file, folder):
    # Por ahora retorna una ruta simulada hasta conectar AWS
    return f"s3://contralog-bucket/{folder}/{file.filename}"