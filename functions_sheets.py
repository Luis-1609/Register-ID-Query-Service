import os
import logging
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger("RegisterService.sheets")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_valid_creds(credentials_file="credentials.json", token_file="token.json"):
    """
    Obtiene credenciales válidas de OAuth 2.0.
    Si token.json existe, lo usa y refresca si ha expirado.
    Si no existe, inicia el flujo OAuth para generar el token.
    """
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            logger.warning(f"Error leyendo {token_file}: {e}. Se solicitará nueva autorización.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refrescando token OAuth expirado...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"No se encontró el archivo de credenciales: {credentials_file}")
            
            logger.info("Iniciando flujo de autorización OAuth 2.0...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            
            is_docker = os.path.exists("/.dockerenv")
            if is_docker:
                logger.info("Ejecutando en Docker. Iniciando servidor OAuth en puerto 8080...")
                creds = flow.run_local_server(host="localhost", bind_addr="0.0.0.0", port=8080, open_browser=False)
            else:
                creds = flow.run_local_server(port=0)

        # Guardar el token para las siguientes ejecuciones
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
        logger.info(f"Token OAuth guardado correctamente en {token_file}")

    return creds

def get_sheets_api(creds):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()

def get_sheet_values(sheets, spreadsheet_id, address, retries=3):
    for intento in range(retries):
        try:
            result = sheets.values().get(spreadsheetId=spreadsheet_id, range=address).execute()
            return result.get("values", [])
        except Exception as e:
            logger.warning(f"Error al leer rango {address} (intento {intento+1}/{retries}): {e}")
            if intento == retries - 1:
                raise
            time.sleep(2)

def update_sheet_values(sheets, spreadsheet_id, address, values, retries=3):
    for intento in range(retries):
        try:
            body = {"values": values}
            sheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=address,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return
        except Exception as e:
            logger.warning(f"Error al actualizar rango {address} (intento {intento+1}/{retries}): {e}")
            if intento == retries - 1:
                raise
            time.sleep(2)

def get_sheet_id(sheets, spreadsheet_id, sheet_name):
    """Obtiene el sheetId numérico de una pestaña por su nombre."""
    try:
        metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
        for s in metadata.get("sheets", []):
            if s.get("properties", {}).get("title") == sheet_name:
                return s["properties"]["sheetId"]
    except Exception as e:
        logger.warning(f"Error buscando sheetId para '{sheet_name}': {e}")
    return 0

def format_cell_bold_center(sheets, spreadsheet_id, sheet_name, row_idx=11, col_idx=8):
    """
    Aplica estilo Negrita, Centrado Horizontal y Centrado Vertical a una celda específica.
    row_idx=11 (Fila 12, 0-indexed), col_idx=8 (Columna I, 0-indexed).
    """
    try:
        sheet_id = get_sheet_id(sheets, spreadsheet_id, sheet_name)
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row_idx,
                            "endRowIndex": row_idx + 1,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True,
                                    "fontSize": 10
                                },
                                "horizontalAlignment": "CENTER",
                                "verticalAlignment": "MIDDLE"
                            }
                        },
                        "fields": "userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)"
                    }
                }
            ]
        }
        sheets.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        logger.info("Formato (Negrita + Centrado) aplicado a la celda I12 con éxito.")
    except Exception as e:
        logger.warning(f"No se pudo aplicar formato visual a la celda: {e}")
