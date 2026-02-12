# app/core/exceptions.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import mysql.connector
from app.core.errors import RegistroNoEncontrado, DatosDuplicados, ErrorOperacion, CredencialesInvalidas

def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(RegistroNoEncontrado)
    async def registro_no_encontrado_handler(request: Request, exc: RegistroNoEncontrado):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "tipo": "NotFound", "message": exc.mensaje}
        )

    @app.exception_handler(DatosDuplicados)
    async def datos_duplicados_handler(request: Request, exc: DatosDuplicados):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "tipo": "DuplicateData", "message": exc.mensaje}
        )

    @app.exception_handler(ErrorOperacion)
    async def error_operacion_handler(request: Request, exc: ErrorOperacion):
        return JSONResponse(
            status_code=422, # Unprocessable Entity
            content={"status": "error", "tipo": "OperationError", "message": exc.mensaje}
        )

    @app.exception_handler(mysql.connector.Error)
    async def mysql_exception_handler(request: Request, exc: mysql.connector.Error):
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "Error de base de datos.", "technical": str(exc)}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Fallo crítico del sistema.", "technical": str(exc)}
        )
    
    @app.exception_handler(CredencialesInvalidas)
    async def credenciales_invalidas_handler(request: Request, exc: CredencialesInvalidas):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "tipo": "Unauthorized", "message": exc.mensaje}
        )