# 이상징후 감지 로직 담당
# 수집된 데이터가 정상인지, 이상징후 인지 판단
# JSON 데이터를 보고 온도가 너무 높으면 ATTACK_DETECTED라는 문구를 데이터에 추가


class SecurityEngine:
    def __init__(self, threshold=80.0):
        self.threshold = threshold

    def analyze(self, sensor_payload):
        # sensor_payload["data"]["temperature"] 구조를 확인합니다.
        temp = sensor_payload["data"].get("temperature", 0)
        
        if temp >= self.threshold:
            print(f"🚨 [경고] 이상 징후 감지! ({temp}°C)")
            sensor_payload["status"] = "ATTACK_DETECTED"
        else:
            sensor_payload["status"] = "NORMAL"
            
        return sensor_payload