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
                print(f"▶︎[시뮬레이션] 데이터 생성: {temp}°C, {hum}%")
            else:
                # 실제 하드웨어 데이터 읽기
                data = modbus.read_sensor_data(slave_id=SENSOR_ID)
                if data:
                    t1 = datetime.now()  # 센서 데이터 받은 시간
                    hum, temp= data[0]/10, data[1]/10
                    print(f"⏱ [GW 수신 시간] {t1.strftime('%H:%M:%S.%f')[:-3]}")
                else:
                    continue


            payload = {
                "data": {"temperature": temp, "humidity": hum}, "t3": int(time.time() * 1000)
                }
            result = security.analyze(payload)
            status = result['status']
            print(f"🔒 보안 상태: {result['status']}")        

            mqtt_mg.publish_sensor(slave_id=SENSOR_ID, temp=temp, hum=hum, status=status)
            time.sleep(0.2)

    except KeyboardInterrupt:
        mqtt_mg.disconnect()
        modbus.close()

if __name__ == "__main__":
    main()



