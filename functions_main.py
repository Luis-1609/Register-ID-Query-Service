import os
import logging
from functions_sheets import (
    get_valid_creds, 
    get_sheets_api, 
    get_sheet_values, 
    update_sheet_values, 
    format_cell_bold_center
)
from service import ejecutar_registro_id

logger = logging.getLogger("RegisterService.main")

def cargar_env():
    for env_path in [".env", os.path.join(os.path.dirname(__file__), ".env")]:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
            break

cargar_env()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
# Por defecto lee la pestaña 'Register-ID-Query-Service' si no se especifica otra en el .env
HOJA_NOMBRE = os.getenv("SHEET_NAME", "Register-ID-Query-Service")

def obtener_rango(rango: str) -> str:
    if HOJA_NOMBRE:
        return f"'{HOJA_NOMBRE}'!{rango}"
    return rango

def procesar_registro_sheets():
    """
    Función principal que consulta el Sheet, detecta si se solicitó un registro en I12,
    valida los inputs, ejecuta Playwright (service.py) y escribe el ID generado en I12.
    """
    if not SPREADSHEET_ID:
        logger.error("SPREADSHEET_ID no configurado en .env.")
        return

    sheets = get_sheets_api(get_valid_creds())

    # 1. Leer el estado del disparador en I12 de la pestaña 'Register-ID-Query-Service'
    estado_actual = get_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"))
    valor_estado = estado_actual[0][0].strip().upper() if estado_actual and estado_actual[0] else ""

    # Solo procesamos si el usuario presionó el botón (que escribe PENDIENTE, REGISTRAR o EJECUTAR en I12)
    TRIGGERS = ["PENDIENTE", "REGISTRAR", "EJECUTAR", "CONSULTAR", "SI"]
    if valor_estado not in TRIGGERS:
        return

    logger.info(f"Trigger detectado en I12 ('{valor_estado}'). Iniciando proceso...")

    # 2. Poner inmediatamente en I12: 'Procesando...' para dar feedback visual
    update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [["Procesando..."]])

    try:
        # 3. Leer Nombre Solicitud (B1)
        val_nombre_sol = get_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("B1"))
        nombre_solicitud = val_nombre_sol[0][0].strip() if val_nombre_sol and val_nombre_sol[0] else "STOCK PRUEBA"

        # 4. Leer Categoría (I3)
        val_categoria = get_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J3"))
        categoria = val_categoria[0][0].strip() if val_categoria and val_categoria[0] else "MAT_INFORMATICO"

        # 5. Leer Chartfields (J6:J10) -> Unidad, Actividad, Sede, Ref Ppto, Línea
        val_chartfields = get_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J6:J10"))
        
        unidad = val_chartfields[0][0].strip() if len(val_chartfields) > 0 and val_chartfields[0] else ""
        actividad = val_chartfields[1][0].strip() if len(val_chartfields) > 1 and val_chartfields[1] else ""
        sede = val_chartfields[2][0].strip() if len(val_chartfields) > 2 and val_chartfields[2] else ""
        ref_ppto = val_chartfields[3][0].strip() if len(val_chartfields) > 3 and val_chartfields[3] else ""
        linea_accion = val_chartfields[4][0].strip() if len(val_chartfields) > 4 and val_chartfields[4] else ""

        # 6. Leer Tabla de Items (B4:F25)
        # B: Descripción, C: Cantidad, D: Precio, E: Total (fórmula), F: Proveedor
        val_items = get_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("B4:G25"))
        items = []
        for fila in val_items:
            if not fila or not fila[0].strip():
                continue
            desc = fila[0].strip()
            cant = int(fila[1]) if len(fila) > 1 and str(fila[1]).isdigit() else 1
            precio = str(fila[2]).strip() if len(fila) > 2 else "0,00"
            prov = str(fila[4]).strip() if len(fila) > 4 else ""
            #categoria_linea = str(fila[5]).strip() if len(fila) > 5 else ""

            #REVISAR
            cat_raw = str(fila[5]).strip() if len(fila) > 5 else ""
            categoria_final = cat_raw if (cat_raw and cat_raw != "-") else categoria

            items.append({
                "descripcion": desc,
                "cantidad": cant,
                "precio": precio,
                "nombre_corto_proveedor": prov,
                #"categoria_linea": categoria_linea
                "categoria_linea": categoria_final #REVISAR
            })

        # 7. VALIDACIONES DE DATOS
        if not unidad or not actividad or not ref_ppto or not linea_accion:
            logger.error("Error: Faltan valores obligatorios en los Chartfields (J6:J10).")
            update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [["Error: Chartfields incompletos"]])
            return

        if len(items) == 0:
            logger.error("Error: No hay items ingresados en la tabla B4:G25.")
            update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [["Error: Sin items"]])
            return

        chartfield_dict = {
            "unidad": unidad,
            "actividad": actividad,
            "sede": sede,
            "ref_ppto": ref_ppto,
            "linea_accion": linea_accion
        }

        logger.info(f"Datos validados con éxito. Solicitud: '{nombre_solicitud}', Categoría: '{categoria}', Items: {len(items)}")

        # 8. Ejecutar la lógica de Playwright validada en service.py
        resultado = ejecutar_registro_id(
            items=items,
            categoria=categoria,
            nombre_solicitud=nombre_solicitud,
            chartfield=chartfield_dict
        )

        req_id = resultado.get("numero_req_id", "")
        if req_id and resultado.get("status") == "COMPLETADO":
            # Forzar formato exacto de 10 dígitos con ceros a la izquierda (ej: '0000875160)
            # El apóstrofe al inicio le indica a Google Sheets que lo guarde como TEXTO puro sin truncar ceros
            req_id_formateado = f"'{str(req_id).strip().zfill(10)}"
            logger.info(f"Requerimiento generado exitosamente: {req_id_formateado}")
            update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [[req_id_formateado]])
            # Forzar estilo Negrita y Centrado en la celda J12 (Fila 12, Columna J)
            format_cell_bold_center(sheets, SPREADSHEET_ID, HOJA_NOMBRE, row_idx=11, col_idx=9)
        else:
            logger.error(f"Fallo en creación de requerimiento: {resultado}")
            update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [["Error en registro"]])

    except Exception as e:
        logger.error(f"Excepción durante el proceso: {str(e)}", exc_info=True)
        update_sheet_values(sheets, SPREADSHEET_ID, obtener_rango("J12"), [["Error: Falló automatización"]])
