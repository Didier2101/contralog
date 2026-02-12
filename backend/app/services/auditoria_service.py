from app.database import get_db_connection
import json

# Función que llamarás desde otros servicios (Contratos, Clientes, etc.)
def registrar_cambio_db(id_usuario: int, accion: str, tabla: str, id_registro: int, detalle: dict = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO auditoria_cambios 
            (id_usuario, accion, tabla_afectada, id_registro_afectado, detalle_cambio)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_usuario, accion, tabla, id_registro, json.dumps(detalle) if detalle else None))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# Función para el endpoint de consulta

def obtener_logs_auditoria_db(limit: int = 5):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT a.*, u.nombre as usuario_nombre 
            FROM auditoria_cambios a
            LEFT JOIN usuarios u ON a.id_usuario = u.id_usuario
            ORDER BY a.fecha_cambio DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        logs = cursor.fetchall()
        
        # --- EL TRUCO ESTÁ AQUÍ ---
        for log in logs:
            # Si el detalle es un texto (string), lo convertimos a diccionario
            if log['detalle_cambio'] and isinstance(log['detalle_cambio'], str):
                try:
                    log['detalle_cambio'] = json.loads(log['detalle_cambio'])
                except:
                    log['detalle_cambio'] = {} # Si falla el parseo, enviamos vacío
            elif log['detalle_cambio'] is None:
                log['detalle_cambio'] = {}
        # --------------------------

        return logs
    finally:
        cursor.close()
        conn.close()