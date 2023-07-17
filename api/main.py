import asyncio

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from owen_counter.owen_ci8 import OwenCI8
from owen_poller.exeptions import DeviceNotFound
from owen_poller.owen_poller import CountersPoller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

poller = CountersPoller()

param_names = {
    OwenCI8.DCNT: 'count',
    OwenCI8.DTMR: 'seconds',
    OwenCI8.DSPD: 'flow'
}


@app.on_event('startup')
async def app_startup():
    asyncio.create_task(poller.poll())


@app.get("/")
async def root():
    return {"message": "Owen Pulse Counter API"}


@app.get("/counters/{name}")
async def get_counter_values(name: str, response: Response):
    try:
        device_attrs = poller.get_params(name)
    except DeviceNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    return {param_names[param]: value for param, value in device_attrs.items()}
