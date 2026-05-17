# 이상징후 감지 로직 담당
# 수집된 데이터가 정상인지, 이상징후 인지 판단
# JSON 데이터를 보고 온도가 너무 높으면 ATTACK_DETECTED라는 문구를 데이터에 추가


class SecurityEngine:
    def __init__(self, threshold=45.0):
        # threshold가 혹시나 문자열로 들어오더라도 안전하게 float로 변환
        self.threshold = float(threshold)

    def analyze(self, sensor_payload):
        # 데이터가 없을 때의 기본값도 0.0(float)으로 지정
        raw_temp = sensor_payload["data"].get("temperature", 0.0)
        
        # 데이터가 문자열("42.5")로 들어올 경우를 대비해 float로 강제 변환
        try:
            temp = float(raw_temp)
        except (ValueError, TypeError):
            # 숫자로 변환할 수 없는 이상한 데이터가 들어온 경우 예외 처리
            print(f"❌ [오류] 온도 데이터 형식이 올바르지 않습니다: {raw_temp} (Type: {type(raw_temp)})")
            sensor_payload["status"] = "ERROR"
            return sensor_payload
        
        # 이제 안전하게 숫자 대 숫자로 비교합니다.
        if temp >= self.threshold:
            print(f"🚨 [경고] 이상 징후 감지! ({temp}°C)")
            sensor_payload["status"] = "ATTACK_DETECTED"
        else:
            sensor_payload["status"] = "NORMAL"
            
        return sensor_payload