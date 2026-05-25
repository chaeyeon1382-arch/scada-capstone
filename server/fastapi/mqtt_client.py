import json
import os
import time
import paho.mqtt.client as mqtt
from database import SessionLocal
from models import SensorData

MQTT_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
MQTT_PORT = 1883
MQTT_USER = os.getenv("RABBITMQ_USER", "admin")
MQTT_PASS = os.getenv("RABBITMQ_PASS", "admin1234")


def on_connect(client, userdata, flags, rc, properties):
    print(f"MQTT 연결 완료: {rc}")
    client.subscribe("scada/sensor/+/data")


def on_message(client, userdata, msg):
    db = SessionLocal()
    try:
        payload = json.loads(msg.payload.decode())
        record = SensorData(
            slave_id=payload["slave_id"],
            temperature=payload.get("temperature") or payload.get("data", {}).get("temperature"),
            humidity=payload.get("humidity") or payload.get("data", {}).get("humidity"),
            status=payload.get("status", "NORMAL"),
            received_at=payload.get("received_at")
        )
        db.add(record)
        db.commit()
    except Exception as e:
        print(f"처리 실패: {e}")
        db.rollback()
    finally:
        db.close()


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message

    for i in range(10):
        try:
            client.connect(MQTT_HOST, MQTT_PORT)
            client.loop_start()
            return
        except Exception:
            print(f"MQTT 연결 재시도 중... ({i+1}/10)")
            time.sleep(3)

    print("MQTT 연결 실패")