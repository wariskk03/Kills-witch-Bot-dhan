from config import session
from engine import run_killswitch_bot
from log_config import log_config

logger = log_config(__name__)

if __name__ == "__main__":
    try:
        run_killswitch_bot()
    except KeyboardInterrupt:
        logger.warning("\n👋 [EXIT] Interrupted by user.")
    finally:
        session.close()
        logger.critical("\n\n=====================================================\n")
        logger.info("\n\n=====================================================\n")
