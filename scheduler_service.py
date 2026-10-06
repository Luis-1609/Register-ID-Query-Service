import time
import logging
from datetime import datetime
from functions_main import procesar_registro_sheets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Scheduler")

START_HOUR = 7
END_HOUR = 21

def run_scheduler():
    logger.info("Scheduler de Register-ID iniciado. Monitoreando Google Sheets cada 5 segundos...")
    while True:
        try:
            now = datetime.now()
            if START_HOUR <= now.hour < END_HOUR:
                procesar_registro_sheets()
                time.sleep(5)
            else:
                logger.debug(f"Fuera de horario ({now.strftime('%H:%M')}). Durmiendo...")
                time.sleep(1800)
        except Exception as e:
            logger.error(f"Error en ciclo del scheduler: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_scheduler()
