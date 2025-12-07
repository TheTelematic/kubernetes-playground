from fastapi import FastAPI

app = FastAPI()


@app.get("/liveness")
async def liveness():
    return "ok"


@app.get("/readiness")
async def readiness():
    return "ok"
