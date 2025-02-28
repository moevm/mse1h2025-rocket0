import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def foo(m: int, n: int) -> int:
    logger.debug('foo(%d, %d)', m, n)

    if m < 0 or n < 0:
        logger.error('values are less than zero (%d, %d)', m, n)

    return m * n

if __name__ == '__main__':
    handler = logging.FileHandler(f"{__name__}.log", mode='w')
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    foo(5, 5)
    foo(-4, 5)
    foo(1, -4)
    foo(-3, -3)