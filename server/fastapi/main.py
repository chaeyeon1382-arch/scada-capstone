from fastapi import FastAPI

app = FastAPI(title="SCADA API Server")


@app.get("/")
def root():
    return {"status": "ok", "message": "SCADA API is running"}


# ─────────────────────────────────────────
# 여기에 DB 팀원이 라우터를 추가할 예정
# 예: app.include_router(sensor_router)
#     app.include_router(control_router)
# ─────────────────────────────────────────
