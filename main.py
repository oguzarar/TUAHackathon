"""
============================================================
  ASA TEAM — FastAPI Backend
  Solar Storm Early Warning System
============================================================
Endpoints:
  GET  /               → Health check
  GET  /status         → Live NOAA + NASA analysis + Flares + Kp
  GET  /history        → Past N threat history records
  GET  /history/noaa   → Past NOAA measurement history
  GET  /history/cme    → Past CME event history
  WS   /ws             → WebSocket (live updates)

Install:
  pip install fastapi uvicorn sqlalchemy requests pandas
Run:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
============================================================
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import (
    create_database, get_db,
    NoaaMeasurement, CmeEvent, ThreatHistory,
    KpIndex, SolarFlare
)
from veri_motoru import full_analysis, already_alerted_cme

# ── Connection Manager (WebSocket) ──────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            if ws in self.active:
                self.active.remove(ws)


connection_manager = ConnectionManager()
latest_analysis: dict = {}


# ── Background Task ──────────────────────────────────────
async def periodic_scan():
    """Fetches data every 10 mins, saves to DB, broadcasts to WS."""
    while True:
        global latest_analysis
        try:
            # Run blocking HTTP calls in a thread so the event loop stays alive
            result = await asyncio.to_thread(full_analysis)
            latest_analysis = result

            # Save to DB (also blocking I/O)
            def _db_save():
                db = next(get_db())
                try:
                    _save_to_db(db, result)
                finally:
                    db.close()
            await asyncio.to_thread(_db_save)

            # Broadcast to WebSocket clients
            await connection_manager.broadcast(result)

            print(f"[Scan OK] {result.get('timestamp', '?')} — level: {result.get('final_level')}")

        except Exception as e:
            import traceback
            print(f"[Scan Error] {e}")
            traceback.print_exc()

        await asyncio.sleep(600)  # 10 minutes


def _save_to_db(db: Session, result: dict):
    """Saves the analysis result into the tables."""
    noaa = result.get("noaa", {})
    cme_list = result.get("cme_list", [])
    kp = result.get("kp", {})
    flr_list = result.get("flr_list", [])

    # NOAA record
    if noaa.get("level") != "UNKNOWN":
        db.add(NoaaMeasurement(
            bz_gsm          = noaa.get("bz_gsm"),
            bt              = noaa.get("bt"),
            speed           = noaa.get("speed"),
            density         = noaa.get("density"),
            bz_neg_duration = noaa.get("bz_neg_duration", 0),
            l1_delay_min    = noaa.get("l1_delay_min"),
            level           = noaa.get("level"),
            message         = noaa.get("message"),
        ))

    # CME records
    for cme in cme_list:
        existing = db.query(CmeEvent).filter_by(cme_id=cme["cme_id"]).first()
        if not existing:
            db.add(CmeEvent(
                cme_id            = cme["cme_id"],
                speed             = cme.get("speed"),
                half_angle        = cme.get("half_angle"),
                longitude         = cme.get("longitude"),
                latitude          = cme.get("latitude"),
                alignment         = cme.get("alignment"),
                level             = cme.get("level"),
                earth_target      = cme.get("earth_target", False),
                estimated_arrival = cme.get("estimated_arrival"),
                l1_delay          = cme.get("l1_delay"),
                targets           = cme.get("targets"),
            ))

    # KP Index Record
    if kp and kp.get("level") != "UNKNOWN":
        db.add(KpIndex(
            kp_value = kp.get("kp_value", 0),
            time_tag = kp.get("time_tag"),
            level    = kp.get("level")
        ))
        
    # Solar Flares Record
    for flr in flr_list:
        existing = db.query(SolarFlare).filter_by(flare_id=flr["flare_id"]).first()
        if not existing:
            db.add(SolarFlare(
                flare_id   = flr["flare_id"],
                begin_time = flr.get("begin_time"),
                peak_time  = flr.get("peak_time"),
                end_time   = flr.get("end_time"),
                class_type = flr.get("class_type"),
                level      = flr.get("level")
            ))

    # Combined threat record
    db.add(ThreatHistory(
        noaa_level  = result.get("noaa", {}).get("level", "UNKNOWN"),
        cme_level   = max(
            (c["level"] for c in cme_list if c.get("earth_target")),
            key=lambda s: ["SAFE","UNKNOWN","LOW","MEDIUM","HIGH","CRITICAL"].index(s),
            default="SAFE"
        ),
        kp_level    = kp.get("level", "SAFE"),
        flare_level = max(
            (f["level"] for f in flr_list),
            key=lambda s: ["SAFE","UNKNOWN","LOW","MEDIUM","HIGH","CRITICAL"].index(s),
            default="SAFE"
        ),
        final_level = result.get("final_level", "SAFE"),
        determiner  = result.get("determiner"),
    ))
    db.commit()


# ── App Lifespan ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    # Initial scan — run in thread so startup doesn't block
    global latest_analysis
    try:
        latest_analysis = await asyncio.to_thread(full_analysis)
        def _db_save():
            db = next(get_db())
            try:
                _save_to_db(db, latest_analysis)
            finally:
                db.close()
        await asyncio.to_thread(_db_save)
        print(f"[Startup OK] {latest_analysis.get('timestamp', '?')} — level: {latest_analysis.get('final_level')}")
    except Exception as e:
        import traceback
        print(f"[Startup Scan Error] {e}")
        traceback.print_exc()
    # Start background loop
    task = asyncio.create_task(periodic_scan())
    yield
    task.cancel()


# ── FastAPI App ────────────────────────────────────
app = FastAPI(
    title="ASA Team — Solar Storm API",
    description="Real-time space weather with NASA (CME, Flare) + NOAA (DSCOVR, Kp)",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/", tags=["General"])
def health_check():
    """Checks if API is running."""
    return {
        "status": "online",
        "version": "3.0.0",
        "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    }


@app.get("/status", tags=["Live Data"])
def live_status():
    """
    Returns live NOAA + NASA analysis.
    Reads from cache (updated every 10 min).
    """
    if latest_analysis:
        return latest_analysis
    return full_analysis()


@app.get("/status/fresh", tags=["Live Data"])
def fresh_status(db: Session = Depends(get_db)):
    """Fetches real-time data from NASA + NOAA (bypasses cache)."""
    global latest_analysis
    result = full_analysis()
    latest_analysis = result
    _save_to_db(db, result)
    return result


@app.get("/history", tags=["History"])
def threat_history(
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db)
):
    """Returns past N combined threat records."""
    records = (
        db.query(ThreatHistory)
        .order_by(ThreatHistory.record_time.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "time":        k.record_time.strftime("%d.%m.%Y %H:%M"),
            "noaa_level":  k.noaa_level,
            "cme_level":   k.cme_level,
            "kp_level":    k.kp_level,
            "flare_level": k.flare_level,
            "final_level": k.final_level,
            "determiner":  k.determiner,
        }
        for k in records
    ]


@app.get("/history/noaa", tags=["History"])
def noaa_history(
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Returns past N NOAA measurements. Used for charts."""
    records = (
        db.query(NoaaMeasurement)
        .order_by(NoaaMeasurement.record_time.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "time":            k.record_time.strftime("%d.%m.%Y %H:%M"),
            "bz_gsm":          k.bz_gsm,
            "bt":              k.bt,
            "speed":           k.speed,
            "density":         k.density,
            "bz_neg_duration": k.bz_neg_duration,
            "l1_delay_min":    k.l1_delay_min,
            "level":           k.level,
            "message":         k.message,
        }
        for k in records
    ]


@app.get("/history/cme", tags=["History"])
def cme_history(
    limit: int = Query(default=20, le=200),
    db: Session = Depends(get_db)
):
    """Returns past N CME events."""
    records = (
        db.query(CmeEvent)
        .order_by(CmeEvent.record_time.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "time":              k.record_time.strftime("%d.%m.%Y %H:%M"),
            "cme_id":            k.cme_id,
            "speed":             k.speed,
            "half_angle":        k.half_angle,
            "longitude":         k.longitude,
            "latitude":          k.latitude,
            "alignment":         k.alignment,
            "level":             k.level,
            "earth_target":      k.earth_target,
            "estimated_arrival": k.estimated_arrival,
            "l1_delay":          k.l1_delay,
            "targets":           k.targets,
        }
        for k in records
    ]


@app.get("/statistics", tags=["General"])
def statistics(db: Session = Depends(get_db)):
    """Returns DB stats."""
    return {
        "noaa_count":        db.query(NoaaMeasurement).count(),
        "cme_count":         db.query(CmeEvent).count(),
        "threat_count":      db.query(ThreatHistory).count(),
        "kp_count":          db.query(KpIndex).count(),
        "flr_count":         db.query(SolarFlare).count(),
        "last_update":       latest_analysis.get("timestamp", "—"),
        "active_ws_clients": len(connection_manager.active),
    }


# ── WebSocket ─────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Live connection.
    Sends latest analysis on connect, then auto-updates.
    """
    await connection_manager.connect(websocket)
    try:
        if latest_analysis:
            await websocket.send_json(latest_analysis)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
