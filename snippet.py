from logger_config import logger
import random

def foo():
    logger.info("Test", extra={"user":"maintainer", "random": random.random()})

if __name__ == '__main__':
    logger.debug("Script started.")
    foo()
    logger.debug("Script finished.")