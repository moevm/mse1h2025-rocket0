# Примеры логирования

## exception
```python
from logger_config import logger

def foo():
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Ошибка", exc_info=True)

if __name__ == '__main__':
    foo()
```

### Вывод
```
2025-03-07 21:24:38,931 - mse1h2025-rocket0 - ERROR - Ошибка
Traceback (most recent call last):
  File "C:\Users\wwwod\PycharmProjects\mse1h2025-rocket0\snippet.py", line 5, in foo
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

## info, error
```python
from logger_config import logger
import random

def foo():
    logger.info("Test")
    if random.randint(0, 2) == 1:
        logger.error("You have a lucky error")

if __name__ == '__main__':
    logger.debug("Script started.")
    foo()
    logger.debug("Script finished.")
```

### Консоль
```
2025-03-07 21:29:20,056 - mse1h2025-rocket0 - INFO - Test
2025-03-07 21:29:20,056 - mse1h2025-rocket0 - ERROR - You have a lucky error
```

### Файл
```
2025-03-07 21:29:20,055 - mse1h2025-rocket0 - DEBUG - Script started.
2025-03-07 21:29:20,056 - mse1h2025-rocket0 - INFO - Test
2025-03-07 21:29:20,056 - mse1h2025-rocket0 - ERROR - You have a lucky error
2025-03-07 21:29:20,056 - mse1h2025-rocket0 - DEBUG - Script finished.
```