from fastapi import FastAPI
from routers import sensor, control
from database import Base, engine
from mqtt_client import start_mqtt

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SCADA API Server")

app.include_router(sensor.router)
app.include_router(control.router)


@app.on_event("startup")
def startup():
    start_mqtt()


@app.get("/")
def root():
    return {"status": "ok", "message": "SCADA API is running"}