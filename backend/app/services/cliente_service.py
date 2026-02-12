from app.database import get_db_connection
from app.models.cliente import ClienteCreate, ClienteUpdate
from app.core.errors import RegistroNoEncontrado, DatosDuplicados, ErrorOperacion
from app.services.auditoria_service import registrar_cambio_db
from app.utils.codigos import generar_codigo_cliente

import mysql.connector

def crear_cliente_db(cliente: ClienteCreate, id_usuario_operador: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    codigo_nuevo = generar_codigo_cliente()
    try:
        query = """
            INSERT INTO clientes (tipo_persona, tipo_identificacion, identificacion, 
            nombre_o_razon_social, codigo_unico, telefono, email_contacto, activo, creado_por) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            cliente.tipo_persona.value, cliente.tipo_identificacion.value,
            cliente.identificacion, cliente.nombre_o_razon_social,
            codigo_nuevo, cliente.telefono, cliente.email_contacto, 
            cliente.activo, id_usuario_operador  # <--- Usamos el ID validado por el Token
        )
        cursor.execute(query, valores)
        id_generado = cursor.lastrowid
        connection.commit()

        # Registro de Auditoría usando el ID del operador
        registrar_cambio_db(
            id_usuario=id_usuario_operador,
            accion="CREATE",
            tabla="clientes",
            id_registro=id_generado,
            detalle={
                "mensaje": f"Cliente creado: {cliente.nombre_o_razon_social}", 
                "identificacion": cliente.identificacion, 
                "codigo_unico": codigo_nuevo
            }
        )

        return {"id_cliente": id_generado, "mensaje": "Cliente creado exitosamente"}
    except mysql.connector.Error as err:
        connection.rollback()
        if err.errno == 1062:
            raise DatosDuplicados("La identificación o correo ya están registrados.")
        raise ErrorOperacion("Fallo al registrar el cliente.")
    finally:
        cursor.close()
        connection.close()
def obtener_clientes_db(skip: int = 0, limit: int = 10):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Consulta ligera: Solo tabla clientes
        query = "SELECT id_cliente, codigo_unico, tipo_persona, tipo_identificacion, nombre_o_razon_social, identificacion, telefono, activo, fecha_creacion FROM clientes LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, skip))
        clientes = cursor.fetchall()
        return clientes if clientes else [] 
    finally:
        cursor.close()
        connection.close()

def obtener_cliente_por_codigo_db(codigo_unico: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. Obtener datos básicos del cliente
        # Buscamos por codigo_unico, pero traemos el id_cliente para las subconsultas
        query_cliente = """
            SELECT c.*, u.nombre AS nombre_creador 
            FROM clientes c 
            LEFT JOIN usuarios u ON c.creado_por = u.id_usuario 
            WHERE c.codigo_unico = %s
        """
        cursor.execute(query_cliente, (codigo_unico,))
        cliente = cursor.fetchone()
        
        if not cliente:
            return None

        id_cli = cliente['id_cliente']

        # 2. Traer solo los códigos de los contratos naturales
        cursor.execute("SELECT codigo_unico FROM contratos_naturales WHERE id_cliente = %s", (id_cli,))
        # Extraemos solo el string del código para que sea una lista simple: ["CNT-N1", "CNT-N2"]
        cliente['contratos_naturales'] = [row['codigo_unico'] for row in cursor.fetchall()]

        # 3. Traer solo los códigos de los contratos jurídicos
        cursor.execute("SELECT codigo_unico FROM contratos_juridicos WHERE id_cliente = %s", (id_cli,))
        cliente['contratos_juridicos'] = [row['codigo_unico'] for row in cursor.fetchall()]

        return cliente

    finally:
        cursor.close()
        connection.close()




def actualizar_cliente_db(codigo_unico: str, cliente_data: ClienteUpdate, id_usuario_operador: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. Obtener ID interno para la auditoría y verificar existencia
        cursor.execute("SELECT id_cliente FROM clientes WHERE codigo_unico = %s", (codigo_unico,))
        cliente = cursor.fetchone()
        if not cliente:
            raise RegistroNoEncontrado("Cliente", codigo_unico)
        
        id_interno = cliente['id_cliente']

        # 2. Preparar campos para actualizar
        # Usamos model_dump para Pydantic v2 (o .dict() en v1)
        campos = cliente_data.model_dump(exclude_unset=True)
        if not campos:
            raise ErrorOperacion("No se enviaron datos para actualizar.")

        set_query = ", ".join([f"{c} = %s" for c in campos.keys()])
        valores = list(campos.values())
        valores.append(codigo_unico) # Para el WHERE

        # 3. Ejecutar actualización
        query = f"UPDATE clientes SET {set_query} WHERE codigo_unico = %s"
        cursor.execute(query, valores)
        connection.commit()

        # 4. Registro de Auditoría
        registrar_cambio_db(
            id_usuario=id_usuario_operador,
            accion="UPDATE",
            tabla="clientes",
            id_registro=id_interno, # Seguimos auditando con el ID numérico
            detalle={"codigo": codigo_unico, "cambios": campos}
        )
        
        return {"mensaje": f"Cliente {codigo_unico} actualizado con éxito"}

    except mysql.connector.Error as err:
        connection.rollback()
        if err.errno == 1062:
            raise DatosDuplicados("Los datos entran en conflicto con un registro existente (Identificación duplicada).")
        raise ErrorOperacion(f"Error interno: {str(err)}")
    finally:
        cursor.close()
        connection.close()


def cambiar_estado_cliente_db(codigo_unico: str, nuevo_estado: bool, id_usuario_operador: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. Obtener ID interno
        cursor.execute("SELECT id_cliente FROM clientes WHERE codigo_unico = %s", (codigo_unico,))
        cliente = cursor.fetchone()
        if not cliente:
            raise RegistroNoEncontrado("Cliente", codigo_unico)
        
        id_interno = cliente['id_cliente']

        # 2. Actualizar estado por código único
        query = "UPDATE clientes SET activo = %s WHERE codigo_unico = %s"
        cursor.execute(query, (nuevo_estado, codigo_unico))
        connection.commit()

        # 3. Auditoría
        accion_auditoria = "ACTIVAR" if nuevo_estado else "DESACTIVAR"
        registrar_cambio_db(
            id_usuario=id_usuario_operador,
            accion=accion_auditoria,
            tabla="clientes",
            id_registro=id_interno,
            detalle={"codigo": codigo_unico, "estado": "activo" if nuevo_estado else "inactivo"}
        )

        return {"mensaje": f"Cliente {codigo_unico} {'activado' if nuevo_estado else 'desactivado'} con éxito"}
    
    except mysql.connector.Error as err:
        connection.rollback()
        raise ErrorOperacion(f"No se pudo cambiar el estado: {str(err)}")
    finally:
        cursor.close()
        connection.close()