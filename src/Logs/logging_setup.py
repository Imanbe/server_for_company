import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Логгер для пользовательских сообщений (только наши логи)
    app_logger = logging.getLogger('carex_app')
    app_logger.setLevel(logging.INFO)
    app_logger.handlers.clear()  # Очищаем обработчики

    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Обработчик для файла только с нашими логами
    app_file_handler = RotatingFileHandler(
        'Logs/carex_main.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(formatter)

    # Добавляем обработчик к app_logger
    app_logger.addHandler(app_file_handler)
    app_logger.propagate = False  # Изолируем от корневого логгера

    debug_logger = logging.getLogger("carex_debug")
    debug_logger.setLevel(logging.DEBUG)
    debug_logger.handlers.clear()

    # Обработчик для подробного файла
    debug_file_handler = RotatingFileHandler(
        "Logs/carex_debug.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)

    # Добавляем обработчик к debug_logger
    debug_logger.addHandler(debug_file_handler)
    debug_logger.propagate = False  # Изолируем от корневого логгера

    # Настройка корневого логгера (для сторонних библиотек)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень для сторонних библиотек
    root_logger.handlers.clear()  # Очищаем стандартные обработчики
    root_logger.addHandler(debug_file_handler)  # Перенаправляем все в debug лог

    return app_logger, debug_logger


app_logger, debug_logger = setup_logging()
