from app.database import get_db_connection
from app.models.contrato import ContratoJuridicoCreate, ContratoNaturalCreate
from app.utils.file_manager import validar_y_guardar_pdf
from datetime import datetime, timedelta # Para manejar fechas y vencimientos
from app.core.errors import RegistroNoEncontrado # Para la excepción del detalle
from app.services.auditoria_service import registrar_cambio_db
from app.utils.codigos import generar_codigo_contrato, generar_codigo_documento
from fastapi import UploadFile

async def crear_contrato_natural_db(contrato: ContratoNaturalCreate, archivo: UploadFile):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    codigo_cnt = generar_codigo_contrato()
    
    try:
        # 1. Insertar contrato natural
        query = """
            INSERT INTO contratos_naturales (codigo_unico, id_cliente, fecha_inicio, fecha_final, nda_firmado, estado, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (codigo_cnt, contrato.id_cliente, contrato.fecha_inicio, contrato.fecha_final, contrato.nda_firmado, contrato.estado.value, contrato.creado_por))
        id_contrato = cursor.lastrowid

        # 2. Guardar el PDF en la tabla de documentos
        ruta = await validar_y_guardar_pdf(archivo, "naturales")
        cod_doc = generar_codigo_documento()
        
        query_doc = "INSERT INTO contrato_documentos (codigo_seguimiento, id_contrato_n, id_tipo_doc, s3_key) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_doc, (cod_doc, id_contrato, 1, ruta)) # 1 = Contrato Principal

        conn.commit()
        
        # Auditoría
        registrar_cambio_db(contrato.creado_por, "CREATE", "contratos_naturales", id_contrato, {"codigo": codigo_cnt})
        
        return {"id": id_contrato, "codigo": codigo_cnt, "mensaje": "Contrato Natural Creado"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

async def crear_contrato_juridico_db(contrato: ContratoJuridicoCreate, principal: UploadFile, polizas: list, tipos_poliza: list):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    codigo_cnt = generar_codigo_contrato() # CNT-2026-XXXX
    
    try:
        # 1. Insertar en contratos_juridicos
        query_jur = """
            INSERT INTO contratos_juridicos (codigo_unico, id_cliente, fecha_inicio, fecha_final, estado, creado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_jur, (codigo_cnt, contrato.id_cliente, contrato.fecha_inicio, contrato.fecha_final, contrato.estado.value, contrato.creado_por))
        id_contrato = cursor.lastrowid

        # 2. Insertar Documento Principal (ID_TIPO = 1)
        ruta_p = await validar_y_guardar_pdf(principal, "juridicos")
        cod_doc_p = generar_codigo_documento() # DOC-2026-YYYY
        
        query_doc = "INSERT INTO contrato_documentos (codigo_seguimiento, id_contrato_j, id_tipo_doc, s3_key) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_doc, (cod_doc_p, id_contrato, 1, ruta_p))

        # 3. Insertar Pólizas Adicionales
        if polizas and tipos_poliza:
            for i, archivo_poliza in enumerate(polizas):
                ruta_pol = await validar_y_guardar_pdf(archivo_poliza, "polizas")
                cod_pol = generar_codigo_documento()
                # Usamos el ID de tipo que viene del formulario
                cursor.execute(query_doc, (cod_pol, id_contrato, tipos_poliza[i], ruta_pol))

        conn.commit()
        return {"codigo": codigo_cnt, "mensaje": "Contrato y documentos creados con éxito"}
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
# --- LISTADO GENERAL (UNION) ---
def obtener_todos_contratos_db(limit: int = 20, skip: int = 0):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                cn.codigo_unico AS contrato_codigo, 
                cl.codigo_unico AS cliente_codigo, 
                cl.nombre_o_razon_social AS cliente_nombre, 
                cn.fecha_inicio, 
                cn.fecha_final, 
                cn.estado, 
                'natural' AS tipo_contrato 
            FROM contratos_naturales cn
            JOIN clientes cl ON cn.id_cliente = cl.id_cliente
            
            UNION ALL
            
            SELECT 
                cj.codigo_unico AS contrato_codigo, 
                cl.codigo_unico AS cliente_codigo, 
                cl.nombre_o_razon_social AS cliente_nombre, 
                cj.fecha_inicio, 
                cj.fecha_final, 
                cj.estado, 
                'juridico' AS tipo_contrato 
            FROM contratos_juridicos cj
            JOIN clientes cl ON cj.id_cliente = cl.id_cliente
            
            ORDER BY fecha_inicio DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, skip))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

# --- DETALLE POR ID ---
def obtener_contrato_por_codigo_db(codigo_unico: str, tipo: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. Definir tabla según el tipo
        tabla = "contratos_naturales" if tipo == "natural" else "contratos_juridicos"
        id_col = "id_contrato_n" if tipo == "natural" else "id_contrato_j"
        
        # 2. Consultar los datos básicos del contrato
        query_contrato = f"""
            SELECT con.*, cli.nombre_o_razon_social AS cliente_nombre, usu.nombre AS creador_nombre
            FROM {tabla} con
            JOIN clientes cli ON con.id_cliente = cli.id_cliente
            LEFT JOIN usuarios usu ON con.creado_por = usu.id_usuario
            WHERE con.codigo_unico = %s
        """
        cursor.execute(query_contrato, (codigo_unico,))
        contrato = cursor.fetchone()

        if not contrato:
            raise RegistroNoEncontrado(f"Contrato {tipo}", codigo_unico)

        # 3. Consultar los documentos asociados a este contrato
        # Usamos el ID interno que acabamos de obtener para buscar los archivos
        id_interno = contrato[id_col]
        fk_col = "id_contrato_n" if tipo == "natural" else "id_contrato_j"

        query_docs = f"""
            SELECT cd.codigo_seguimiento, td.nombre AS tipo_documento, cd.s3_key, cd.fecha_subida
            FROM contrato_documentos cd
            JOIN tipo_documentos td ON cd.id_tipo_doc = td.id_tipo
            WHERE cd.{fk_col} = %s
        """
        cursor.execute(query_docs, (id_interno,))
        documentos = cursor.fetchall()

        # 4. Unificar todo en un solo resultado
        contrato["documentos"] = documentos
        
        print(f"--- Detalle Contrato {codigo_unico} ---")
        print(f"Documentos encontrados: {len(documentos)}")

        # imprimir todo lo que viene en un print para verificar
        print(f"Contrato: {contrato}")
        for doc in documentos:
            print(f"Documento: {doc}")

        return contrato

    finally:
        cursor.close()
        connection.close()



def verificar_vencimientos_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    hoy = datetime.now().date()
    proximos_15_dias = hoy + timedelta(days=15)
    
    try:
        # 1. Marcar como 'vencido' los que ya pasaron la fecha final
        query_vencidos = "UPDATE {tabla} SET estado = 'vencido' WHERE fecha_final < %s AND estado != 'vencido'"
        
        # 2. Marcar como 'por_vencer' los que vencen en los próximos 15 días
        query_por_vencer = "UPDATE {tabla} SET estado = 'por_vencer' WHERE fecha_final BETWEEN %s AND %s AND estado = 'activo'"

        for tabla in ["contratos_naturales", "contratos_juridicos"]:
            # Ejecutar vencidos
            cursor.execute(query_vencidos.format(tabla=tabla), (hoy,))
            # Ejecutar próximos a vencer
            cursor.execute(query_por_vencer.format(tabla=tabla), (hoy, proximos_15_dias))
        
        connection.commit()
        print(f"[{datetime.now()}] Auditoría de vencimientos completada exitosamente.")
    except Exception as e:
        print(f"Error en la verificación nocturna: {e}")
    finally:
        cursor.close()
        connection.close()


def obtener_alertas_vencimiento_db():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Traemos contratos naturales y jurídicos que estén 'por_vencer'
        query = """
            SELECT id_contrato_n AS id, 'natural' AS tipo, fecha_final, cl.nombre_o_razon_social
            FROM contratos_naturales cn
            JOIN clientes cl ON cn.id_cliente = cl.id_cliente
            WHERE cn.estado = 'por_vencer'
            UNION ALL
            SELECT id_contrato_j AS id, 'juridico' AS tipo, fecha_final, cl.nombre_o_razon_social
            FROM contratos_juridicos cj
            JOIN clientes cl ON cj.id_cliente = cl.id_cliente
            WHERE cj.estado = 'por_vencer'
            ORDER BY fecha_final ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()