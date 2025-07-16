from engine import run_killswitch_bot
from config import session
from log_config import log_config

path = "/Users/wariskhan/Python Algo/dhanhq_api/Killswitch_bot/logs.log"

logger = log_config(__name__, path)

if __name__ == "__main__":
    try:
        run_killswitch_bot()
    except KeyboardInterrupt:
        logger.info("\n👋 [EXIT] Interrupted by user.")
    finally:
        session.close()
        logger.critical("\n\n=====================================================\n")
