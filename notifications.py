"""
═══════════════════════════════════════════════════════════
  ASA — 4-Tier Notification System (Telegram)
  Follows NOAA's Watch → Warning → Alert model

  Tier 1: EARLY ALERT  — CME detected heading to Earth (1-4 days before)
  Tier 2: APPROACH      — Arrival within 24 hours
  Tier 3: IMMINENT      — L1 shockwave spike detected (30-60 min before)
  Tier 4: ACTIVE STORM  — Kp ≥ 5 or weighted HIGH/CRITICAL (happening now)
═══════════════════════════════════════════════════════════
"""

import os
import requests
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from database import NotificationLog

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WEB_URL = "https://asa-space-weather.vercel.app" # Örnek web adresi

TSI = timezone(timedelta(hours=3))


# ─────────────────────────────────────────────
#  TELEGRAM CORE
# ─────────────────────────────────────────────

def send_telegram(text: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    if not TELEGRAM_TOKEN:
        print("[Telegram] No TELEGRAM_BOT_TOKEN configured — skipping.")
        return False
    if not TELEGRAM_CHAT_ID:
        print("[Telegram] No TELEGRAM_CHAT_ID configured — skipping.")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=10)
        if resp.status_code == 200:
            print(f"[Telegram] ✅ Message sent.")
            return True
        else:
            print(f"[Telegram] ❌ Error: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[Telegram] ❌ Exception: {e}")
        return False


def send_start_screen(chat_id: int):
    """Sends a simplified welcome message to a user who typed /start."""
    if not TELEGRAM_TOKEN:
        return

    msg = (
        f"🛰️ <b>ASA — Uzay Hava Durumu Bilgi Servisi</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Güneş fırtınaları (CME), jeomanyetik sapmalar ve potansiyel riskler için aktif izleme sistemine hoş geldiniz.\n"
        f"\n"
        f"Sistemimiz Dünya'yı etkileyebilecek her türlü uzay hava durumu olayını 7/24 takip eder ve kritik bir durum tespit edildiğinde sizi **anında bu hat üzerinden** bilgilendirir.\n"
        f"\n"
        f"📢 <b>Neler Alacaksınız?</b>\n"
        f"• 72 saatlik erken uyarılar (CME)\n"
        f"• Şok dalgası varış bildirimleri\n"
        f"• Aktif manyetik fırtına güncellemeleri\n"
        f"\n"
        f"Herhangi bir işlem yapmanıza gerek yoktur. Bir tehdit durumunda tahmin seviyeleri güncellenecek ve tarafınıza bildirilecektir."
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"[Telegram Bot] Error sending start screen: {e}")


def get_bot_updates(offset: int = 0):
    """Fetch recent updates from Telegram API."""
    if not TELEGRAM_TOKEN:
        return []
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        resp = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
        if resp.status_code == 200:
            return resp.json().get("result", [])
    except Exception as e:
        print(f"[Telegram Bot] Polling error: {e}")
    return []


def was_already_sent(db: Session, event_id: str, tier: int, cooldown_hours: int = 6) -> bool:
    """Check if this tier notification was already sent for this event recently."""
    cutoff = datetime.utcnow() - timedelta(hours=cooldown_hours)
    existing = (
        db.query(NotificationLog)
        .filter(
            NotificationLog.event_id == event_id,
            NotificationLog.tier == tier,
            NotificationLog.sent_at >= cutoff,
            NotificationLog.success == True,
        )
        .first()
    )
    return existing is not None


def log_notification(db: Session, event_id: str, tier: int, message: str, success: bool):
    """Save notification to audit log."""
    db.add(NotificationLog(
        event_id=event_id,
        tier=tier,
        channel="telegram",
        message=message[:500],
        success=success,
    ))
    db.commit()


# ─────────────────────────────────────────────
#  TIER 1: EARLY ALERT — CME heading to Earth
#  Triggers: earth_target=True + estimated_arrival exists
#  Timing: 1-4 days before impact
# ─────────────────────────────────────────────

def check_tier1(db: Session, cme_list: list):
    """
    Check for new Earth-directed CMEs with ENLIL arrival predictions.
    This is the TRUE early warning — days before impact.
    """
    for cme in cme_list:
        if not cme.get("earth_target"):
            continue
        if not cme.get("estimated_arrival"):
            continue

        cme_id = cme["cme_id"]
        event_id = f"tier1_{cme_id}"

        if was_already_sent(db, event_id, tier=1, cooldown_hours=24):
            continue

        speed = cme.get("speed", "?")
        alignment = cme.get("alignment", "?")
        arrival = cme.get("estimated_arrival", "?")
        details = cme.get("alignment_details", "")
        level = cme.get("level", "?")
        targets = cme.get("targets", "")
        is_gb = cme.get("is_earth_gb", False)

        eta_text = f"\n⏳ Tahmini varış: {arrival}"

        gb_text = " (Sıyırma Darbesi)" if is_gb else " (Doğrudan Etki Riski)"

        msg = (
            f"🟡 <b>ASA ERKEN UYARI — CME Tespit Edildi</b>\n"
            f"\n"
            f"Güneş'ten Dünya yönlü bir kütle atımı (CME) algılandı.\n"
            f"\n"
            f"📊 CME Hızı: <b>{speed} km/s</b>\n"
            f"🎯 Yön: <b>{alignment}</b> — {details}\n"
            f"🔭 72 Saatlik Tahmin: <b>{level} Risk</b>{gb_text}\n"
            f"{eta_text}\n"
            f"\n"
            f"🛰️ Etkilenen hedefler: {targets}\n"
            f"\n"
            f"📋 Bu bir tahmindir. Durum değiştikçe güncel bildirimler alacaksınız.\n"
            f"\n"
            f"🕐 {datetime.now(TSI).strftime('%d.%m.%Y %H:%M TSİ')}"
        )

        success = send_telegram(msg)
        log_notification(db, event_id, tier=1, message=msg, success=success)
        if success:
            print(f"[Tier 1] 🟡 Early alert sent for {cme_id}")


# ─────────────────────────────────────────────
#  TIER 2: APPROACH — Arrival within 24 hours
#  Triggers: Known CME with arrival < 24h
#  Timing: 12-24 hours before impact
# ─────────────────────────────────────────────

def check_tier2(db: Session, cme_list: list):
    """
    Check if any Earth-directed CME's estimated arrival is within 24 hours.
    Uses ENLIL estimatedShockArrivalTime for calculation.
    """
    for cme in cme_list:
        if not cme.get("earth_target"):
            continue
        if not cme.get("estimated_arrival"):
            continue

        cme_id = cme["cme_id"]
        event_id = f"tier2_{cme_id}"

        if was_already_sent(db, event_id, tier=2, cooldown_hours=12):
            continue

        # Try to estimate hours remaining from arrival string
        # The arrival format is "DD Month HH:MM TSİ"
        # We need raw UTC from the ENLIL data — but we only have formatted string
        # So we'll look at the raw ENLIL data if available
        arrival_str = cme.get("estimated_arrival", "")

        # Parse "DD Month HH:MM TSİ" format back to datetime
        hours_remaining = None
        for fmt in ["%d %B %H:%M TSİ", "%d %b %H:%M TSİ", "%d %B %H:%M Local", "%d %b %H:%M Local"]:
            try:
                parsed = datetime.strptime(arrival_str, fmt)
                parsed = parsed.replace(year=datetime.now().year, tzinfo=TSI)
                hours_remaining = (parsed - datetime.now(TSI)).total_seconds() / 3600
                break
            except ValueError:
                continue

        if hours_remaining is None or hours_remaining > 24 or hours_remaining < 0:
            continue

        speed = cme.get("speed", "?")
        level = cme.get("level", "?")

        msg = (
            f"🟠 <b>ASA YAKLAŞMA UYARISI — CME 24 Saat İçinde</b>\n"
            f"\n"
            f"Daha önce bildirilen CME Dünya'ya yaklaşıyor.\n"
            f"\n"
            f"📅 Tahmini Varış: <b>{arrival_str}</b>\n"
            f"⏳ Kalan süre: <b>~{hours_remaining:.0f} saat</b>\n"
            f"📊 Hız: {speed} km/s\n"
            f"📋 72 Saatlik Tahmin: <b>{level} Risk</b>\n"
            f"\n"
            f"📋 Öneriler:\n"
            f"• Hassas elektronik cihazların yedeklerini alın\n"
            f"• Uydu haberleşme kesintilerine hazırlıklı olun\n"
            f"• GPS doğruluğunda azalma olabilir\n"
            f"\n"
            f"🕐 {datetime.now(TSI).strftime('%d.%m.%Y %H:%M TSİ')}"
        )

        success = send_telegram(msg)
        log_notification(db, event_id, tier=2, message=msg, success=success)
        if success:
            print(f"[Tier 2] 🟠 Approach warning sent for {cme_id} ({hours_remaining:.0f}h)")


# ─────────────────────────────────────────────
#  TIER 3: IMMINENT — L1 Shockwave Detection
#  Triggers: Sudden Bz drop or speed jump at DSCOVR
#  Timing: 30-60 minutes before Earth impact
# ─────────────────────────────────────────────

def check_tier3(db: Session, noaa_data: dict):
    """
    Detect sudden changes in DSCOVR/L1 data indicating an incoming shockwave.
    A shockwave at L1 means Earth impact in ~30-60 minutes.
    """
    bz = noaa_data.get("bz_gsm")
    speed = noaa_data.get("speed")
    bt = noaa_data.get("bt")

    if bz is None or speed is None:
        return

    # Spike detection thresholds
    # A shockwave typically causes: Bz drops sharply, speed jumps, Bt spikes
    is_spike = False
    spike_reason = ""

    if bz <= -15 and speed >= 500:
        is_spike = True
        spike_reason = f"Bz={bz:.1f} nT, Hız={speed:.0f} km/s — şiddetli manyetik sapma"
    elif bz <= -10 and speed >= 600:
        is_spike = True
        spike_reason = f"Bz={bz:.1f} nT, Hız={speed:.0f} km/s — güçlü şok dalgası"
    elif bt and bt >= 20 and bz <= -10:
        is_spike = True
        spike_reason = f"Bt={bt:.1f} nT, Bz={bz:.1f} nT — yüksek toplam alan"

    if not is_spike:
        return

    today = datetime.utcnow().strftime("%Y%m%d")
    event_id = f"tier3_l1spike_{today}"

    # L1 spike alerts max once per hour
    if was_already_sent(db, event_id, tier=3, cooldown_hours=1):
        return

    delay = noaa_data.get("l1_delay_str", "~45 dakika")

    msg = (
        f"🔴 <b>ACİL — Şok Dalgası L1'de Tespit Edildi!</b>\n"
        f"\n"
        f"DSCOVR uydusu L1 noktasında ani manyetik değişim algıladı.\n"
        f"\n"
        f"🧲 Bz: <b>{bz:.1f} nT</b>\n"
        f"💨 Hız: <b>{speed:.0f} km/s</b>\n"
    )
    if bt:
        msg += f"🔋 Bt: <b>{bt:.1f} nT</b>\n"
    msg += (
        f"\n"
        f"📡 Sebep: {spike_reason}\n"
        f"⏳ Dünya'ya ulaşma süresi: <b>{delay}</b>\n"
        f"\n"
        f"⚡ Manyetik fırtına başlamak üzere olabilir!\n"
        f"\n"
        f"🕐 {datetime.now(TSI).strftime('%d.%m.%Y %H:%M TSİ')}"
    )

    success = send_telegram(msg)
    log_notification(db, event_id, tier=3, message=msg, success=success)
    if success:
        print(f"[Tier 3] 🔴 L1 spike alert sent!")


# ─────────────────────────────────────────────
#  TIER 4: ACTIVE STORM — Geomagnetic storm
#  Triggers: Kp >= 5 (G1+) or final_level HIGH/CRITICAL/EXTREME
#  Timing: Storm is happening NOW
# ─────────────────────────────────────────────

KP_TO_GSCALE = {
    5: ("G1", "Zayıf Fırtına"),
    6: ("G2", "Orta Fırtına"),
    7: ("G3", "Güçlü Fırtına"),
    8: ("G4", "Şiddetli Fırtına"),
    9: ("G5", "Aşırı Fırtına"),
}

def check_tier4(db: Session, kp_data: dict, final_level: str):
    """
    Alert when a geomagnetic storm is actively happening.
    Kp ≥ 5 = G1 or higher.
    """
    kp = kp_data.get("kp_value", 0)
    kp_level = kp_data.get("level", "SAFE")

    # Only trigger for Kp >= 5 OR final weighted level is HIGH/CRITICAL/EXTREME
    should_alert = (kp >= 5) or (final_level in ("HIGH", "CRITICAL", "EXTREME"))

    if not should_alert:
        return

    today = datetime.utcnow().strftime("%Y%m%d")
    event_id = f"tier4_storm_{today}"

    # Active storm alert max once per 3 hours
    if was_already_sent(db, event_id, tier=4, cooldown_hours=3):
        return

    g_scale, g_desc = KP_TO_GSCALE.get(int(kp), ("G1+", "Manyetik Fırtına"))
    if kp < 5:
        g_scale = "—"
        g_desc = "Yüksek Tehdit Seviyesi"

    msg = (
        f"⚫ <b>AKTİF MANYETİK FIRTINA — {g_scale} (Kp={kp:.1f})</b>\n"
        f"\n"
        f"Dünya'da {'güçlü bir manyetik fırtına' if kp >= 7 else 'manyetik fırtına'} devam ediyor.\n"
        f"\n"
        f"🧲 Kp-Index: <b>{kp:.1f}</b> ({g_scale} — {g_desc})\n"
        f"📊 72 Saatlik Tahmin: <b>{final_level} Risk</b>\n"
        f"\n"
        f"⚡ Olası etkiler:\n"
    )

    if kp >= 8:
        msg += "• 🔴 Elektrik şebekesi hasarı riski\n• 🔴 Uydu haberleşmesi ciddi kesinti\n• 🔴 HF radyo tamamen kesilmiş olabilir\n• 🟡 GPS kullanılamaz hale gelebilir\n"
    elif kp >= 6:
        msg += "• 🟠 GPS doğruluğu düşebilir\n• 🟠 HF radyo iletişimi kesilmiş olabilir\n• 🟡 Transformatör gerilim dalgalanmaları\n• 🟢 Kuzey enlemlerinde aurora\n"
    else:
        msg += "• 🟡 GPS doğruluğunda hafif azalma\n• 🟡 HF radyo zayıflayabilir\n• 🟢 Yüksek enlemlerde aurora\n"

    msg += f"\n🕐 {datetime.now(TSI).strftime('%d.%m.%Y %H:%M TSİ')}"

    success = send_telegram(msg)
    log_notification(db, event_id, tier=4, message=msg, success=success)
    if success:
        print(f"[Tier 4] ⚫ Active storm alert sent! Kp={kp}")


# ─────────────────────────────────────────────
#  MASTER CHECK — Called after each scan
# ─────────────────────────────────────────────

def check_all_notifications(db: Session, analysis_result: dict):
    """
    Run all 4 notification tiers against the latest analysis.
    Called by main.py after each periodic scan.
    """
    if not TELEGRAM_CHAT_ID:
        return  # No chat configured

    cme_list = analysis_result.get("cme_list", [])
    noaa = analysis_result.get("noaa", {})
    kp = analysis_result.get("kp", {})
    final_level = analysis_result.get("final_level", "SAFE")

    try:
        # Tier 1: New Earth-directed CME? (1-4 days before)
        check_tier1(db, cme_list)

        # Tier 2: Known CME arriving within 24h?
        check_tier2(db, cme_list)

        # Tier 3: L1 shockwave spike? (30-60 min before)
        check_tier3(db, noaa)

        # Tier 4: Active storm? (happening now)
        check_tier4(db, kp, final_level)

    except Exception as e:
        print(f"[Notification Error] {e}")
