import paho.mqtt.client as mqtt
import json
import time
import ssl
from datetime import datetime

class MQTTClientManager:
    def __init__(self, reader, host="34.47.100.119", port=8883):
        self.reader = reader
        client_id = f"scada-gw-{int(time.time())}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.host = host
        self.port = port

        # TLS 설정 - self-signed 인증서용
        self.client.tls_set(
            ca_certs="/home/chaeyeon1382/scada-capstone/server/rabbitmq/certs/ca.crt",
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_NONE,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        self.client.tls_insecure_set(True)
        self.client.username_pw_set("admin", "admin1234")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("🟢 서버 연결 성공 [TLS]")
            self.client.subscribe("scada/control/relay/+/command")
        else:
            print(f"🟡 연결 실패 (에러 코드: {rc})")

    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties):
        print("🔴 연결이 끊어졌습니다.")

    def on_message(self, client, userdata, msg):
        print(f"📥 RAW 데이터 수신: {msg.topic} -> {msg.payload}")
        try:
            command_data = json.loads(msg.payload.decode())
            slave_id = command_data.get("slave_id")
            action = command_data.get("command", {}).get("action")
            if action == "on":
                self.reader.control_fan(True, slave_id=slave_id)
            elif action == "off":
                self.reader.control_fan(False, slave_id=slave_id)
        except Exception as e:
            print(f"❌ 명령 해석 오류: {e}")

    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ 초기 연결 실패: {e}")
            return False

    def publish_sensor(self, slave_id, temp, hum, status="NORMAL"):
        if not self.client.is_connected():
            print("⚠️ 연결 끊김")
            return
        payload = {
            "slave_id": slave_id,
            "temperature": temp,
            "humidity": hum,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "received_at": datetime.now().timestamp(),
            "status": status
        }
        topic = f"scada/sensor/{slave_id}/data"
        self.client.publish(topic, json.dumps(payload), qos=1)
        print(f"📤 데이터 전송 성공 [TLS]: {topic} -> {payload}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
