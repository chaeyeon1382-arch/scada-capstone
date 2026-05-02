#RabbitMQ 연결 및 전송 담당
#RabbitMQ의 MQTT 플로그인과 대화하는 파일
#JSON 패키지를 도커 서버로 전송


import paho.mqtt.client as mqtt
import json
import time

class MQTTManager:
    def __init__(self, reader, host="127.0.0.1", port=1883):     # 구현 시 host 부분 수정하기 (라즈베리파이가 찾아가야 되는 노트북의 IP 주소로)
        self.reader = reader # 이제 여기서 modbus_client(reader)를 사용할 수 있음
        # 고유 ID 생성 및 클라이언트 초기화
        client_id = f"scada-gw-{int(time.time())}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.host = host
        self.port = port

        self.reader = reader
        
        # 로그인 정보 설정
        self.client.username_pw_set("admin", "admin1234")
        
        # 콜백 함수 연결 (이 부분이 에러의 원인이었습니다!)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("🟢 서버 연결 성공 (scada/control/relay/+/command 구독 중)")
            # 서버로부터 오는 릴레이 제어 명령 구독
            self.client.subscribe("scada/control/relay/+/command")
        else:
            print(f"🟡 연결 실패 (에러 코드: {rc})")

    # 연결이 끊겼을 때 실행되는 함수
    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties):
        print("🔴 서버와의 연결이 끊어졌습니다. 자동으로 재연결을 시도합니다...")


    # 서버에서 릴레이 제어 명령이 왔을 때 실행
    def on_message(self, client, userdata, msg):
        try:
            # 데이터 해석
            command_data = json.loads(msg.payload.decode()) # 서버가 보낸 JSON 패키지를 풂
            print(f"📥 [명령 수신] 내용: {command_data}")
            
            # 수신된 명령에 따라 실제 하드웨어(reader) 제어
            action = command_data.get("command", {}).get("action")

           # 릴레이 제어 (1개이므로 무조건 0번 고정)
            if action == "on":
                self.reader.write_coil(0, True) # 실제 하드웨어 0번 핀(또는 주소) 작동
                print("✅ 릴레이 ON")
            elif action == "off":
                self.reader.write_coil(0, False)
                print("✅ 릴레이 OFF")
            else:
                print(f"⚠️ 알 수 없는 명령: {action}")
                
        except Exception as e:
            print(f"❌ 명령 해석 오류: {e}")

    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start() # 백그라운드 루프 시작
        except Exception as e:
            print(f"❌ 초기 연결 실패: {e}")

    def publish_sensor(self, slave_id, data):
        if not self.client.is_connected():
            print("⚠️ 연결 끊김: 전송을 건너뜁니다.")
            return

        topic = f"scada/sensor/{slave_id}/data"
        payload = json.dumps(data)
        self.client.publish(topic, payload, qos=1)
        print(f"📤 데이터 전송 성공 [{topic}]")




