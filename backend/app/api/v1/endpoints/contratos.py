from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.core.security import obtener_usuario_actual
from app.services import contrato_service
from app.schemas.contrato import ContratoOut
import json

router = APIRouter()

@router.post("/", response_model=ContratoOut)
async def crear_nuevo_contrato(
    # Recibimos el JSON como un string en el formulario
    data: str = Form(...), 
    archivo: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(obtener_usuario_actual)
):
    try:
        # Convertimos el string JSON a diccionario
        datos_contrato = json.loads(data)
        
        # El id_usuario viene del token (verificado en el paso anterior)
        id_operador = int(current_user["id_usuario"])
        
        return await contrato_service.registrar_contrato_completo(
            db=db,
            datos_contrato=datos_contrato,
            archivo_principal=archivo,
            id_usuario=id_operador
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El campo 'data' debe ser un JSON válido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# obtener todos los contratos listados por paginacion
@router.get("/", response_model=list[ContratoOut])
def listar_contratos(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(deps.get_db), 
    current_user: dict = Depends(obtener_usuario_actual)
):
    return contrato_service.listar_contratos(db, skip=skip, limit=limit)    