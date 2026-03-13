from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from app.models.documento import ContratoDocumento
from app.utils.codigos import generar_codigo_contrato, generar_codigo_documento
from app.utils.file_manager import validar_y_guardar_pdf # Tu lógica de guardado
from app.core.errors import ErrorOperacion
from datetime import date, timedelta
from app.core.errors import ErrorOperacion


from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from app.utils.codigos import generar_codigo_contrato
from app.core.errors import ErrorOperacion

async def registrar_contrato_completo(
    db: Session, 
    datos_contrato: dict, 
    ruta_pdf: str, # Ya guardado por el file_manager
    id_usuario: int
):
    try:
        # VALIDACIÓN SENIOR: Casteo de seguridad
        nuevo_contrato = Contrato(
            codigo_unico=generar_codigo_contrato(),
            creado_por=int(id_usuario), # Forzamos entero para la FK
            id_cliente=int(datos_contrato['id_cliente']),
            tipo_contrato=datos_contrato['tipo_contrato'],
            fecha_inicio=datos_contrato['fecha_inicio'],
            fecha_final=datos_contrato['fecha_final'],
            nda_firmado=datos_contrato.get('nda_firmado', False),
            s3_key_contrato=ruta_pdf,
            estado='activo'
        )
        
        db.add(nuevo_contrato)
        db.commit()
        db.refresh(nuevo_contrato)
        return nuevo_contrato

    except Exception as e:
        db.rollback()
        raise ErrorOperacion(f"Error en base de datos: {str(e)}")
    
# obtener contratos con paginación
def listar_contratos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Contrato).offset(skip).limit(limit).all()

def validar_logica_contrato(fecha_inicio: date, fecha_final: date):
    if fecha_inicio >= fecha_final:
        raise ErrorOperacion("La fecha de inicio no puede ser mayor o igual a la de vencimiento.")
    
    # Si el contrato vence hoy mismo, ya nace como 'por_vencer' o 'vencido'
    if fecha_final < date.today():
         raise ErrorOperacion("No puedes registrar un contrato que ya está vencido.")
    
def verificar_vencimientos(db: Session):
    """
    Actualiza el estado de los contratos según la fecha actual.
    """
    hoy = date.today()
    proximos_15_dias = hoy + timedelta(days=15)
    
    # 1. Marcar como vencidos
    db.query(Contrato).filter(
        Contrato.fecha_final < hoy, 
        Contrato.estado != 'vencido'
    ).update({"estado": "vencido"}, synchronize_session=False)

    # 2. Marcar como por vencer
    db.query(Contrato).filter(
        Contrato.fecha_final >= hoy,
        Contrato.fecha_final <= proximos_15_dias,
        Contrato.estado == 'activo'
    ).update({"estado": "por_vencer"}, synchronize_session=False)
    
    db.commit()
    return True