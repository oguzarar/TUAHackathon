"""
Solar data fetch and analysis engine.
API-compatible version.
No terminal output — returns raw data dictionaries.
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

NASA_API_KEY    = os.environ.get("NASA_API_KEY", "DEMO_KEY")
NOAA_MAG_URL    = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
NOAA_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
NASA_CME_URL    = "https://api.nasa.gov/DONKI/CME"
STRATEGIC_ZONES = ["EARTH", "L1", "STEREO A", "DSCOVR", "ACE"]
L1_DISTANCE_KM  = 1_500_000

already_alerted_cme: set = set()

LEVEL_ORDER = ["SAFE", "UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def utc_to_local(utc_str: str) -> str:
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", ""))
        return (dt + timedelta(hours=3)).strftime("%d %B %H:%M Local")
    except Exception:
        return utc_str


def l1_delay_min(speed: float) -> float | None:
    if not speed or speed <= 0:
        return None
    return round((L1_DISTANCE_KM / speed) / 60, 1)


def l1_delay_str(speed: float) -> str:
    mins = l1_delay_min(speed)
    if mins is None:
        return "Cannot be calculated"
    if mins >= 60:
        return f"~{mins/60:.1f} hours"
    return f"~{mins:.0f} minutes"


# ═══════════════════════════════════════════════════════════
#  NOAA
# ═══════════════════════════════════════════════════════════

def fetch_noaa_data(url: str) -> list:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    return [dict(zip(data[0], s)) for s in data[1:]]


def merge_noaa_data(mag: list, plasma: list) -> pd.DataFrame:
    mag_df    = pd.DataFrame(mag)
    plasma_df = pd.DataFrame(plasma)
    mag_df["time_tag"]    = pd.to_datetime(mag_df["time_tag"])
    plasma_df["time_tag"] = pd.to_datetime(plasma_df["time_tag"])
    mag_df    = mag_df.sort_values("time_tag")
    plasma_df = plasma_df.sort_values("time_tag")
    for df in [mag_df, plasma_df]:
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    merged = pd.merge_asof(
        mag_df, plasma_df, on="time_tag",
        tolerance=pd.Timedelta("1min"), direction="nearest"
    )
    return merged.dropna(subset=["bz_gsm", "speed"])


def bz_negative_duration(df: pd.DataFrame) -> int:
    max_duration = counter = 0
    for bz in df["bz_gsm"].dropna():
        if bz < 0:
            counter += 1
            max_duration = max(max_duration, counter)
        else:
            counter = 0
    return max_duration


def analyze_noaa() -> dict:
    """
    Fetch NOAA data, analyze last 1 hour.
    Returns dict for API response / DB record.
    """
    try:
        mag    = fetch_noaa_data(NOAA_MAG_URL)
        plasma = fetch_noaa_data(NOAA_PLASMA_URL)
        df     = merge_noaa_data(mag, plasma)
    except Exception as e:
        return {"level": "UNKNOWN", "message": f"Data fetch error: {str(e)}"}

    if df.empty:
        return {"level": "UNKNOWN", "message": "Data could not be merged."}

    last          = df["time_tag"].max()
    one_hour_ago  = last - pd.Timedelta(hours=1)
    recent_df     = df[df["time_tag"] >= one_hour_ago]
    bz_duration   = bz_negative_duration(recent_df)

    bz    = recent_df["bz_gsm"].mean()
    bt    = recent_df["bt"].mean()      if "bt"      in recent_df.columns else None
    speed = recent_df["speed"].mean()   if "speed"   in recent_df.columns else None
    dens  = recent_df["density"].mean() if "density" in recent_df.columns else None

    # Threat level
    if bz <= -20 or (bz <= -10 and bz_duration >= 20) or (speed and speed >= 800) or (bt and bt >= 25) or (dens and dens >= 30):
        level   = "CRITICAL"
        message = f"Severe storm (G4-G5). Bz={bz:.1f} nT, {bz_duration} min negative."
    elif bz <= -10 or (bz <= -5 and bz_duration >= 20) or (speed and speed >= 600) or (bt and bt >= 15) or (dens and dens >= 15):
        level   = "HIGH"
        message = f"Strong storm (G2-G3). Bz negative for {bz_duration} mins."
    elif bz <= -5 or bz_duration >= 10 or (speed and speed >= 500) or (bt and bt >= 10) or (dens and dens >= 10):
        level   = "MEDIUM"
        message = f"Moderate storm (G1). Bz negative for {bz_duration} mins."
    else:
        level   = "SAFE"
        message = "Space weather is calm."

    return {
        "level":         level,
        "message":       message,
        "bz_gsm":        round(float(bz), 2),
        "bt":            round(float(bt), 2)  if bt  is not None else None,
        "speed":         round(float(speed), 1) if speed is not None else None,
        "density":       round(float(dens), 2)  if dens  is not None else None,
        "bz_neg_duration": bz_duration,
        "l1_delay_min":  l1_delay_min(speed) if speed else None,
        "l1_delay_str":  l1_delay_str(speed) if speed else "—",
        "last_measure":  (last + pd.Timedelta(hours=3)).strftime("%d.%m.%Y %H:%M"),
        "record_count":  len(recent_df),
    }


# ═══════════════════════════════════════════════════════════
#  NASA CME
# ═══════════════════════════════════════════════════════════

def calculate_cme_alignment(lon, lat) -> tuple[str, str]:
    try:
        lo, la = float(lon), float(lat)
        if abs(lo) < 20 and abs(la) < 20:
            return "DIRECT", f"lon={lo:+.0f}° lat={la:+.0f}° — direct hit risk"
        elif abs(lo) < 45 and abs(la) < 45:
            return "EDGE",   f"lon={lo:+.0f}° lat={la:+.0f}° — partial impact"
        else:
            return "FAR",    f"lon={lo:+.0f}° lat={la:+.0f}° — misses Earth"
    except (TypeError, ValueError):
        return "UNKNOWN", "No directional data"


def analyze_nasa_cme() -> list[dict]:
    """
    Fetch and analyze new CMEs in the last 72 hours.
    Returns list of dicts.
    """
    now       = datetime.now(timezone.utc)
    today     = now.strftime("%Y-%m-%d")
    past_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    params    = {"api_key": NASA_API_KEY, "startDate": past_date, "endDate": today}

    r = requests.get(NASA_CME_URL, params=params, timeout=15)
    if r.status_code == 429:
        time.sleep(60)
        r = requests.get(NASA_CME_URL, params=params, timeout=15)
    r.raise_for_status()

    results = []
    for cme in (r.json() or []):
        cme_id      = cme.get("activityID", "")
        analyses    = cme.get("cmeAnalyses") or []
        if not analyses:
            continue

        best        = next((a for a in analyses if a.get("isMostAccurate")), analyses[0])
        speed       = best.get("speed")
        angle       = best.get("halfAngle")
        lon         = best.get("longitude")
        lat         = best.get("latitude")
        enlil       = (best.get("enlilList") or [{}])[0]
        impacts     = enlil.get("impactList") or []
        targets     = [v.get("location", "").upper() for v in impacts]

        earth_target       = any(z in h for h in targets for z in STRATEGIC_ZONES)
        alignment, details = calculate_cme_alignment(lon, lat)

        if not earth_target and alignment == "FAR":
            level = "SAFE"
            estimated_arrival = None
        else:
            if alignment == "DIRECT" and speed and speed >= 1000 and angle and angle >= 60:
                level = "CRITICAL"
            elif speed and speed >= 1000 and angle and angle >= 60:
                level = "CRITICAL"
            elif alignment == "DIRECT" and speed and speed >= 600:
                level = "HIGH"
            elif speed and (speed >= 700 or (angle and angle >= 45)):
                level = "HIGH"
            else:
                level = "MEDIUM"

            impacting = next(
                (v for v in impacts if
                 "EARTH" in v.get("location","").upper() or
                 "L1"    in v.get("location","").upper()),
                None
            )
            estimated_arrival = utc_to_local(impacting["arrivalTime"]) if impacting else None

        results.append({
            "cme_id":            cme_id,
            "level":             level,
            "speed":             speed,
            "half_angle":        angle,
            "longitude":         lon,
            "latitude":          lat,
            "alignment":         alignment,
            "alignment_details": details,
            "earth_target":      earth_target,
            "targets":           ", ".join(targets),
            "estimated_arrival": estimated_arrival,
            "l1_delay":          l1_delay_str(speed) if speed else "—",
        })

    return results


# ═══════════════════════════════════════════════════════════
#  COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════

def full_analysis() -> dict:
    """
    Fetches both NOAA and NASA data and returns a combined result.
    FastAPI endpoints and background task use this function.
    """
    noaa     = {}
    cme_list = []

    try:
        noaa = analyze_noaa()
    except Exception as e:
        noaa = {"level": "UNKNOWN", "message": str(e)}

    try:
        cme_list = analyze_nasa_cme()
    except Exception as e:
        cme_list = []

    noaa_level  = noaa.get("level", "UNKNOWN")
    highest_cme = "SAFE"
    for cme in cme_list:
        if cme["earth_target"] and \
           LEVEL_ORDER.index(cme["level"]) > LEVEL_ORDER.index(highest_cme):
            highest_cme = cme["level"]

    if LEVEL_ORDER.index(noaa_level) >= LEVEL_ORDER.index(highest_cme):
        final_level = noaa_level
        determiner  = "NOAA live data"
    else:
        final_level = highest_cme
        determiner  = "NASA CME prediction"

    return {
        "timestamp":   datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "final_level": final_level,
        "determiner":  determiner,
        "noaa":        noaa,
        "cme_list":    cme_list,
    }
