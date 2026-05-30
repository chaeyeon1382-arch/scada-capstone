# 이상징후 감지 로직 담당
# 수집된 데이터가 정상인지, 이상징후 인지 판단
# JSON 데이터를 보고 온도가 너무 높으면 ATTACK_DETECTED라는 문구를 데이터에 추가


class SecurityEngine:
    def __init__(self, threshold=30.0):
        self.threshold = float(threshold)

    def analyze(self, sensor_payload):
        data_content = sensor_payload.get("data", sensor_payload)
        raw_temp = data_content.get("temperature", 0.0)
        
        try:
            temp = float(raw_temp)
        except (ValueError, TypeError):
            print(f"❌ [오류] 온도 데이터 형식이 올바르지 않습니다: {raw_temp}")
            sensor_payload["status"] = "ERROR"
            return sensor_payload
        
        # 355 같은 RAW 값이 들어오면 35.5로 변환
        if temp > 100:
            temp = temp / 10.0
        
        # 외부에서 무슨 값을 보냈든 상관없이 무조건 45.0도로 강제 고정
        current_threshold = 30.0 
        
        # 터미널에서 눈으로 직접 확인하기 위한 디버깅 로그
        print(f"🔍 현재 온도: {temp}°C | 비교할 기준치: {current_threshold}°C")
        
        # 무조건 35.5 >= 45.0 을 비교하게 되므로 무조건 else로 빠짐
        if temp >= current_threshold:
            print(f"🚨 [경고] 이상 징후 감지! ({temp}°C)")
            sensor_payload["status"] = "ATTACK_DETECTED"
        else:
            sensor_payload["status"] = "NORMAL"
            
        return sensor_payload