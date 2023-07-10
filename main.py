import asyncio

from fastapi import FastAPI

from owen_poller.owen_poller import CountersPoller

app = FastAPI()
poller = CountersPoller()


@app.on_event('startup')
async def app_startup():
    asyncio.create_task(poller.poll())


@app.get("/")
async def root():
    return {"message": "Owen Pulse Counter API"}


@app.get("/counters/{name}")
async def say_hello(name: str):
    # return {"message": owen_counter.read(name)}
    pass
