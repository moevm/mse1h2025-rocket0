import logging

def foo(m: int, n: int) -> int:
    logging.debug('foo(%d, %d)', m, n)

    if m < 0 or n < 0:
        logging.error('values are less than zero (%d, %d)', m, n)

    return m * n

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    foo(5, 5)
    foo(-4, 5)
    foo(1, -4)
    foo(-3, -3)