# 센서 데이터 읽기 담당

# modbus_client.py
from pymodbus.client import ModbusSerialClient
import threading

lock = threading.Lock()

class ModbusClientManager:
    def __init__(self, port='/dev/ttyUSB0'): # 본인의 포트 경로 확인 필수
        self.client = ModbusSerialClient(
            port=port,
            baudrate=9600,     # 제품 기본 전송 속도 
            parity='N',        
            stopbits=1,        
            bytesize=8,        
            timeout=1
        )

    def connect(self):
        return self.client.connect()

    # 센서 데이터 읽기 (ID: 2, 주소 0번부터 2개 <- 장치 매뉴얼 확인하기)
    def read_sensor_data(self, slave_id=2):
        with lock:
            response = self.client.read_holding_registers(0, count=2, device_id=slave_id)
            if not response.isError():
                print(f"📊 raw 값: {response.registers}")
                return response.registers
            return None

    # FAN 제어 (ID: 1, Channel: 0)
    def control_fan(self, is_on, slave_id=1):
        with lock:
            response = self.client.write_coil(0, is_on, device_id=slave_id)
            return not response.isError()


    def close(self):
        self.client.close()



"""
import random

class SensorReader:
    def __init__(self, slave_id=1):
        self.slave_id = slave_id

    def read_data(self):
        # 온도와 습도 가짜 데이터 생성
        temp = round(random.uniform(20.0, 30.0), 2)
        humi = round(random.uniform(40.0, 60.0), 2)
        
        # 10% 확률로 이상치 발생
        if random.random() < 0.1:
            temp = round(random.uniform(80.0, 100.0), 2)
            
        return {
            "temperature": temp,
            "humidity": humi
        }
    
    # 릴레이 움직이는 기능
    def write_coil(self, address, value):
        # 지금은 하드웨어가 없으니 터미널에 출력하는 것으로 대체
        action = "ON" if value else "OFF"
        print(f"⚡ [Modbus 하드웨어 제어] 주소 {address}번 릴레이를 {action} 합니다.")
        # 나중에 실제 pymodbus 등을 쓸 때 여기에 client.write_coil()이 들어감
"""

"""
 실제 장비로 교체 시 전기 신호 읽어 숫자로 바꿔야됨
 pymodbus 라이브러리 사용해서 실제 하드웨어의 메모리 주소(register)를 읽어와야됨.(장비 매뉴얼에서 레지스터 확인)
 client.read_holding_registers() 같은 실제 통신 함수로 변경.
 main.py에서 연결 정보를 실제 기기의 IP주소나 시리얼 포트(COM포트)번호 알려줘야 됨.
"""

"""
#실제 장비 교체 시 (수정 필요)

from pymodbus.client import ModbusSerialClient

class SensorReader:
    def __init__(self, slave_id=1, port='/dev/ttyUSB0'): # 맥북은 '/dev/cu.usbserial-...' 형식
        self.slave_id = slave_id
        # 시리얼 설정 (장비 매뉴얼에 적힌 baudrate와 맞아야 함)
        self.client = ModbusSerialClient(
            port=port, 
            baudrate=9600, 
            stopbits=1, 
            bytesize=8, 
            parity='N'
        )

    def read_data(self):
        self.client.connect()
        # 장비 레지스터 0번부터 2개 읽기
        result = self.client.read_holding_registers(0, 2, slave=self.slave_id)   # 장비 매뉴얼에 맞게 0번 레지스터 수정해야 됨
        
        if not result.isError():
            temp = result.registers[0] / 10.0           # 대부분의 PLC는 소수점을 보내지 못해서 데이터 스케일링 필요
            humi = result.registers[1] / 10.0
            return {"temperature": temp, "humidity": humi}
        return {"temperature": 0, "humidity": 0}

    def write_coil(self, address, value):
        self.client.connect()
        self.client.write_coil(address, value, slave=self.slave_id)
        print(f"⚡ [RS485 시리얼 제어] 릴레이 {address}번 -> {value}")


"""
