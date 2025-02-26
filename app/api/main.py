import asyncio
import logging
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.config import settings
from app.dummy.sender import DummyPcsPerMinSender
from app.owen_poller.exeptions import DeviceNotFound
from app.owen_poller.owen_poller import SensorsPoller
from app.owen_poller.sender import PcsPerMinSender

logger = logging.getLogger(__name__)
application = FastAPI()

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

poller = SensorsPoller()
if settings.poller_active:
    if settings.dummy:
        readings_sender = DummyPcsPerMinSender(poller)
    else:
        readings_sender = PcsPerMinSender(poller)


@application.on_event('startup')
async def app_startup():
    asyncio.create_task(poller.poll())
    if settings.poller_active:
        asyncio.create_task(readings_sender.send_readings())


@application.get("/")
async def root():
    return {"message": "Owen Pulse Counter API"}


@application.get("/sensors/")
async def get_some_sensor_readings(work_centers: str):
    work_centers = work_centers.split(',')
    logger.info(f"Getting readings for {work_centers}")
    response = []
    for work_center in work_centers:
        try:
            reading = poller.get_sensor_readings(work_center)
            reading['status'] = 'OK'
        except DeviceNotFound:
            reading = {
                'name': work_center,
                'reading': None,
                'reading_time': datetime.now(),
                'status': 'Not Found',
            }
            logger.error(f'Device {work_center} not found in settings.py')
        response.append(reading)
    logger.info(f"{response=}")
    return response


@application.get("/sensors/{name}")
async def get_sensor_readings(name: str):
    try:
        logger.info(f"Getting readings for {name}")
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
