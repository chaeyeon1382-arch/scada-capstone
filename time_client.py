# time_client.py (노트북에서 실행)
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2)

offsets = []

for i in range(10):  # 10번 측정
    T1 = time.time()
    s.sendto(str(T1).encode(), ('192.168.0.115', 9999))
    
    data, _ = s.recvfrom(1024)
    T4 = time.time()
    
    T2, T3 = map(float, data.decode().split(','))
    
    offset = ((T2 - T1) + (T3 - T4)) / 2
    offsets.append(offset)
    print(f"측정 {i+1}: 시계 오차 = {offset*1000:.2f}ms")
    time.sleep(0.5)

avg_offset = sum(offsets) / len(offsets)
print(f"\n평균 시계 오차: {avg_offset*1000:.2f}ms")
print(f"두 기기 시간 차이: {'라즈베리파이가 빠름' if avg_offset > 0 else '노트북이 빠름'} ({abs(avg_offset)*1000:.2f}ms)")

