# Примеры логирования

## Дополнительные поля + несколько логеров
```python
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
```

### Консоль
```json lines
{"timestamp": "2025-03-07 22:21:19,554", "name": "general", "level": "INFO", "msg": "Script started."}
{"timestamp": "2025-03-07 22:21:19,554", "name": "debug", "level": "DEBUG", "msg": "Request had number: 6"}
{"timestamp": "2025-03-07 22:21:19,554", "name": "general", "level": "ERROR", "msg": "division by zero", "exc_info": "Traceback (most recent call last):\n  File \"C:\\Users\\wwwod\\PycharmProjects\\mse1h2025-rocket0\\snippet.py\", line 15, in <module>\n    foo()\n    ~~~^^\n  File \"C:\\Users\\wwwod\\PycharmProjects\\mse1h2025-rocket0\\snippet.py\", line 10, in foo\n    a = 1 / 0\n        ~~^~~\nZeroDivisionError: division by zero"}
{"timestamp": "2025-03-07 22:21:19,556", "name": "general", "level": "INFO", "msg": "Script finished."}
```

### Файл requests.log
```json
{"timestamp": "2025-03-07 22:21:19,554", "name": "requests", "level": "INFO", "msg": "Got request", "user": "maintainer", "random": 0.7549071001025663}
```