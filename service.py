import os
import logging
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

logger = logging.getLogger("RegisterService")

def ejecutar_registro_id(
    items: List[Dict[str, Any]], 
    categoria: str = "MAT_INFORMÁTICO", 
    nombre_solicitud: str = "Solicitud automatizada",
    chartfield: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Ejecuta el flujo de creación de requerimiento en Centuria usando Playwright (Headless en Docker).
    Los valores de chartfield (Unidad, Actividad, Sede, Ref Ppto, Línea) y la Categoría provienen del Sheet.
    """
    if chartfield is None:
        chartfield = {}

    # Credenciales fijas de login (del .env)
    usuario = (os.getenv("TEST_USERNAME") or "").strip().strip('"').strip("'")
    password = (os.getenv("TEST_PASSWORD") or "").strip().strip('"').strip("'")

    # Valores dinámicos del Chartfield (prioridad al Sheet, fallback al .env si viniera vacío)
    # Se añade zfill() para asegurar que los ceros a la izquierda perdidos en Sheets se restauren.
    unidad = str(chartfield.get("unidad") or os.getenv("TEST_UNIDAD", "")).strip().strip('"').strip("'").zfill(5)
    actividad = str(chartfield.get("actividad") or os.getenv("TEST_ACTIVIDAD", "")).strip().strip('"').strip("'")
    sede = str(chartfield.get("sede") or os.getenv("TEST_SEDE", "")).strip().strip('"').strip("'").zfill(3)
    ref_ppto = str(chartfield.get("ref_ppto") or os.getenv("TEST_REF_PPTO", "")).strip().strip('"').strip("'").zfill(4)
    linea_accion = str(chartfield.get("linea_accion") or os.getenv("TEST_LINEA_ACCION", "")).strip().strip('"').strip("'")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            slow_mo=100, # Da tiempo a que las animaciones y menús de Centuria abran correctamente
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            logger.info("Navegando a https://centuria.pucp.edu.pe/ ...")
            page.goto("https://centuria.pucp.edu.pe/")
            
            ## LOGIN
            logger.info("Seleccionando el sistema CENTURIA Finanzas...")
            page.get_by_text("Elija uno de los sistemas CENTURIA").first.click(force=True)
            #page.wait_for_timeout(1000)
            page.get_by_text("Centuria Finanzas", exact=True).click(force=True)
            #page.wait_for_timeout(1000)
            
            logger.info(f"Ingresando usuario '{usuario}'...")
            page.get_by_role("textbox", name="Ingrese su usuario").click(force=True)
            page.get_by_role("textbox", name="Ingrese su usuario").fill(usuario, force=True)
            
            logger.info("Ingresando contraseña...")
            page.get_by_role("textbox", name="Ingrese su contraseña aquí").click(force=True)
            page.get_by_role("textbox", name="Ingrese su contraseña aquí").fill(password, force=True)
            
            logger.info("Presionando botón INGRESAR...")
            page.get_by_role("button", name="INGRESAR").click(force=True)
            
            logger.info("Esperando carga tras el login...")
            #page.wait_for_timeout(4000)
            #page.screenshot(path="debug_login.png")

            ## NAVEGACIÓN
            logger.info("Haciendo clic en 'Menú Principal : Menú Bú'...")
            page.get_by_text("Menú Principal : Menú Bú").click(force=True)
            ##page.wait_for_timeout(1000)
            #page.screenshot(path="debug_menu1.png")
            
            logger.info("Navegando: CO_EMPLOYEE_SELF_SERVICE > EPAM_PROCUREMENT > crefli_EP_PV_REQ_ENTRY_GBL")
            page.locator("#CO_EMPLOYEE_SELF_SERVICE > .pthnavrightarrow").click(force=True)
            ##page.wait_for_timeout(1000)
            #page.screenshot(path="debug_menu2.png")
            
            page.locator("#EPAM_PROCUREMENT > .pthnavrightarrow").click(force=True)
            ##page.wait_for_timeout(1000)
            #page.screenshot(path="debug_menu3.png")
            
            page.locator("#crefli_EP_PV_REQ_ENTRY_GBL").click(force=True)
            ##page.wait_for_timeout(2000)
            
            logger.info("Consultar Unidad Negocio...")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Unidad Negocio").click()
            page.locator("iframe[name=\"ptModFrame_0\"]").content_frame.get_by_role("link", name="PO001").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Acep").click()
            
            logger.info(f"Llenando Nombre Solicitud: {nombre_solicitud}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").press("CapsLock")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").fill(nombre_solicitud)
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").press("CapsLock")
            
            logger.info("Expandir Sección Valores p/ y seleccionar Sustituir")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Expandir Sección Valores p/").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("radio", name="Sustituir").check()
            
            #PROBANDO - REVISAR
            #logger.info(f"Llenando Categoría: {categoria}")
            #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").click()
            #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").press("CapsLock")
            #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").fill(categoria)
            #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").press("Tab")
            #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consulta Categoría").press("Tab")
            
            logger.info("Llenando Unidad Medida...")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Unidad Medida:").fill("UND")
            
            logger.info(f"Llenando Sede: {sede}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").fill(str(sede))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Sede").press("Tab")
            
            logger.info(f"Llenando Unidad (DEPTID): {unidad}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("input[name=\"DEPTID$0\"]").fill(str(unidad))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("input[name=\"DEPTID$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Unidad", exact=True).press("Tab")
            
            logger.info(f"Llenando Ref Ppto: {ref_ppto}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"BUDGET_REF$0\"]").fill(str(ref_ppto))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"BUDGET_REF$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Ref Ppto").press("Tab")
            
            logger.info(f"Llenando Actividad (PRODUCT): {actividad}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"PRODUCT$0\"]").fill(str(actividad))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"PRODUCT$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"tdREQ_DFLT_DISTRB$0#10\"]").get_by_role("button", name="Consultar Actividad").press("Tab")
            
            logger.info("Tabulando por campos restantes...")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"BUSINESS_UNIT_PC$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar UniNeg PC").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"PROJECT_ID$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Proy").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"ACTIVITY_ID$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"ACTIVITY_ID$prompt$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"RESOURCE_TYPE$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Tp Origen").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"RESOURCE_CATEGORY$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Categ").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"RESOURCE_SUB_CAT$0\"]").press("Tab")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Subcat").press("Tab")
            
            logger.info(f"Llenando Línea Acción (CHARTFIELD1): {linea_accion}")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"CHARTFIELD1$0\"]").fill(str(linea_accion))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"CHARTFIELD1$0\"]").press("Tab")
            ##page.wait_for_timeout(1000)
            #page.screenshot(path="debug_pre_contin.png")

            logger.info("Continuar y seleccionar Artículo Especial...")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Contin").click(force=True)
            ##page.wait_for_timeout(2000)
            #page.screenshot(path="debug_post_contin.png")
            
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_text("Artículo Especial").first.click(force=True)
            ##page.wait_for_timeout(1000)

            ## LLENADO DE ITEMS
            logger.info(f"Empezando iteración de {len(items)} items...")
            for i in range(len(items)):
                desc = items[i].get('descripcion', '')
                precio = str(items[i].get('precio', ''))
                cantidad = str(items[i].get('cantidad', ''))
                prov = items[i].get('nombre_corto_proveedor', '')
                categoria_linea = items[i].get('categoria_linea', '')
                
                logger.info(f"Procesando item {i+1}: {desc}, {cantidad} UND a {precio}, prov: {prov}, categoria_linea: {categoria_linea}")
                
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Descripción Artículo:").click()
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Descripción Artículo:").fill(desc)
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Precio:").click()
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Precio:").fill(precio)
                if categoria_linea != "" and categoria_linea != "-":
                    logger.info(f"Buscando categoria_linea {categoria_linea} para item {i+1}...")
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").click()
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").dblclick()
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").fill(categoria_linea)
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").press("Tab")
                    #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consulta Categoría").click()
                    #page.locator("iframe[name=\"ptModFrame_1\"]").content_frame.locator("#PV_SR_CATLU_WRK_CATEGORY_CD").click()
                    #page.locator("iframe[name=\"ptModFrame_1\"]").content_frame.locator("#PV_SR_CATLU_WRK_CATEGORY_CD").fill(categoria_linea)
                    #page.locator("iframe[name=\"ptModFrame_1\"]").content_frame.get_by_role("button", name="Buscar", description="Buscar Categoría").click()
                    #page.locator("iframe[name=\"ptModFrame_1\"]").content_frame.get_by_role("link", name=categoria_linea).click()
                
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Cantidad:").click()
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Cantidad:").fill(cantidad)
                
                if prov != "":
                    logger.info(f"Buscando proveedor {prov} para item {i+1}...")
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Búsqueda Proveedor").click()
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Corto Proveedor:").click()
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Corto Proveedor:").fill(str(prov))
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Buscar").click()
                    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"VENDOR_ID$0\"]").click()
                
                
                
                # SS debug: campos del item listos antes de añadir
                page.screenshot(path=f"/app/logs/ss_item_{i+1}_a_campos_listos.png", full_page=True)

                logger.info(f"Añadiendo artículo {i+1} a la lista...")
                page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Añadir Art").click()

                # SS debug: resultado después de añadir el item
                page.screenshot(path=f"/app/logs/ss_item_{i+1}_b_despues_anadir.png", full_page=True)

            logger.info("Clic en Revisión y Presentación...")
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("cell", name="Revisión y Presentación").nth(3).click()

            logger.info("Guardando y Enviando...")
            page.screenshot(path="/app/logs/ss_01_antes_guardar.png", full_page=True)
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Guardar y Enviar").click()
            page.screenshot(path="/app/logs/ss_02_despues_guardar.png", full_page=True)

            logger.info("Esperando a que aparezca el ID de requerimiento...")
            page.wait_for_timeout(5000)
            page.screenshot(path="/app/logs/ss_03_esperando_5s.png", full_page=True)

            logger.info("Recopilando ID de requerimiento, monto y moneda...")
            numero_req_id = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_HDR_REQ_ID").inner_text().strip()
            monto_total_id = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_PNLS_WRK_REQ_AMT_TTL").inner_text().strip()
            moneda = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_PNLS_WRK_CURRENCY_CD2").inner_text().strip()

            logger.info(f"Éxito. Req ID: {numero_req_id} | Monto: {moneda} {monto_total_id}")
            return {
                "status": "COMPLETADO",
                "numero_req_id": numero_req_id,
                "monto_total_id": monto_total_id,
                "moneda": moneda
            }

        finally:
            context.close()
            browser.close()
