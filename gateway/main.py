# mqtt_client.py, modbus_client.py, security.py를 불러와서 실행하는 메인 루프
# JSON형식으로 포장


import time
from datetime import datetime
#from modbus_client import SensorReader
from security import SecurityEngine
from mqtt_client import MQTTManager
from modbus_client import ModbusClientManager


# 설정값
SENSOR_ID = 1
RELAY_ID = 2
CLOUD_IP = "34.47.100.119"

def main():
    # Modbus 매니저 먼저 생성
    modbus = ModbusClientManager(port='/dev/ttyUSB0')
    
    # MQTT 매니저 생성 시 modbus 객체를 넘겨줌 (서버 명령 수행을 위해)
    mqtt_mg = MQTTManager(reader=modbus, host=CLOUD_IP)

    if not modbus.connect():
        print("Modbus 연결 실패")
        return
    
    if not mqtt_mg.connect():
        print("MQTT 서버 연결 실패")
        return

    print("SCADA 시스템 가동 및 원격 제어 대기 중...")

    try:
        while True:
            # 센서 데이터 수집
            sensor_values = modbus.read_sensor_data(slave_id=SENSOR_ID)
            
            if sensor_values:
                temp = sensor_values[0] / 10.0
                humi = sensor_values[1] / 10.0
                
                # 클라우드로 전송할 패키지
                payload = {
                    "slave_id":SENSOR_ID,
                    "temperature": temp,
                    "humidity": humi,
                    "timestamp": time.time()
                }
                mqtt_mg.publish_sensor(payload)
            
            time.sleep(5) # 5초 간격으로 보고

    except KeyboardInterrupt:
        print("\n종료 중...")
    finally:
        modbus.close()
        mqtt_mg.disconnect()

if __name__ == "__main__":
    main()



"""
def main():
    SLAVE_ID = 1 # 현재 게이트웨이가 담당하는 기기 ID
    reader = SensorReader(slave_id=SLAVE_ID)             # 실제 기기의 하드웨어 주소
    security = SecurityEngine(threshold=80.0)
    mqtt = MQTTManager(reader=reader, host="127.0.0.1", port=1883)      # 라즈베리파이 연결 시에는 host를 노트북의 IP로 변경(라즈베리파이로부터 데이터 받기 위함)
    
    mqtt.connect()
    print("🚀 SCADA 게이트웨이 구동 시작...")

    try:
        while True:
            # 1. 센서 데이터 읽기, modbus_client.py에서 값 읽어옴
            raw_values = reader.read_data()
            
            # 2. JSON 형식 구성
            sensor_payload = {
                "slave_id": SLAVE_ID,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "data": raw_values
            }
            
            # 3. 보안 분석 및 상태 추가
            final_payload = security.analyze(sensor_payload)
            
            # 4. 약속된 토픽으로 전송
            mqtt.publish_sensor(SLAVE_ID, final_payload)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n 프로그램을 종료합니다.")

if __name__ == "__main__":
    main()

"""

