# mqtt_client.py, modbus_client.py, security.py를 불러와서 실행하는 메인 루프
# JSON형식으로 포장


import time
from datetime import datetime
#from modbus_client import SensorReader
from security import SecurityEngine
from mqtt_client import MQTTClientManager
from modbus_client import ModbusClientManager


# 시뮬레이션 모드 플래그 (하드웨어 -> False)
SIMULATION_MODE = False



# 설정값
SENSOR_ID = 2
RELAY_ID = 1
CLOUD_IP = "34.47.100.119"

def main():
    # Modbus 매니저 먼저 생성
    modbus = ModbusClientManager(port='/dev/ttyUSB0')
    
    # MQTT 매니저 생성 시 modbus 객체를 넘겨줌 (서버 명령 수행을 위해)
    mqtt_mg = MQTTClientManager(reader=modbus, host=CLOUD_IP)


    security = SecurityEngine(threshold=30.0)


    # 시뮬레이션 모드가 아닐 때만 실제 연결 시도
    if not SIMULATION_MODE:
        if not modbus.connect():
            print("❌ Modbus 연결 실패. 프로그램을 종료합니다.")
            return
    
    mqtt_mg.connect()
    time.sleep(2) # 연결 안정화 대기
    #mqtt_mg.loop_start()

    try:
        while True:
            if SIMULATION_MODE:
                # 테스트용 가짜 데이터 (서버가 원하는 형식인지 확인용)
                temp, hum = 26.5, 58.2
                print(f"🧪 [시뮬레이션] 데이터 생성: {temp}°C, {hum}%")
            else:
                # 실제 하드웨어 데이터 읽기
                data = modbus.read_sensor_data(slave_id=SENSOR_ID)
                if data:
                    temp, hum = data[0]/10, data[1]/10
                else:
                    continue


            payload = {"data": {"temperature": temp, "humidity": hum}}
            result = security.analyze(payload)
            print(f"🔒 보안 상태: {result['status']}")        

            mqtt_mg.publish_sensor(slave_id=SENSOR_ID, temp=temp, hum=hum)
            time.sleep(5)

    except KeyboardInterrupt:
        mqtt_mg.disconnect()
        modbus.close()

if __name__ == "__main__":
    main()



    """
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

