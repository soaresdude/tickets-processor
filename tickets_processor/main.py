from fastapi import FastAPI

from .routers import health, tickets

app = FastAPI()

app.include_router(health.router)
app.include_router(tickets.router)


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
