import asyncio

from fastapi import FastAPI

app = FastAPI()


async def get_fibonacci(n: int) -> int:
    await asyncio.sleep(0)
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return await get_fibonacci(n - 1) + await get_fibonacci(n - 2)


@app.get("/liveness")
async def liveness():
    return "ok"


@app.get("/readiness")
async def readiness():
    return "ok"


@app.get("/fibonacci")
async def fibonacci(n: int):
    return await get_fibonacci(n)
