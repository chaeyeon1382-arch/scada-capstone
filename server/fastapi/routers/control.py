from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import RelayLog
import paho.mqtt.client as mqtt
import json
import os
import time

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
    
    # 백그라운드 네트워킹 배송 엔진 가동
    client.loop_start() 
    
    # 데이터 전송 및 확실하게 갈 때까지 대기
    msg_info = client.publish(topic, json.dumps(payload))
    msg_info.wait_for_publish() 
    
    # 데이터가 전선망을 완전히 빠져나갈 때까지 0.2초 대기
    time.sleep(0.2)

    # 전송 완료 후 엔진 정지 및 안전하게 연결 종료
    client.loop_stop() 
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
