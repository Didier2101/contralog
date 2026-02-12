import mysql.connector
from mysql.connector import pooling
import time
from app.core.config import settings  # <--- Importamos tus variables de entorno

db_pool = None

def inicializar_pool():
    global db_pool
    
    # Usamos los valores cargados desde el archivo .env a través de settings
    host_db = settings.DB_HOST
    port_db = settings.DB_PORT
    user_db = settings.DB_USER
    pass_db = settings.DB_PASSWORD
    name_db = settings.DB_NAME

    for i in range(5):
        try:
            db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="contralog_pool",
                pool_size=5,
                host=host_db,
                port=port_db,
                user=user_db,
                password=pass_db,
                database=name_db
            )
            print(f"✅ Conexión exitosa a la base de datos en {host_db}:{port_db}")
            return
        except Exception as e:
            print(f"❌ Intento {i+1}: Fallo en {host_db}:{port_db}. Detalle: {e}")
            time.sleep(3)

# Inicializamos el pool al cargar el módulo
inicializar_pool()

def get_db_connection():
    if db_pool is None:
        # Re-intentamos inicializar si por alguna razón está vacío
        inicializar_pool()
        if db_pool is None:
            raise Exception("El pool de conexiones no está inicializado.")
    return db_pool.get_connection()