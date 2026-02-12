# app/services/auth_service.py

from app.database import get_db_connection
from datetime import datetime
from app.core.security import verificar_password
from app.core.errors import CredencialesInvalidas, RegistroNoEncontrado
import mysql.connector

def login_usuario_db(email, password):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. Buscar usuario activo
        query = "SELECT * FROM usuarios WHERE email = %s AND estado = 'activo'"
        cursor.execute(query, (email,))
        usuario = cursor.fetchone()

        # 2. Validación: Si no existe o la clave no coincide, lanzamos error de negocio
        if not usuario or not verificar_password(password, usuario['password']):
            raise CredencialesInvalidas()

        # 3. Registrar sesión y último ingreso
        ahora = datetime.now()
        cursor.execute("INSERT INTO sesiones (id_usuario, fecha_ingreso) VALUES (%s, %s)", 
                       (usuario['id_usuario'], ahora))
        
        cursor.execute("UPDATE usuarios SET ultimo_ingreso = %s WHERE id_usuario = %s", 
                       (ahora, usuario['id_usuario']))
        
        connection.commit()
        
        usuario.pop('password') # Seguridad: nunca devolver el hash
        return usuario

    finally:
        cursor.close()
        connection.close()

def logout_usuario_db(id_usuario: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Buscamos sesión abierta
        query_buscar = """
            SELECT id_sesion, fecha_ingreso FROM sesiones 
            WHERE id_usuario = %s AND fecha_salida IS NULL 
            ORDER BY fecha_ingreso DESC LIMIT 1
        """
        cursor.execute(query_buscar, (id_usuario,))
        sesion = cursor.fetchone()

        if not sesion:
            # En logout, si no hay sesión, lanzamos error de negocio para avisar al front
            raise RegistroNoEncontrado("Sesión activa", id_usuario)

        ahora = datetime.now()
        duracion = int((ahora - sesion['fecha_ingreso']).total_seconds() / 60)
        
        cursor.execute("""
            UPDATE sesiones SET fecha_salida = %s, duracion_minutos = %s 
            WHERE id_sesion = %s
        """, (ahora, duracion, sesion['id_sesion']))
        
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()