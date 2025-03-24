from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Task(BaseModel):
    task_type: str
    payload: dict


class User(BaseModel):
    user_name: str
    is_excluded: bool


class Settings(BaseSettings):
    REDIS_URL: str = "redis://:Password@localhost:6379/0"
    TECH_ACCOUNT: str = "1111"
    TASKS: str = "task_random_queue"
    TASKS_ERROR: str = "task_random_error_queue"
    WEBHOOK_CAREX: str = 'https://bitrix24.ru/rest/111111/secret_key/'

    HANDLERS: dict[str, str] = {
        'process_carex_random': 'handlers.process_carex_random'
    }

    USERS: dict[str, User] = {
        '0': {"user_name": "Michaele J.", "is_excluded": False},
        '1': {"user_name": "John S.", "is_excluded": False},
        '2': {"user_name": "Elon M.", "is_excluded": False},
        '3': {"user_name": "Jeff B.", "is_excluded": False},
        '4': {"user_name": "Steve J.", "is_excluded": False},
        '5': {"user_name": "Lebron J.", "is_excluded": False},
    }

    class Config:
        env_file = ".env"


settings = Settings()
