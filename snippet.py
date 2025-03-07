from logger_config import general_logger, requests_logger, debug_logger
import random

def foo():
    requests_logger.info("Got request", extra={"user":"maintainer", "random": random.random()})

    # emulate super important actions
    m = random.randint(1, 6)
    debug_logger.debug(f"Request had number: {m}")
    a = 1 / 0

if __name__ == '__main__':
    general_logger.info("Script started.")
    try:
        foo()
    except Exception as e:
        general_logger.error(e, exc_info=True)
    general_logger.info("Script finished.")