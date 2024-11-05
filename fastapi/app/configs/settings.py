from pydantic import AnyHttpUrl, field_validator
from typing import List, Union
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NAVER_REDIRECT_URI: str

    PROJECT_NAME: str = "Modular-RAG"
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    ALLOWED_HOSTS: List[AnyHttpUrl] = ["http://localhost"]

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ACCESS_TOKEN_PREEMPTIVE_REFRESH_MINUTES: int = 5

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def LOGGING(self):
        log_dir = "/code/logs" if os.getenv("ENVIRONMENT") == "production" else "logs"
        os.makedirs(log_dir, exist_ok=True)

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "access_file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": os.path.join(log_dir, "access.log"),
                },
                "error_file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": os.path.join(log_dir, "error.log"),
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["error_file"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access_file"],
                    "level": "INFO",
                    "propagate": False,
                },
                "app": {
                    "handlers": ["console", "access_file", "error_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            "root": {
                "level": "WARNING",
                "handlers": [
                    "console",
                ],
            },
        }

    @field_validator("ALLOWED_HOSTS")
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        case_sensitive = True
        # env_file = ".env"


settings = Settings()
