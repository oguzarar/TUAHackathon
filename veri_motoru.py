"""
Solar data fetch and analysis engine.
API-compatible version.
No terminal output — returns raw data dictionaries.
"""

import os
import re
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

NASA_API_KEY    = os.environ.get("NASA_API_KEY")
NOAA_MAG_URL    = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
NOAA_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
NOAA_KP_URL     = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
NASA_CME_URL    = "https://api.nasa.gov/DONKI/CME"
NASA_FLR_URL    = "https://api.nasa.gov/DONKI/FLR"
L1_DISTANCE_KM  = 1_500_000

# Severity weights for weighted scoring
SOURCE_WEIGHTS = {
    "NOAA live data":    0.40,   # Real-time measured data — most reliable
    "NOAA Kp-Index":     0.20,   # Actual geomagnetic impact
    "NASA CME prediction": 0.25, # Model/prediction based
    "NASA Solar Flare":  0.15,   # Indirect effect
}
LEVEL_SCORES = {"SAFE": 0, "UNKNOWN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "EXTREME": 5}

LEVEL_ORDER = ["SAFE", "UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL", "EXTREME"]


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def utc_to_local(utc_str: str) -> str:
    if not utc_str:
        return ""
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", ""))
        return (dt + timedelta(hours=3)).strftime("%d %B %H:%M TSİ")
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
#  NOAA (MAG/PLASMA & KP)
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
    """Calculate the longest consecutive Bz-negative streak in MINUTES.
    Uses actual timestamps instead of row count to handle data gaps."""
    if df.empty or "time_tag" not in df.columns:
        return 0
    sorted_df = df.sort_values("time_tag").dropna(subset=["bz_gsm"])
    if sorted_df.empty:
        return 0

    max_minutes = 0
    streak_start = None
    for _, row in sorted_df.iterrows():
        if row["bz_gsm"] < 0:
            if streak_start is None:
                streak_start = row["time_tag"]
            streak_end = row["time_tag"]
        else:
            if streak_start is not None:
                minutes = (streak_end - streak_start).total_seconds() / 60
                max_minutes = max(max_minutes, int(minutes))
                streak_start = None
    # Check trailing streak
    if streak_start is not None:
        minutes = (streak_end - streak_start).total_seconds() / 60
        max_minutes = max(max_minutes, int(minutes))
    return max_minutes


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

    # Threat level — duration must combine with Bz intensity to avoid false positives
    if (bz <= -20
        or (bz <= -15 and bz_duration >= 30)
        or (bz <= -10 and bz_duration >= 20 and speed and speed >= 600)
        or (speed and speed >= 800 and bz <= -10)
        or (bt and bt >= 25 and bz <= -10)
        or (dens and dens >= 30 and bz <= -10)):
        level   = "CRITICAL"
        message = f"Severe storm (G4-G5). Bz={bz:.1f} nT, negative for {bz_duration} min."
    elif (bz <= -10
          or (bz <= -5 and bz_duration >= 30 and speed and speed >= 500)
          or (speed and speed >= 600 and bz <= -5)
          or (bt and bt >= 15 and bz <= -5)
          or (dens and dens >= 15 and bz <= -5)):
        level   = "HIGH"
        message = f"Strong storm (G2-G3). Bz={bz:.1f} nT, negative for {bz_duration} min."
    elif (bz <= -5
          or (bz <= -3 and bz_duration >= 15)
          or (speed and speed >= 500 and bz <= -3)
          or (bt and bt >= 10 and bz <= -3)
          or (dens and dens >= 10 and bz <= -3)):
        level   = "MEDIUM"
        message = f"Moderate storm (G1). Bz={bz:.1f} nT, negative for {bz_duration} min."
    elif bz <= -3 or (speed and speed >= 450):
        level   = "LOW"
        message = f"Minor activity. Bz={bz:.1f} nT, speed={speed:.0f} km/s."
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


def analyze_kp_index() -> dict:
    """
    Fetch the latest Planetary K-Index from NOAA JSON.
    """
    try:
        r = requests.get(NOAA_KP_URL, timeout=15)
        r.raise_for_status()
        data = r.json()
        if len(data) > 1:
            # First row is headers, get the very last row
            latest_row = data[-1]
            time_tag = latest_row[0]
            kp_val_str = latest_row[1]
            kp = float(kp_val_str)
            
            if kp >= 7:
                level = "CRITICAL"
            elif kp >= 5:
                level = "HIGH"
            elif kp >= 4:
                level = "MEDIUM"
            elif kp >= 3:
                level = "LOW"
            else:
                level = "SAFE"
                
            return {
                "kp_value": kp,
                "time_tag": utc_to_local(time_tag),
                "level": level
            }
    except Exception as e:
        print("[Kp-Index Error]", str(e))
    return {"kp_value": 0, "time_tag": "—", "level": "UNKNOWN"}


# ═══════════════════════════════════════════════════════════
#  NASA DONKI (CME & FLARES)
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
        time.sleep(10)
        r = requests.get(NASA_CME_URL, params=params, timeout=15)
    if r.status_code != 200:
        return []

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

        # ── Parse ALL ENLIL runs, pick the most relevant ──
        enlil_list  = best.get("enlilList") or []
        # Prefer the latest model run (last in list tends to be most up-to-date)
        enlil       = enlil_list[-1] if enlil_list else {}

        # ── ENLIL Earth impact flags (this is the actual prediction!) ──
        is_earth_gb    = enlil.get("isEarthGB", False)          # Glancing blow to Earth
        is_earth_minor = enlil.get("isEarthMinorImpact", False) # Minor impact on Earth
        est_arrival    = enlil.get("estimatedShockArrivalTime")  # Shock arrival at Earth
        kp_90          = enlil.get("kp_90")                      # Predicted Kp (90° clock)
        kp_180         = enlil.get("kp_180")                     # Predicted Kp (180° clock)

        # ── Classify impact list targets ──
        impacts     = enlil.get("impactList") or []
        targets     = [v.get("location", "").upper() for v in impacts]

        # Targets near Earth (~1 AU, could indicate nearby CME passage)
        NEAR_EARTH_CRAFT = ["STEREO A", "DSCOVR", "ACE", "L1",
                            "BEPICOLOMBO", "OSIRIS-APEX"]
        # Deep space (not relevant to Earth threat)
        # Juno (Jupiter), Mars, Europa Clipper, Psyche, Lucy, Solar Orbiter (variable)

        has_near_earth_craft = any(
            any(ne in loc for ne in NEAR_EARTH_CRAFT)
            for loc in targets
        )

        # Earth is targeted if:  ENLIL says GB/minor OR impactList has Earth/L1/DSCOVR/ACE
        direct_earth_in_list = any(
            z in h for h in targets
            for z in ["EARTH", "L1", "DSCOVR", "ACE"]
        )

        # Earth is targeted if ANY of these are true:
        # 1. ENLIL says glancing blow or minor impact
        # 2. impactList contains Earth/L1/DSCOVR/ACE
        # 3. ENLIL has estimatedShockArrivalTime (= predicted shock at Earth!)
        # 4. ENLIL has kp predictions (these ARE predictions for Earth's Kp)
        has_enlil_earth_kp = (est_arrival is not None) or (kp_90 is not None) or (kp_180 is not None)
        earth_target = is_earth_gb or is_earth_minor or direct_earth_in_list or has_enlil_earth_kp

        alignment, details = calculate_cme_alignment(lon, lat)

        # ── Estimated arrival: prefer ENLIL shock arrival, else from impactList ──
        estimated_arrival = None
        if est_arrival:
            estimated_arrival = utc_to_local(est_arrival)
        else:
            # Fallback: look for Earth/L1 in impact list
            earth_impact = next(
                (v for v in impacts if
                 "EARTH" in v.get("location","").upper() or
                 "L1"    in v.get("location","").upper()),
                None
            )
            if earth_impact:
                estimated_arrival = utc_to_local(earth_impact["arrivalTime"])

        # ── Determine threat level ──
        if earth_target:
            # ENLIL confirms Earth impact — use alignment + speed for severity
            if alignment == "DIRECT":
                if speed and speed >= 1000 and angle and angle >= 60:
                    level = "CRITICAL"
                elif speed and speed >= 600:
                    level = "HIGH"
                elif speed and speed >= 400:
                    level = "MEDIUM"
                else:
                    level = "LOW"
            elif alignment == "EDGE":
                if speed and speed >= 1000 and angle and angle >= 60:
                    level = "HIGH"
                elif speed and speed >= 700:
                    level = "HIGH"
                elif speed and speed >= 400:
                    level = "MEDIUM"
                else:
                    level = "LOW"
            elif alignment == "FAR":
                # Geometry says FAR but ENLIL says Earth — trust ENLIL (glancing)
                if is_earth_gb and not is_earth_minor:
                    level = "MEDIUM" if (speed and speed >= 500) else "LOW"
                else:
                    level = "LOW"
            elif alignment == "UNKNOWN":
                # No coordinates but ENLIL says Earth
                if kp_180 and kp_180 >= 6:
                    level = "HIGH"
                elif kp_90 and kp_90 >= 4:
                    level = "MEDIUM"
                else:
                    level = "MEDIUM" if (speed and speed >= 500) else "LOW"
            else:
                level = "MEDIUM"
        elif has_near_earth_craft and not earth_target:
            # CME hits nearby spacecraft but not Earth — situational awareness
            if alignment in ("DIRECT", "EDGE") and speed and speed >= 800:
                level = "LOW"
            else:
                level = "SAFE"
        else:
            # No Earth/nearby impact
            if alignment == "UNKNOWN" and speed and speed >= 700:
                level = "LOW"  # Unknown direction, fast — can't rule out
            else:
                level = "SAFE"

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
            "is_earth_gb":       is_earth_gb,
            "targets":           ", ".join(targets),
            "estimated_arrival": estimated_arrival,
            "l1_delay":          l1_delay_str(speed) if speed else "—",
        })

    return results


def analyze_nasa_flares() -> list[dict]:
    """
    Fetch and analyze Solar Flares in the last 72 hours.
    Returns list of dicts.
    """
    now       = datetime.now(timezone.utc)
    today     = now.strftime("%Y-%m-%d")
    past_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    params    = {"api_key": NASA_API_KEY, "startDate": past_date, "endDate": today}
    
    r = requests.get(NASA_FLR_URL, params=params, timeout=15)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get(NASA_FLR_URL, params=params, timeout=15)
    if r.status_code != 200:
        return []
    
    results = []
    # FLR data
    for flr in (r.json() or []):
        flr_id = flr.get("flrID", "")
        # e.g., "M2.1", "X1.0", "C9.9"
        class_type = flr.get("classType", "")
        
        # Threat level assignment based on flare class
        # X: Critical, M: High, C: Medium/Low, A/B: Safe
        if "X" in class_type:
            level = "CRITICAL"
        elif "M" in class_type:
            level = "HIGH"
        elif "C" in class_type:
            level = "MEDIUM"
        else:
            level = "SAFE"
            
        loc = flr.get("sourceLocation", "")
        lat = None
        lon = None
        if loc:
            m = re.match(r'([NS])(\d+)([EW])(\d+)', loc.upper())
            if m:
                lat_dir, lat_val, lon_dir, lon_val = m.groups()
                lat = float(lat_val) if lat_dir == 'N' else -float(lat_val)
                lon = -float(lon_val) if lon_dir == 'W' else float(lon_val)
                
        results.append({
            "flare_id": flr_id,
            "class_type": class_type,
            "begin_time": utc_to_local(flr.get("beginTime")),
            "peak_time": utc_to_local(flr.get("peakTime")),
            "end_time": utc_to_local(flr.get("endTime")),
            "level": level,
            "source_location": loc,
            "latitude": lat,
            "longitude": lon
        })
    return results


# ═══════════════════════════════════════════════════════════
#  COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════

def full_analysis() -> dict:
    """
    Fetches NOAA and NASA data, creates a combined result,
    including Solar Flares and Kp-Index.
    """
    noaa     = {}
    kp       = {}
    cme_list = []
    flr_list = []

    try:
        noaa = analyze_noaa()
    except Exception as e:
        noaa = {"level": "UNKNOWN", "message": str(e)}

    try:
        kp = analyze_kp_index()
    except Exception as e:
        kp = {"level": "UNKNOWN"}

    try:
        cme_list = analyze_nasa_cme()
    except Exception:
        cme_list = []

    try:
        flr_list = analyze_nasa_flares()
    except Exception:
        flr_list = []

    # ── Determine highest level per source ──
    noaa_level = noaa.get("level", "UNKNOWN")
    kp_level   = kp.get("level", "UNKNOWN")

    # CME: only count earth-targeted ones, but also consider EDGE/DIRECT non-earth
    highest_cme = "SAFE"
    for cme in cme_list:
        cme_lvl = cme["level"]
        if cme_lvl in LEVEL_ORDER and LEVEL_ORDER.index(cme_lvl) > LEVEL_ORDER.index(highest_cme):
            highest_cme = cme_lvl

    highest_flr = "SAFE"
    for flr in flr_list:
        flr_lvl = flr["level"]
        if flr_lvl in LEVEL_ORDER and LEVEL_ORDER.index(flr_lvl) > LEVEL_ORDER.index(highest_flr):
            highest_flr = flr_lvl

    # ── Weighted scoring system ──
    source_levels = {
        "NOAA live data":      noaa_level,
        "NOAA Kp-Index":       kp_level,
        "NASA CME prediction": highest_cme,
        "NASA Solar Flare":    highest_flr,
    }

    weighted_score = 0.0
    top_source = "System"
    top_score  = -1
    for source, lvl in source_levels.items():
        score = LEVEL_SCORES.get(lvl, 0)
        weight = SOURCE_WEIGHTS.get(source, 0.1)
        weighted_score += score * weight
        # Track which source contributes most
        if score > top_score:
            top_score  = score
            top_source = source

    # Map weighted score back to level
    if weighted_score >= 3.8:
        final_level = "EXTREME"
    elif weighted_score >= 3.2:
        final_level = "CRITICAL"
    elif weighted_score >= 2.2:
        final_level = "HIGH"
    elif weighted_score >= 1.2:
        final_level = "MEDIUM"
    elif weighted_score >= 0.5:
        final_level = "LOW"
    else:
        final_level = "SAFE"

    # Override: if ANY source is CRITICAL, final is at least HIGH
    if any(lvl == "CRITICAL" for lvl in source_levels.values()):
        if LEVEL_ORDER.index(final_level) < LEVEL_ORDER.index("HIGH"):
            final_level = "HIGH"

    determiner = top_source

    return {
        "timestamp":   datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "final_level": final_level,
        "determiner":  determiner,
        "noaa":        noaa,
        "kp":          kp,
        "cme_list":    cme_list,
        "flr_list":    flr_list,
    }
