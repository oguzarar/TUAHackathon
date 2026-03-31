const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

// --- i18n Dictionary ---
const i18n = {
    en: {
        appTitle: "ASA Space Weather",
        loading: "Loading...",
        finalThreat: "72-Hour Forecast",
        systemStarting: "System Starting...",
        magField: "Magnetic Field (Bz)",
        solarOrientation: "Solar Wind Orientation",
        windSpeed: "Wind Speed",
        earthVelocity: "Earth Approach Velocity",
        plasmaDensity: "Plasma Density",
        particleCount: "Particle Count",
        l1Delay: "L1 Delay",
        timeToReach: "Time to reach Earth",
        chartTitle: "Bz and Speed History",
        cmeTitle: "Detected CMEs (Last 72h)",
        checkingData: "Checking Data...",
        cmeEmpty: "No Coronal Mass Ejection (CME) recorded in the last 72 hours.",
        cmeDetailsTitle: "CME Details",
        solarSource: "Solar Source Location",
        earthFacingDisk: "* Earth-facing disk / ±90° longitude",
        alertTitle: "NEW THREAT LEVEL DETECTED",
        acknowledge: "Acknowledge",
        alertMsgFull: "Space Weather Threat Level is at {LEVEL}! Please check your systems.",
        kpTitle: "Geomagnetic Kp-Index",
        flareTitle: "Solar Flares (Last 72h)",
        flareDetailsTitle: "Solar Flare Details",
        flrEmpty: "No significant solar flares detected.",
        detailFlareClass: "Flare Class",
        detailBeginTime: "Begin Time",
        detailPeakTime: "Peak Time",
        detailEndTime: "End Time",
        
        // Values & States
        levelSAFE: "SAFE",
        levelLOW: "LOW",
        levelMEDIUM: "MEDIUM",
        levelHIGH: "HIGH",
        levelCRITICAL: "CRITICAL",
        levelEXTREME: "EXTREME",
        levelUNKNOWN: "UNKNOWN",

        alignDIRECT: "DIRECT",
        alignEDGE: "EDGE",
        alignFAR: "FAR",
        alignUNKNOWN: "UNKNOWN",
        
        targetEarth: "EARTH TARGET: Arrival ~",
        targetNotEarth: "Not directed at Earth",
        
        detailThreatLevel: "Threat Level",
        detailSpeed: "CME Speed",
        detailAngle: "Half Angle",
        detailCoords: "Coordinates",
        detailAlignment: "Earth Alignment",
        detailTargets: "Impact Targets",
        detailArrival: "Estimated Arrival",
        detailL1: "L1 Delay",
        
        noData: "No Data",
        calculating: "Calculating",
        notEarthDirected: "Not Earth Directed",
        none: "None",
        unknown: "Unknown",
        determiner: "Determiner",
        lastUpdate: "Last Update",
        connError: "CONNECTION ERROR",
        connErrorDesc: "Backend server unreachable. Make sure FastAPI is running.",
        latText: "Lat",
        lonText: "Longitude",
        lblNow: "NOW (Kp):",
        lblFuture: "72h FORECAST (ASA):",
        
        impSat: "Satellites", impGrid: "Power Grid", impRadio: "Comms (HF)", impGps: "Navigation",
        impact_sat_SAFE: "Optimal conditions", impact_grid_SAFE: "No impact detected", impact_radio_SAFE: "Stable bands", impact_gps_SAFE: "Precision nominal",
        impact_sat_LOW: "Minor charging", impact_grid_LOW: "No impact detected", impact_radio_LOW: "Slight HF fade", impact_gps_LOW: "Precision nominal",
        impact_sat_MEDIUM: "Surface charging req.", impact_grid_MEDIUM: "Minor grid fluct.", impact_radio_MEDIUM: "HF fade in poles", impact_gps_MEDIUM: "Meter-level errors",
        impact_sat_HIGH: "Warning: Charging risk", impact_grid_HIGH: "Voltage alarms", impact_radio_HIGH: "Blackout in poles", impact_gps_HIGH: "Tens of meters errors",
        impact_sat_CRITICAL: "Safe Mode Required", impact_grid_CRITICAL: "Grid collapse risk", impact_radio_CRITICAL: "Global HF blackout", impact_gps_CRITICAL: "Navigation failure",
        impact_sat_EXTREME: "EVASIVE MANEUVERS", impact_grid_EXTREME: "CATASTROPHIC COLLAPSE", impact_radio_EXTREME: "TOTAL BLACKOUT", impact_gps_EXTREME: "TOTAL SIGNAL LOSS",
    },
    tr: {
        appTitle: "ASA Uzay Hava Durumu",
        loading: "Yükleniyor...",
        finalThreat: "72 Saatlik Tahmin",
        systemStarting: "Sistem Başlatılıyor...",
        magField: "Manyetik Alan (Bz)",
        solarOrientation: "Güneş Rüzgarı Yönü",
        windSpeed: "Rüzgar Hızı",
        earthVelocity: "Dünyaya Yaklaşma Hızı",
        plasmaDensity: "Plazma Yoğunluğu",
        particleCount: "Parçacık Sayısı",
        l1Delay: "L1 Gecikmesi",
        timeToReach: "Dünyaya Ulaşma Süresi",
        chartTitle: "Bz ve Hız Geçmişi",
        cmeTitle: "Tespit Edilen KKA (Son 72s)",
        checkingData: "Veriler Kontrol Ediliyor...",
        cmeEmpty: "Son 72 saatte kaydedilmiş bir Koronal Kütle Atımı (KKA/CME) tespit edilmedi.",
        cmeDetailsTitle: "CME Detayları",
        solarSource: "Güneş Yüzeyi Çıkış Noktası",
        earthFacingDisk: "* Dünya'ya dönük yüz / ±90° boylam",
        alertTitle: "YENİ TEHDİT SEVİYESİ",
        acknowledge: "Anladım",
        alertMsgFull: "Uzay Hava Durumu Tehdit Seviyesi {LEVEL} aşamasında! Sistemleri kontrol edin.",
        kpTitle: "Jeomanyetik Kp-İndeksi",
        flareTitle: "Güneş Patlamaları (Son 72s)",
        flareDetailsTitle: "Güneş Patlaması (Flare) Detayları",
        flrEmpty: "Önemli bir güneş patlaması (Flare) tespit edilmedi.",
        detailFlareClass: "Patlama Sınıfı",
        detailBeginTime: "Başlangıç Zamanı",
        detailPeakTime: "Zirve (Peak) Zamanı",
        detailEndTime: "Bitiş Zamanı",

        levelSAFE: "GÜVENLİ",
        levelLOW: "DÜŞÜK",
        levelMEDIUM: "ORTA",
        levelHIGH: "YÜKSEK",
        levelCRITICAL: "KRİTİK",
        levelEXTREME: "EKSTREM",
        levelUNKNOWN: "BİLİNMİYOR",

        alignDIRECT: "DİREKT",
        alignEDGE: "KENAR",
        alignFAR: "UZAK",
        alignUNKNOWN: "BİLİNMİYOR",
        
        targetEarth: "DÜNYA HEDEFTE: Varış ~",
        targetNotEarth: "Dünya'ya yönelmiş değil",
        
        detailThreatLevel: "Tehdit Durumu",
        detailSpeed: "Çıkış Hızı",
        detailAngle: "Uzamsal Açı (Yarım)",
        detailCoords: "Koordinatlar",
        detailAlignment: "Dünyaya Hizalama",
        detailTargets: "Etkilenecek Hedefler",
        detailArrival: "Tahmini Varış",
        detailL1: "L1 Ulaşma Gecikmesi",
        
        noData: "Veri Yok",
        calculating: "Hesaplanıyor",
        notEarthDirected: "Dünya Hedefte Değil",
        none: "Yok",
        unknown: "Bilinmiyor",
        determiner: "Belirleyen",
        lastUpdate: "Son Güncelleme",
        connError: "BAĞLANTI HATASI",
        connErrorDesc: "Sunucuya ulaşılamıyor. FastAPI'nin çalıştığından emin olun.",
        latText: "Enlem",
        lonText: "Boylam",
        lblNow: "ŞU AN (Kp):",
        lblFuture: "72s TAHMİN (ASA):",
        
        impSat: "Uydular", impGrid: "Elektrik Şb.", impRadio: "İletişim (HF)", impGps: "Navigasyon",
        impact_sat_SAFE: "Optimal koşullar", impact_grid_SAFE: "Etki gözlenmedi", impact_radio_SAFE: "Bantlar stabil", impact_gps_SAFE: "Hassasiyet normal",
        impact_sat_LOW: "Hafif sürtünme", impact_grid_LOW: "Etki gözlenmedi", impact_radio_LOW: "Hafif sinyal kaybı", impact_gps_LOW: "Hassasiyet normal",
        impact_sat_MEDIUM: "Sürtünme uyarısı", impact_grid_MEDIUM: "Dalgalanmalar bşld.", impact_radio_MEDIUM: "Kutuplarda kesinti", impact_gps_MEDIUM: "Metrelik sapmalar",
        impact_sat_HIGH: "Şarj riski yüksek", impact_grid_HIGH: "Voltaj alarmları", impact_radio_HIGH: "Radyo kararması (HF)", impact_gps_HIGH: "Onlarca metre sapma",
        impact_sat_CRITICAL: "Güvenli mod şart", impact_grid_CRITICAL: "Şebeke çökme riski", impact_radio_CRITICAL: "Küresel HF kesintisi", impact_gps_CRITICAL: "Sinyal kaybı uyarısı",
        impact_sat_EXTREME: "KORUMA PROSEDÜRÜ", impact_grid_EXTREME: "TAM ÇÖKÜŞ SENARYOSU", impact_radio_EXTREME: "KÜRESEL BLACKOUT", impact_gps_EXTREME: "TÜM SİNYALLER KOPUK",
    }
};

let currentLang = 'tr';
function t(key) { return i18n[currentLang][key] || key; }
function tLevels(val) { if(!val) return t("unknown"); return t("level" + val) || val; }
// --- End i18n ---

// DOM Elements
const timeEl = document.getElementById("current-time");
const threatLevelEl = document.getElementById("final-level");
const threatDescEl = document.getElementById("threat-determiner");

const bzValueEl = document.getElementById("bz-value");
const windSpeedEl = document.getElementById("wind-speed");
const densityEl = document.getElementById("density");
const l1DelayEl = document.getElementById("l1-delay");
const cmeListEl = document.getElementById("cme-list");
const flrListEl = document.getElementById("flr-list");

const kpDisplay = document.getElementById("kp-display");
const kpMeterBg = document.getElementById("kp-meter-bg");
const kpStatusText = document.getElementById("kp-status-text");

const modal = document.getElementById("alert-modal");
const alertMsg = document.getElementById("alert-msg");
const closeModalBtn = document.getElementById("close-modal");

const cmeModal = document.getElementById("cme-detail-modal");
const closeCmeModalBtn = document.getElementById("close-cme-modal");
const cmeMarker = document.getElementById("cme-marker");
const cmeInfoList = document.getElementById("cme-detail-info");
const cmeDetailTitle = document.getElementById("cme-detail-title");

const flrModal = document.getElementById("flr-detail-modal");
const closeFlrModalBtn = document.getElementById("close-flr-modal");
const flrInfoList = document.getElementById("flr-detail-info");
const flrDetailTitle = document.getElementById("flr-detail-title");
const flrMarker = document.getElementById("flr-marker");

let chartInstance = null;
let currentThreatLevel = null;
let globalDataCache = null;

// Language Toggles
document.getElementById("lang-en").addEventListener("click", () => setLang('en'));
document.getElementById("lang-tr").addEventListener("click", () => setLang('tr'));

function setLang(lang) {
    currentLang = lang;
    document.getElementById("lang-en").classList.toggle("active", lang === 'en');
    document.getElementById("lang-tr").classList.toggle("active", lang === 'tr');
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.innerText = t(el.getAttribute('data-i18n'));
    });
    
    if (globalDataCache) updateDashboard(globalDataCache);
}

// Clock
setInterval(() => {
    const now = new Date();
    const locTime = now.toLocaleTimeString(currentLang === 'tr' ? 'tr-TR' : 'en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const gmtTime = now.toLocaleTimeString('en-GB', { timeZone: 'UTC', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    const localStr = currentLang === 'tr' ? 'Yerel' : 'Local';
    timeEl.innerText = `${localStr}: ${locTime} | GMT: ${gmtTime}`;
}, 1000);

// Initialize
async function init() {
    closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
    closeCmeModalBtn.addEventListener('click', () => cmeModal.classList.add('hidden'));
    closeFlrModalBtn.addEventListener('click', () => flrModal.classList.add('hidden'));

    setLang('tr');

    try {
        await initChart();
        await fetchInitialData();
        setupWebSocket();
    } catch (e) {
        console.error("Initialization error:", e);
        threatLevelEl.innerText = t("connError");
        threatLevelEl.className = "threat-level level-unknown";
        threatDescEl.innerText = t("connErrorDesc");
    }
}

async function fetchInitialData() {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Status data could not be fetched.");
    const data = await res.json();
    globalDataCache = data;
    updateDashboard(globalDataCache);
}

function setupWebSocket() {
    const ws = new WebSocket(`${WS_BASE}/ws`);
    ws.onmessage = (event) => {
        globalDataCache = JSON.parse(event.data);
        updateDashboard(globalDataCache);
    };
    ws.onclose = () => setTimeout(setupWebSocket, 5000);
}

function updateDashboard(data) {
    if (!data) return;

    // 1. Main Banner
    const newTarget = data.forecast_level || data.final_level; // Use forecast
    const localizedLevel = tLevels(newTarget);
    threatLevelEl.innerText = localizedLevel;
    
    const classMap = {
        "SAFE": "level-safe", "LOW": "level-low", "MEDIUM": "level-medium",
        "HIGH": "level-high", "CRITICAL": "level-critical", "EXTREME": "level-extreme", "UNKNOWN": "level-unknown"
    };

    threatLevelEl.className = `threat-level ${classMap[newTarget] || 'level-unknown'}`;
    
    // Use forecast description if available, else determiner
    const descText = data.forecast_description ? data.forecast_description : (`${t('determiner')}: ${data.determiner || '—'}`);
    threatDescEl.innerText = `${descText} | ${t('lastUpdate')}: ${data.timestamp}`;

    // Alert Modal Logic
    if (["HIGH", "CRITICAL", "EXTREME"].includes(newTarget) && newTarget !== currentThreatLevel && currentThreatLevel !== null) {
        alertMsg.innerText = t("alertMsgFull").replace("{LEVEL}", localizedLevel);
        modal.classList.remove("hidden");
    }
    currentThreatLevel = newTarget;

    // Infrastructure Impact Logic
    const impactColorMap = {
        "SAFE": "val-safe", "LOW": "val-low", "MEDIUM": "val-medium",
        "HIGH": "val-high", "CRITICAL": "val-critical", "EXTREME": "val-extreme", "UNKNOWN": "val-safe"
    };
    const nowLevel = (data.kp && data.kp.level) ? data.kp.level : "SAFE";
    const futureLevel = data.forecast_level || data.final_level || "SAFE";

    ["sat", "grid", "radio", "gps"].forEach(sys => {
        const cardEl = document.getElementById(`impact-${sys}`);
        const nowSpan = document.getElementById(`text-${sys}-now`);
        const futureSpan = document.getElementById(`text-${sys}-future`);
        
        if (cardEl) {
             // Card overall class follows futureLevel for border/bg highlight
             cardEl.className = `impact-card impact-${futureLevel.toLowerCase()}`;
        }
        if (nowSpan) {
            nowSpan.innerText = t(`impact_${sys}_${nowLevel}`) || t("unknown");
            nowSpan.className = `desc-val ${impactColorMap[nowLevel]}`;
        }
        if (futureSpan) {
            futureSpan.innerText = t(`impact_${sys}_${futureLevel}`) || t("unknown");
            futureSpan.className = `desc-val ${impactColorMap[futureLevel]}`;
        }
    });

    // 2. NOAA Live Data Panel
    const noaa = data.noaa || {};
    bzValueEl.innerText = (noaa.bz_gsm !== null && noaa.bz_gsm !== undefined) ? noaa.bz_gsm : "--";
    bzValueEl.className = (noaa.bz_gsm < -5) ? "value status-negative" : "value status-neutral";
    windSpeedEl.innerText = (noaa.speed) ? noaa.speed : "--";
    windSpeedEl.className = (noaa.speed > 600) ? "value status-negative" : "value status-neutral";
    densityEl.innerText = (noaa.density) ? noaa.density : "--";
    densityEl.className = (noaa.density > 15) ? "value status-negative" : "value status-neutral";
    l1DelayEl.innerText = (noaa.l1_delay_str) ? noaa.l1_delay_str : "--";

    // 3. Kp-Index Panel
    const kpData = data.kp || {};
    const kpVal = kpData.kp_value !== undefined ? kpData.kp_value : 0;
    const kpLevel = kpData.level || "UNKNOWN";
    
    kpDisplay.innerText = kpVal.toFixed(1);
    kpStatusText.innerText = tLevels(kpLevel);
    kpStatusText.className = `kp-status-text ${classMap[kpLevel]}`;
    
    // Gauge Color Gradient
    let gaugeColor = "rgba(16, 185, 129, 0.4)"; // Safe
    if(kpVal >= 7) gaugeColor = "rgba(239, 68, 68, 0.6)"; // Crit
    else if(kpVal >= 5) gaugeColor = "rgba(249, 115, 22, 0.5)"; // High
    else if(kpVal >= 4) gaugeColor = "rgba(245, 158, 11, 0.4)"; // Med
    else if(kpVal >= 3) gaugeColor = "rgba(59, 130, 246, 0.4)"; // Low
    
    kpMeterBg.style.background = `radial-gradient(circle at bottom, ${gaugeColor} 0%, rgba(15, 23, 42, 1) 100%)`;

    // 4. NASA Flares Panel
    let flrList = data.flr_list || [];
    // Sort so X-class and most recent are prioritized. 
    // Simply descending by begin_time or flare_id works for recent.
    flrList.sort((a, b) => b.flare_id.localeCompare(a.flare_id));
    
    flrListEl.innerHTML = "";
    if (flrList.length === 0) {
        flrListEl.innerHTML = `<p class="empty-cme">${t('flrEmpty')}</p>`;
    } else {
        flrList.forEach(flr => {
            const baseClass = flr.class_type.charAt(0);
            const item = document.createElement("div");
            item.className = "flr-item";
            item.onclick = () => showFlrDetails(flr);
            item.innerHTML = `
                <div class="flr-info">
                    <span class="flr-id">${flr.flare_id}</span>
                    <span class="flr-time">${flr.begin_time}</span>
                </div>
                <div class="flr-class ${baseClass}">${flr.class_type}</div>
            `;
            flrListEl.appendChild(item);
        });
    }

    // 5. NASA CME List
    let cmeList = data.cme_list || [];
    cmeList.sort((a, b) => b.cme_id.localeCompare(a.cme_id));

    cmeListEl.innerHTML = "";
    if (cmeList.length === 0) {
        cmeListEl.innerHTML = `<p class="empty-cme">${t('cmeEmpty')}</p>`;
    } else {
        cmeList.forEach(cme => {
            const isEarthTarget = cme.earth_target;
            let htmlTargetClass = isEarthTarget ? "target-earth" : "";
            let htmlTargetText = isEarthTarget 
                ? `<div class="cme-arrival"><i class="fa-solid fa-earth-americas"></i> ${t('targetEarth')} ${cme.estimated_arrival || t('unknown')}</div>`
                : `<div style="font-size: 0.8rem; color: var(--accent-safe); margin-top: 5px;">${t('targetNotEarth')} (${t("align"+cme.alignment) || cme.alignment})</div>`;

            const item = document.createElement("div");
            item.className = `cme-item ${htmlTargetClass}`;
            item.onclick = () => showCmeDetails(cme);
            item.innerHTML = `
                <div class="cme-header">
                    <span class="cme-id">${cme.cme_id || t('unknown')}</span>
                    <span class="cme-level ${classMap[cme.level]}">${tLevels(cme.level)}</span>
                </div>
                <div class="cme-details">
                    <div class="cme-detail-item">
                        <span class="cme-detail-label">${t('detailSpeed')}</span>
                        <span class="cme-detail-value">${cme.speed ? cme.speed + " km/s" : t('noData')}</span>
                    </div>
                    <div class="cme-detail-item">
                        <span class="cme-detail-label">${t('detailL1')}</span>
                        <span class="cme-detail-value">${cme.l1_delay || t('noData')}</span>
                    </div>
                </div>
                ${htmlTargetText}
            `;
            cmeListEl.appendChild(item);
        });
    }

    updateChart();
}


// Chart.js Setup
async function initChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Bz (nT)',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Speed (km/s)',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top' },
                tooltip: { backgroundColor: 'rgba(10, 14, 23, 0.9)' }
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Bz (nT)' } },
                y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Speed (km/s)' } }
            }
        }
    });

    await updateChart();
}

async function updateChart() {
    try {
        const res = await fetch(`${API_BASE}/history/noaa?limit=30`);
        if (!res.ok) return;
        let data = await res.json();
        
        data = data.reverse();
        const labels = data.map(repo => {
            const timeParts = repo.time.split(' ');
            return timeParts[1] || repo.time; 
        });
        const bzData = data.map(repo => repo.bz_gsm);
        const speedData = data.map(repo => repo.speed);

        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = bzData;
        chartInstance.data.datasets[1].data = speedData;
        chartInstance.update();
    } catch (e) {
        console.warn("Chart data fetch error", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    generateStarfield();
    init();
});

// ═══ Starfield Generator ═══
function generateStarfield() {
    const container = document.getElementById('starfield');
    if (!container) return;

    const starCount = 220;
    const colors = [
        'rgba(255, 255, 255,',       // Pure white
        'rgba(200, 220, 255,',       // Cool blue-white  
        'rgba(180, 200, 255,',       // Blue
        'rgba(255, 240, 200,',       // Warm yellow
        'rgba(255, 200, 180,',       // Warm orange (rare)
    ];

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');

        // Random position
        const x = Math.random() * 100;
        const y = Math.random() * 100;

        // Size tiers: 70% small, 20% medium, 10% large
        const rand = Math.random();
        let size, opacity, glow;
        if (rand < 0.7) {
            // Small stars
            size = 1 + Math.random() * 1.5;  // 1-2.5px
            opacity = 0.3 + Math.random() * 0.4;
            glow = '';
        } else if (rand < 0.9) {
            // Medium stars
            size = 2 + Math.random() * 1.5;  // 2-3.5px
            opacity = 0.5 + Math.random() * 0.4;
            glow = `0 0 ${size * 2}px rgba(200, 220, 255, 0.3)`;
        } else {
            // Large bright stars
            size = 3 + Math.random() * 2;  // 3-5px
            opacity = 0.7 + Math.random() * 0.3;
            glow = `0 0 ${size * 3}px rgba(200, 220, 255, 0.5), 0 0 ${size * 6}px rgba(100, 150, 255, 0.2)`;
        }

        // Random color (more whites, fewer warm tones)
        const colorRand = Math.random();
        let color;
        if (colorRand < 0.5) color = colors[0];
        else if (colorRand < 0.75) color = colors[1];
        else if (colorRand < 0.88) color = colors[2];
        else if (colorRand < 0.96) color = colors[3];
        else color = colors[4];

        star.style.left = `${x}%`;
        star.style.top = `${y}%`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.background = `${color}${opacity})`;
        if (glow) star.style.boxShadow = glow;

        // Random twinkle animation (60% of stars twinkle)
        if (Math.random() < 0.6) {
            const twinkleClass = `twinkle-${Math.ceil(Math.random() * 4)}`;
            star.classList.add(twinkleClass);
            star.style.animationDelay = `${Math.random() * 5}s`;
        }

        container.appendChild(star);
    }

    // Shooting stars — one every 8-15 seconds
    setInterval(() => {
        spawnShootingStar(container);
    }, 8000 + Math.random() * 7000);
}

function spawnShootingStar(container) {
    const star = document.createElement('div');
    star.classList.add('shooting-star');

    star.style.left = `${10 + Math.random() * 60}%`;
    star.style.top = `${5 + Math.random() * 40}%`;

    // Random direction
    const angle = 20 + Math.random() * 30; // degrees
    const distance = 200 + Math.random() * 300;
    star.style.setProperty('--shoot-x', `${distance}px`);
    star.style.setProperty('--shoot-y', `${Math.tan(angle * Math.PI / 180) * distance}px`);

    container.appendChild(star);

    // Trigger animation
    requestAnimationFrame(() => {
        star.classList.add('active');
    });

    // Remove after animation
    setTimeout(() => star.remove(), 1500);
}

// CME Details
const colorMap = {
    "SAFE": "var(--accent-safe)", "LOW": "var(--accent-low)", "MEDIUM": "var(--accent-mid)",
    "HIGH": "var(--accent-high)", "CRITICAL": "var(--accent-crit)", "EXTREME": "var(--accent-extreme)", "UNKNOWN": "var(--accent-unknown)"
};

const markerContrastMap = {
    "SAFE": "#22c55e", "LOW": "#3b82f6", "MEDIUM": "#a855f7",
    "HIGH": "#000000", "CRITICAL": "#ffffff", "EXTREME": "#000000", "UNKNOWN": "#64748b"
};

function positionMarker(marker, lat, lon, level) {
    marker.style.backgroundColor = markerContrastMap[level] || markerContrastMap["UNKNOWN"];
    marker.style.border = (level === "CRITICAL" || level === "EXTREME") ? "3px solid #ef4444" : "3px solid #ffffff";
    marker.style.boxShadow = "0 0 15px rgba(0,0,0,0.9)";
    if (!isNaN(lon) && !isNaN(lat)) {
        let top = 50 - (lat / 90) * 50;
        let left = 50 + (lon / 90) * 50;
        top = Math.max(0, Math.min(100, top));
        left = Math.max(0, Math.min(100, left));
        marker.style.top = `${top}%`;
        marker.style.left = `${left}%`;
        marker.style.display = 'block';
    } else {
        marker.style.display = 'none';
    }
}

function showCmeDetails(cme) {
    cmeDetailTitle.innerText = `CME: ${cme.cme_id || t('unknown')}`;
    const lon = parseFloat(cme.longitude);
    const lat = parseFloat(cme.latitude);
    const textColor = colorMap[cme.level] || colorMap["UNKNOWN"];
    
    positionMarker(cmeMarker, lat, lon, cme.level);
    
    const fields = [
        { label: t("detailThreatLevel"), value: `<span style="color: ${textColor}; font-weight:800">${tLevels(cme.level)}</span>` },
        { label: t("detailSpeed"), value: cme.speed ? `${cme.speed} km/s` : t('noData') },
        { label: t("detailAngle"), value: cme.half_angle ? `${cme.half_angle}°` : t('noData') },
        { label: t("detailCoords"), value: (!isNaN(lon) && !isNaN(lat)) ? `${t('latText')}: ${lat}°, ${t('lonText')}: ${lon}°` : t('noData') },
        { label: t("detailAlignment"), value: t("align"+cme.alignment) || cme.alignment || t("unknown") },
        { label: t("detailTargets"), value: cme.targets || t('none') },
        { label: t("detailArrival"), value: cme.estimated_arrival || (cme.earth_target ? t('calculating') : t('notEarthDirected')) },
        { label: t("detailL1"), value: cme.l1_delay || "N/A" }
    ];
    
    cmeInfoList.innerHTML = fields.map(f => `
        <div class="info-row">
            <span class="info-label">${f.label}</span>
            <span class="info-value">${f.value}</span>
        </div>
    `).join('');
    
    cmeModal.classList.remove("hidden");
}

function showFlrDetails(flr) {
    flrDetailTitle.innerText = `${t('flareDetailsTitle')}: ${flr.flare_id || t('unknown')}`;
    const textColor = colorMap[flr.level] || colorMap["UNKNOWN"];
    
    const lat = parseFloat(flr.latitude);
    const lon = parseFloat(flr.longitude);
    positionMarker(flrMarker, lat, lon, flr.level);
    
    const fields = [
        { label: t("detailThreatLevel"), value: `<span style="color: ${textColor}; font-weight:800">${tLevels(flr.level)}</span>` },
        { label: t("detailFlareClass"), value: flr.class_type ? `<strong class="flr-class ${flr.class_type.charAt(0)}" style="font-size:1.1rem">${flr.class_type}</strong>` : t('noData') },
        { label: t("detailCoords"), value: (!isNaN(lat) && !isNaN(lon)) ? `${t('latText')}: ${lat.toFixed(1)}°, ${t('lonText')}: ${lon.toFixed(1)}° (${flr.source_location})` : t('noData') },
        { label: t("detailBeginTime"), value: flr.begin_time || t('noData') },
        { label: t("detailPeakTime"), value: flr.peak_time || t('noData') },
        { label: t("detailEndTime"), value: flr.end_time || t('noData') }
    ];
    
    flrInfoList.innerHTML = fields.map(f => `
        <div class="info-row">
            <span class="info-label">${f.label}</span>
            <span class="info-value">${f.value}</span>
        </div>
    `).join('');
    
    flrModal.classList.remove("hidden");
}
