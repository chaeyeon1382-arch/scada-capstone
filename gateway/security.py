# 이상징후 감지 로직 담당
# 수집된 데이터가 정상인지, 이상징후 인지 판단
# JSON 데이터를 보고 온도가 너무 높으면 ATTACK_DETECTED라는 문구를 데이터에 추가


class SecurityEngine:
    def __init__(self, threshold=450):
        # threshold가 혹시나 문자열로 들어오더라도 안전하게 float로 변환 (450.0)
        self.threshold = float(threshold)

    def analyze(self, sensor_payload):
        # 미세조정 1: "data" 키가 있으면 안의 값을 쓰고, 없으면 전체 dict에서 찾음 (KeyError 방지)
        data_content = sensor_payload.get("data", sensor_payload)
        raw_temp = data_content.get("temperature", 0.0)
        
        # 데이터가 문자열("425")로 들어올 경우를 대비해 float로 강제 변환
        try:
            temp = float(raw_temp)
        except (ValueError, TypeError):
            print(f"❌ [오류] 온도 데이터 형식이 올바르지 않습니다: {raw_temp} (Type: {type(raw_temp)})")
            sensor_payload["status"] = "ERROR"
            return sensor_payload
        
        # 안전하게 Raw 값 대 Raw 값(353 >= 450.0)으로 비교합니다.
        if temp >= self.threshold:
            # 💡 미세조정 2: 비교는 353으로 하되, 프린트할 때는 보기 좋게 10을 나눠서 '45.3°C'로 출력
            display_temp = temp / 10.0 if temp > 100 else temp
            print(f"🚨 [경고] 이상 징후 감지! ({display_temp}°C)")
            sensor_payload["status"] = "ATTACK_DETECTED"
        else:
            sensor_payload["status"] = "NORMAL"
            
        return sensor_payload