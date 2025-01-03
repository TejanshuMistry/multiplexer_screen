from fastapi import FastAPI
import sockets

app = FastAPI()

app.include_router(sockets.router)

@app.get("/")
async def ping():
    return {"Message": "Pong"}

