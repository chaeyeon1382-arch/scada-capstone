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