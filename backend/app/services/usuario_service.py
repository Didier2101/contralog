from app.database import get_db_connection
from app.core.security import obtener_password_hash
from app.models.usuario import UsuarioCreate
from app.core.errors import RegistroNoEncontrado, DatosDuplicados, ErrorOperacion
import mysql.connector
from app.services.auditoria_service import registrar_cambio_db

def crear_nuevo_usuario(usuario: UsuarioCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        password_hasheado = obtener_password_hash(str(usuario.password).strip())
        
        query = """
            INSERT INTO usuarios (nombre, email, password, rol, estado) 
            VALUES (%s, %s, %s, %s, 'activo')
        """
        valores = (usuario.nombre, usuario.email, password_hasheado, usuario.rol.value)
        cursor.execute(query, valores)
        id_generado = cursor.lastrowid
        conn.commit()
        # --- REGISTRO DE AUDITORÍA ---
        registrar_cambio_db(
            id_usuario=id_generado,
            accion="CREATE",
            tabla="usuarios",
            id_registro=id_generado,
            detalle={"mensaje": f"Usuario creado: {usuario.nombre}", "email": usuario.email}
        )
        
        return obtener_usuario_completo_db(cursor.lastrowid)

    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1062:
            raise DatosDuplicados(f"El email '{usuario.email}' ya está registrado.")
        raise ErrorOperacion("No se pudo crear el usuario en la base de datos.")
    finally:
        conn.close()

def obtener_usuarios_db(limit: int = 20, offset: int = 0):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id_usuario, nombre, email, rol, estado, ultimo_ingreso, created_at FROM usuarios ORDER BY created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        usuarios = cursor.fetchall()
        return usuarios if usuarios else []
    finally:
        conn.close()

def obtener_usuario_completo_db(id_usuario: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, email, rol, estado, ultimo_ingreso, created_at FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise RegistroNoEncontrado("Usuario", id_usuario)

        # Consultas adicionales (Auditoría, Sesiones, Clientes)
        cursor.execute("SELECT id_sesion, fecha_ingreso, fecha_salida, duracion_minutos FROM sesiones WHERE id_usuario = %s ORDER BY fecha_ingreso DESC LIMIT 5", (id_usuario,))
        usuario['historial_sesiones'] = cursor.fetchall()

        cursor.execute("SELECT id_log, accion, tabla_afectada, id_registro_afectado, detalle_cambio, fecha_cambio FROM auditoria_cambios WHERE id_usuario = %s ORDER BY fecha_cambio DESC LIMIT 10", (id_usuario,))
        usuario['actividad_auditoria'] = cursor.fetchall()

        cursor.execute("SELECT id_cliente, nombre_o_razon_social, identificacion, codigo_unico FROM clientes WHERE creado_por = %s", (id_usuario,))
        usuario['clientes_registrados'] = cursor.fetchall()

        return usuario
    finally:
        conn.close()

def actualizar_usuario_db(id_usuario: int, datos: dict, id_usuario_operador: int):
    conn = get_db_connection()
    try:
        # Primero validamos si existe
        obtener_usuario_completo_db(id_usuario)
        
        cursor = conn.cursor()
        campos = ", ".join([f"{k} = %s" for k in datos.keys()])
        valores = list(datos.values())
        valores.append(id_usuario)
        
        cursor.execute(f"UPDATE usuarios SET {campos} WHERE id_usuario = %s", valores)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise ErrorOperacion("No se realizaron cambios en el perfil.")
        # --- REGISTRO DE AUDITORÍA ---
        registrar_cambio_db(
            id_usuario=id_usuario_operador,
            accion="UPDATE",
            tabla="usuarios",
            id_registro_afectado=id_usuario,
            detalle={"campos_actualizados": list(datos.keys()), "datos": datos}
        )
            
        return obtener_usuario_completo_db(id_usuario)
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1062:
            raise DatosDuplicados("Ese email ya está siendo usado por otra cuenta.")
        raise ErrorOperacion("Error al actualizar la información del usuario.")
    finally:
        conn.close()

def cambiar_estado_usuario_db(id_usuario: int, nuevo_estado: str, id_admin: int):
    conn = get_db_connection()
    try:
        # Validamos existencia
        obtener_usuario_completo_db(id_usuario)
        
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET estado = %s WHERE id_usuario = %s", (nuevo_estado, id_usuario))
        conn.commit()

        registrar_cambio_db(
            id_usuario=id_admin,
            accion="UPDATE",
            tabla="usuarios",
            id_registro=id_usuario,
            detalle={"campo_actualizado": "estado", "nuevo_valor": nuevo_estado}
        )
        
        return obtener_usuario_completo_db(id_usuario)
    finally:
        conn.close()