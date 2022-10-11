import environs
from pydantic import BaseSettings


envs = environs.Env()
envs.read_env()

LOGGING_HANDLERS = (
    ["console"] if envs.str("PYTHON_ENV", "local") == "local" else ["json"]
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:%(name)s:%(process)d:%(lineno)d %(levelname)s %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": """
                asctime: %(asctime)s
                created: %(created)f
                filename: %(filename)s
                funcName: %(funcName)s
                levelname: %(levelname)s
                levelno: %(levelno)s
                lineno: %(lineno)d
                message: %(message)s
                module: %(module)s
                msec: %(msecs)d
                name: %(name)s
                pathname: %(pathname)s
                process: %(process)d
                processName: %(processName)s
                relativeCreated: %(relativeCreated)d
                thread: %(thread)d
                threadName: %(threadName)s
                exc_info: %(exc_info)s
            """,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "uvicorn": {"level": "CRITICAL"},
        "urllib3": {
            "level": "CRITICAL",
        },
        "asyncio": {
            "level": "WARNING",
        },
    },
    "root": {"level": "INFO", "handlers": LOGGING_HANDLERS},
}


class Settings(BaseSettings):
    JIRA_BASE_URL: str = envs.str("JIRA_BASE_URL")
    JIRA_USER: str = envs.str("JIRA_USER")
    JIRA_API_TOKEN: str = envs.str("JIRA_API_TOKEN")
    CELERY_BROKER_URL: str = "redis://redis:6379"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379"


settings = Settings()
