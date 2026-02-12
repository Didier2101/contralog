import uuid
import datetime

def generar_codigo_unico(prefijo: str) -> str:
    """
    Genera un código formato: PREFIJO-AÑO-HEX_UNICO
    Ejemplo: CNT-2026-A1B2
    """
    anio = datetime.datetime.now().year
    # Usamos una parte de un UUID para asegurar que no se repita
    codigo_hex = uuid.uuid4().hex[:6].upper() 
    return f"{prefijo}-{anio}-{codigo_hex}"

# Funciones específicas para tu sistema CLM
def generar_codigo_contrato():
    return generar_codigo_unico("CNT")

def generar_codigo_cliente():
    return generar_codigo_unico("CLI")

def generar_codigo_oportunidad():
    return generar_codigo_unico("OPP")

def generar_codigo_documento():
    """Genera códigos tipo DOC-2026-X89Z"""
    return generar_codigo_unico("DOC")