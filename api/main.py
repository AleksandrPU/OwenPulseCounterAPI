import asyncio

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from owen_poller.exeptions import DeviceNotFound
from owen_poller.owen_poller import SensorsPoller
from owen_poller.sender import PcsPerMinSender

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

poller = SensorsPoller()
readings_sender = PcsPerMinSender(poller)


@app.on_event('startup')
async def app_startup():
    asyncio.create_task(poller.poll())
    asyncio.create_task(readings_sender.send_readings())


@app.get("/")
async def root():
    return {"message": "Owen Pulse Counter API"}


@app.get("/sensors/{name}")
async def get_sensor_readings(name: str):
    try:
        return poller.get_sensor_readings(name)
    except DeviceNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=err.args[0])

# @app.get("/counters")
# async def get_all_devices():
#     return {
#         dev: {param_names[param]: value for param, value in params.items()}
#         for dev, params in poller.get_all().items()
#     }
