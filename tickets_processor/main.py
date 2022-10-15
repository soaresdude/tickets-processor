import logging.config

from fastapi import FastAPI

from core.config import LOGGING
from .routers import health, tickets, charts


logging.config.dictConfig(LOGGING)

app = FastAPI()

app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(charts.router)
