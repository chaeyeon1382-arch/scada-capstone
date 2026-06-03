from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os

router = APIRouter(prefix="/slack", tags=["slack"])

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

class AlertMessage(BaseModel):
    message: str

@router.post("/alert")
async def send_slack_alert(body: AlertMessage):
    if not SLACK_WEBHOOK_URL:
        return {"result": "error", "detail": "SLACK_WEBHOOK_URL 미설정"}
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            SLACK_WEBHOOK_URL,
            json={"text": body.message}
        )
    
    return {"result": "ok", "status": res.status_code}