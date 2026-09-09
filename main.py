import os
import re
from playwright.sync_api import Playwright, sync_playwright, expect

def cargar_env(ruta_env=".env"):
    if os.path.exists(ruta_env):
        with open(ruta_env, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                # Ignorar líneas vacías y comentarios
                if linea and not linea.startswith("#"):
                    if "=" in linea:
                        clave, valor = linea.split("=", 1)
                        # Limpiar espacios y comillas
                        clave = clave.strip()
                        valor = valor.strip().strip('"').strip("'")
                        os.environ[clave] = valor
# Cargamos el archivo .env que está en el mismo directorio
cargar_env()
# Ahora puedes obtener las credenciales de forma segura
USUARIO = os.getenv("TEST_USERNAME")
PASSWORD = os.getenv("TEST_PASSWORD")
# Chartflied cargado desde el .env
UNIDAD = os.getenv("TEST_UNIDAD")
ACTIVIDAD = os.getenv("TEST_ACTIVIDAD")
REF_PPTO = os.getenv("TEST_REF_PPTO")
SEDE = os.getenv("TEST_SEDE")
LINEA_ACCION = os.getenv("TEST_LINEA_ACCION")


def run(playwright: Playwright) -> None:
    ###
    #Items de prueba, luego se reemplazará por datos extraidos del sheets
    """
    items = [
        {   
            "descripcion": "Tapa Ciega Blanco PANDUIT CMBIW-X",
            "cantidad": 10,
            "precio"  : "2,71",
            "nombre_corto_proveedor" : "MULTIMPORT-001"
        },
        {
            "descripcion": "Conector RJ45",
            "cantidad": 82,
            "precio"  : "42,36",
            "nombre_corto_proveedor" : "ESQUIVELC-001"
        },
        {
            "descripcion": "Cinta Adhesiva",
            "cantidad": 50,
            "precio"  : "5,93",
            "nombre_corto_proveedor" : "CORPORACIO-102"
        }
    ]
    """
    items = [
        {   
            "descripcion": "SET26 Servicio internet móvil 30GB por modem (6set26-5oct26) - Fondo de conectividad",
            "cantidad": 1,
            "precio"  : "11246,40",
            "nombre_corto_proveedor" : ""
        },
        {
            "descripcion": "OCT26 Servicio internet móvil 30GB por modem (6oct26-5nov26) - Fondo de conectividad",
            "cantidad": 1,
            "precio"  : "11246,40",
            "nombre_corto_proveedor" : ""
        },
        {
            "descripcion": "NOV26 Servicio internet móvil 30GB por modem (6nov26-5dic26) - Fondo de conectividad",
            "cantidad": 1,
            "precio"  : "11246,40",
            "nombre_corto_proveedor" : ""
        },
        {
            "descripcion": "DIC26 Servicio internet móvil 30GB por modem (6dic26-5ene27) - Fondo de conectividad",
            "cantidad": 1,
            "precio"  : "11246,40",
            "nombre_corto_proveedor" : ""
        }
    ]
    ###

    CATEGORIA = "INTERNET_LINEA" #Cambiar cuando sea necesario, MAT_INFORMATICO, por ejemplo
    NOMBRE_SOLICITUD = "Fondo conectividad" #cambiar a "STOCK PRUEBA" cuando sea necesario.
    browser = playwright.chromium.launch(headless=False,slow_mo = 500)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://centuria.pucp.edu.pe/")
    ## LOGIN
    page.locator("span").nth(1).click()
    page.locator("span").nth(3).click()
    page.get_by_role("textbox", name="Ingrese su usuario").click()
    page.get_by_role("textbox", name="Ingrese su usuario").fill(USUARIO)
    page.get_by_role("textbox", name="Ingrese su contraseña aquí").click()
    page.get_by_role("textbox", name="Ingrese su contraseña aquí").fill(PASSWORD)
    page.get_by_role("button", name="INGRESAR").click()

    ## Acaba el Login 


    page.get_by_text("Menú Principal : Menú Bú").click()
    page.locator("#CO_EMPLOYEE_SELF_SERVICE > .pthnavrightarrow").click()
    page.locator("#EPAM_PROCUREMENT > .pthnavrightarrow").click()
    page.locator("#crefli_EP_PV_REQ_ENTRY_GBL").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Unidad Negocio").click()
    page.locator("iframe[name=\"ptModFrame_0\"]").content_frame.get_by_role("link", name="PO001").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Acep").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").press("CapsLock")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").fill(NOMBRE_SOLICITUD)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Solicitud:").press("CapsLock")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Expandir Sección Valores p/").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("radio", name="Sustituir").check()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").press("CapsLock")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").fill(CATEGORIA)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Categoría:").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consulta Categoría").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Unidad Medida:").fill("UND")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").fill(SEDE)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"OPERATING_UNIT$0\"]").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Sede").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("input[name=\"DEPTID$0\"]").fill(UNIDAD)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("input[name=\"DEPTID$0\"]").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Unidad", exact=True).press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"BUDGET_REF$0\"]").fill(REF_PPTO)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"BUDGET_REF$0\"]").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Consultar Ref Ppto").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"PRODUCT$0\"]").fill(ACTIVIDAD)
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"PRODUCT$0\"]").press("Tab")
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"tdREQ_DFLT_DISTRB$0#10\"]").get_by_role("button", name="Consultar Actividad").press("Tab")
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
    page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"CHARTFIELD1$0\"]").fill(LINEA_ACCION)


    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Contin").click()
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("link", name="Artículo Especial").click()
    for i in range(len(items)):
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Descripción Artículo:").click()
        #page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Descripción Artículo:").press("ControlOrMeta+V")
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Descripción Artículo:").fill(items[i]['descripcion'])
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Precio:").click()
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Precio:").fill(str(items[i]['precio']))
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Cantidad:").click()
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Cantidad:").fill(str(items[i]['cantidad']))
        if items[i]['nombre_corto_proveedor'] != "":
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Búsqueda Proveedor").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Corto Proveedor:").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("textbox", name="Nombre Corto Proveedor:").fill(str(items[i]['nombre_corto_proveedor']))
            page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Buscar").click()
            page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("[id=\"VENDOR_ID$0\"]").click()
        page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Añadir Art").click()

    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("cell", name="Revisión y Presentación").nth(3).click()

    # Guardamos y creamos el ID
    page.locator("iframe[name=\"TargetContent\"]").content_frame.get_by_role("button", name="Guardar y Enviar").click()
    
    # Luego de haber creado el ID, lo capturamos y guardamos en una variable
    numero_req_id = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_HDR_REQ_ID").inner_text()
    print(numero_req_id)
    # Capturamos tambien el monto total del ID
    monto_total_id = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_PNLS_WRK_REQ_AMT_TTL").inner_text()
    print(monto_total_id)

    # Capturamos la moneda
    moneda = page.locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_PNLS_WRK_CURRENCY_CD2").inner_text()
    print(moneda)
    
    # Guardamos el ID y el monto total en una variable
    request_info = {
        "numero_req_id": numero_req_id,
        "monto_total_id": monto_total_id,
        "moneda": moneda
    }
    print(request_info)
    #while(True) :
    #print(request_info["numero_req_id"], " - ", request_info["monto_total_id"], " - ", request_info["moneda"])

        
    #locator("iframe[name=\"TargetContent\"]").content_frame.locator("#win0divREQ_HDR_REQ_ID") ## CAPTURAR ESTO, RECUADRO DONDE ESTA EL ID


    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)