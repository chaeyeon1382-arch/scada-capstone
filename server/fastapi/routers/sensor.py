import time  # ★ 맨 위에 파이썬 내장 시간 라이브러리를 추가합니다!
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import SensorData

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/{slave_id}/data")
def get_latest_data(slave_id: int, db: Session = Depends(get_db)):
    result = db.query(SensorData)\
               .filter(SensorData.slave_id == slave_id)\
               .order_by(SensorData.timestamp.desc())\
               .first()

    if result is None:
        raise HTTPException(status_code=404, detail="데이터 없음")
    
    # 🛠️ [백엔드 수정 핵심] ORM 객체 데이터를 파이썬 딕셔너리로 풀고,
    # 출발 도장인 "server_send_time"을 심어서 리턴합니다.
    return {
        "id": result.id,
        "slave_id": result.slave_id,
        "temperature": result.temperature,
        "humidity": result.humidity,
        "timestamp": result.timestamp,
        "received_at": result.received_at,
        "status": getattr(result, "status", "NORMAL"), # status 필드가 없을 경우를 대비한 안전장치
        "server_send_time": time.time()  # ◀︎ ★ UI가 레이턴시를 계산할 수 있도록 현재 서버 시간을 찍어줍니다.
    }


@router.get("/{slave_id}/history")
def get_history(slave_id: int, limit: int = 100, db: Session = Depends(get_db)):
    result = db.query(SensorData)\
               .filter(SensorData.slave_id == slave_id)\
               .order_by(SensorData.timestamp.desc())\
               .limit(limit)\
               .all()
    return result


"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import SensorData

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/{slave_id}/data")
def get_latest_data(slave_id: int, db: Session = Depends(get_db)):
    result = db.query(SensorData)\
               .filter(SensorData.slave_id == slave_id)\
               .order_by(SensorData.timestamp.desc())\
               .first()

    if result is None:
        raise HTTPException(status_code=404, detail="데이터 없음")
    return result


@router.get("/{slave_id}/history")
def get_history(slave_id: int, limit: int = 100, db: Session = Depends(get_db)):
    result = db.query(SensorData)\
               .filter(SensorData.slave_id == slave_id)\
               .order_by(SensorData.timestamp.desc())\
               .limit(limit)\
               .all()
    return result

"""