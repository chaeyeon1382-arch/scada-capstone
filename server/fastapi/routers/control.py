from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import RelayLog
import paho.mqtt.client as mqtt
import json
import os

router = APIRouter(prefix="/control", tags=["control"])

MQTT_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
MQTT_PORT = 1883
MQTT_USER = os.getenv("RABBITMQ_USER", "admin")
MQTT_PASS = os.getenv("RABBITMQ_PASS", "admin1234")


class RelayCommand(BaseModel):
    action: str


def publish_mqtt(topic: str, payload: dict):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.connect(MQTT_HOST, MQTT_PORT)
    client.publish(topic, json.dumps(payload))
    client.disconnect()


@router.post("/relay/{slave_id}")
def control_relay(slave_id: int, cmd: RelayCommand, db: Session = Depends(get_db)):
    payload = {
        "slave_id": slave_id,
        "command": {
            "target": "relay",
            "action": cmd.action
        }
    }
    publish_mqtt(f"scada/control/relay/{slave_id}/command", payload)

    log = RelayLog(slave_id=slave_id, target="relay", action=cmd.action)
    db.add(log)
    db.commit()

    return {"result": "ok", "slave_id": slave_id, "action": cmd.action}


@router.get("/relay/{slave_id}/logs")
def get_relay_logs(slave_id: int, limit: int = 100, db: Session = Depends(get_db)):
    result = db.query(RelayLog)\
               .filter(RelayLog.slave_id == slave_id)\
               .order_by(RelayLog.timestamp.desc())\
               .limit(limit)\
               .all()
    return result
