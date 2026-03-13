from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Construir la URL de conexión (SQLAlchemy usa este formato)
# mysql+pymysql://usuario:password@host:puerto/nombre_db
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 2. Crear el Motor (Engine)
# 'pool_recycle' evita el error de "MySQL server has gone away"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_recycle=3600, 
    pool_pre_ping=True
)

# 3. Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase base para los Modelos
Base = declarative_base()

# 5. Dependencia para FastAPI (La que usaremos en las rutas)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()