from typing import Callable, Dict
from importlib import import_module
from ..Logs.logging_setup import app_logger as logger


def load_handlers(handler_config: Dict[str, str]) -> Dict[str, Callable]:
    handlers = {}
    for task_type, handler_path in handler_config.items():
        try:
            module_name, func_name = handler_path.rsplit(".", 1)
            module = import_module(module_name)
            handler = getattr(module, func_name)
            handlers[task_type] = handler
            logger.info(f'Loaded handler for {task_type}: {handler_path}')
        except (ImportError, AttributeError) as e:
            logger.error(f'Failed to load handler {handler_path} for {task_type}: {e}')
    return handlers
