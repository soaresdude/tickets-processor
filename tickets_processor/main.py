import logging.config

from fastapi import FastAPI

from core.config import LOGGING
from .routers import health, tickets


logging.config.dictConfig(LOGGING)

app = FastAPI()

app.include_router(health.router)
app.include_router(tickets.router)
