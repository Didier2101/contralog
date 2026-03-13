from fastapi import APIRouter
from app.api.v1.endpoints import usuarios, cargos, clientes, proyectos, horas, auth, contratos

api_router = APIRouter()

# Aquí conectamos los módulos de endpoints
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
api_router.include_router(cargos.router, prefix="/cargos", tags=["Cargos"]) 
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(proyectos.router, prefix="/proyectos", tags=["Proyectos"])
api_router.include_router(horas.router, prefix="/horas", tags=["Control de Horas"])
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])

# Cuando tengas listos los demás, solo los desbloqueas aquí:
# api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
# api_router.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])