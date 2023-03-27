from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import here, testmongo, events
from app.mqtt import mqtt

app = FastAPI()

# Connect to MQTT broker

mqtt.init_app(app)

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(here.router, prefix="/here", tags=["here"])
app.include_router(testmongo.router, prefix="/testmongo", tags=["testmongo"])
app.include_router(events.router, prefix="/events", tags=["events"])
