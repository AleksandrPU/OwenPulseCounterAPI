from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Owen Pulse Counter API"}


@app.get("/counters/{name}")
async def say_hello(name: str):
    # return {"message": owen_counter.read(name)}
    pass
