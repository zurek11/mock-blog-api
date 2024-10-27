import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve(strict=True).parent
    print(BASE_DIR)
    BASE_URL: str = 'http://localhost:8000'
    DEBUG: bool = False
    print(DEBUG)
    print(type(DEBUG))
    ENVIRONMENT: str = 'development'
    ALLOWED_HOSTS: str = '*'

    # Postgresql DB
    DATABASE_NAME: str = 'mock_blog_api'
    DATABASE_HOST: str = 'localhost'
    DATABASE_PASSWORD: str = 'postgres'
    DATABASE_PORT: str = '5432'
    DATABASE_USER: str = 'postgres'
    DATABASE_POOL_SIZE: int = 5

    # Sentry SDK
    SENTRY_DSN: Optional[str] = None

    # Logging
    LOGS: dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
        },
        "handlers": {
            "console": {
                "level": 'DEBUG',
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "logfile": {
                "level": 'INFO',
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/api.log",
                "maxBytes": 10*1024*1024,  # 10MB
                "backupCount": 3,
                "mode": "a",
            }
        },
        "root": {
            'level': 'INFO',
            'handlers': ['console', 'logfile']
        },
        'loggers': {
            "api": {
                'level': 'DEBUG',
                'handlers': ['console', 'logfile'],
                'propagate': False
            },
        },
    }

    class Config:
        env_file = ".env"


settings = Settings()
dictConfig(settings.LOGS)
logger = logging.getLogger('api')
