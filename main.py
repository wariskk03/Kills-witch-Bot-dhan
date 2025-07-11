from engine import run_killswitch_bot
from config import session

if __name__ == "__main__":
    try:
        run_killswitch_bot()
    except KeyboardInterrupt:
        print("\n👋 [EXIT] Interrupted by user.")
    finally:
        session.close()
