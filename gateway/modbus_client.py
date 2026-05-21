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
 실제 장비로 교체 시 전기 신호 읽어 숫자로 바꿔야됨
 pymodbus 라이브러리 사용해서 실제 하드웨어의 메모리 주소(register)를 읽어와야됨.(장비 매뉴얼에서 레지스터 확인)
 client.read_holding_registers() 같은 실제 통신 함수로 변경.
 main.py에서 연결 정보를 실제 기기의 IP주소나 시리얼 포트(COM포트)번호 알려줘야 됨.
"""

