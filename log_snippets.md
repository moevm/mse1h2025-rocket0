# Примеры логирования

## exception в plain-формате
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

## info, error в plain-формате
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

## json-формат с дополнительными полями
```python
from logger_config import logger
import random

def foo():
    logger.info("Test", extra={"user":"maintainer", "random": random.random()})

if __name__ == '__main__':
    logger.debug("Script started.")
    foo()
    logger.debug("Script finished.")
```

### Консоль
```json
{"timestamp": "2025-03-07 21:44:07,043", "name": "mse1h2025-rocket0", "level": "INFO", "msg": "Test", "user": "maintainer", "random": 0.8825765114447546}
```

### Файл
```json lines
{"timestamp": "2025-03-07 21:44:07,043", "name": "mse1h2025-rocket0", "level": "DEBUG", "msg": "Script started."}
{"timestamp": "2025-03-07 21:44:07,043", "name": "mse1h2025-rocket0", "level": "INFO", "msg": "Test", "user": "maintainer", "random": 0.8825765114447546}
{"timestamp": "2025-03-07 21:44:07,044", "name": "mse1h2025-rocket0", "level": "DEBUG", "msg": "Script finished."}
```