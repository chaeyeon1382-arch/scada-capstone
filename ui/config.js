const CONFIG = {

  // ── 현재 사용할 환경을 여기서 선택 ──────────────────────────
  //   "local"  → 각자 docker compose up (localhost)
  //   "team"   → 모여서 작업시 (이재정 PC IP)
  //   "cloud"  → 발표·시연 
  ENV: "local",

  
  ENDPOINTS: {
    local: {
      label: "로컬 (localhost)",
      api:   "http://localhost:8000",   // FastAPI (db_api)
    },
    team: {
      label: "팀 서버 (이재정 PC)",
      api:   "http://192.168.0.xxx:8000",  // ← 모여서 작업할 때 터미널로 ipconfig 입력 후 그때 IP로 교체 
    },
    cloud: {
      label: "클라우드 / 시연",
      api:   "http://localhost:8000",   // 클라우드 주소로 교체 
    },
  },

  
  DEFAULT_INTERVAL: 5000,

  
  DEFAULT_SLAVE_SENSOR: 1,
  DEFAULT_SLAVE_RELAY:  2,
};

CONFIG.get = function() {
  return this.ENDPOINTS[this.ENV] || this.ENDPOINTS.local;
};
