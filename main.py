import logging
from functions_main import procesar_registro_sheets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("RegisterService")

def main():
    logger.info("Ejecutando verificación manual de Google Sheets...")
    procesar_registro_sheets()

if __name__ == "__main__":
    main()