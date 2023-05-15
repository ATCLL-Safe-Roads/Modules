from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.mqtt import mqtt
from app.routers import events, flows, graphs

app = FastAPI()
mqtt.init_app(app)


def custom_openapi():
    return get_openapi(
        title='ATCLL - Safe Roads - API Module',
        version='1.0.0',
        routes=app.routes,
    )


# API Documentation
app.openapi = custom_openapi

# API CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# API Routes
app.include_router(events.router, prefix='/events', tags=['events'])
app.include_router(flows.router, prefix='/flows', tags=['flows'])
app.include_router(graphs.router, prefix='/graphs', tags=['graphs'])
