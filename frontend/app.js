const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

// --- i18n Dictionary ---
const i18n = {
    en: {
        appTitle: "ASA Space Weather",
        loading: "Loading...",
        finalThreat: "Final Threat Level",
        systemStarting: "System Starting...",
        magField: "Magnetic Field (Bz)",
        solarOrientation: "Solar Wind Orientation",
        windSpeed: "Wind Speed",
        earthVelocity: "Earth Approach Velocity",
        plasmaDensity: "Plasma Density",
        particleCount: "Particle Count",
        l1Delay: "L1 Delay",
        timeToReach: "Time to reach Earth",
        chartTitle: "24h Bz and Speed History",
        cmeTitle: "Detected CMEs (Last 72h)",
        checkingData: "Checking CME Data...",
        cmeEmpty: "No Coronal Mass Ejection (CME) recorded in the last 72 hours.",
        cmeDetailsTitle: "CME Details",
        solarSource: "Solar Source Location",
        earthFacingDisk: "* Earth-facing disk / ±90° longitude",
        alertTitle: "NEW THREAT LEVEL DETECTED",
        acknowledge: "Acknowledge",
        alertMsgFull: "Space Weather Threat Level is at {LEVEL}! Please check your systems.",
        
        // Values & States
        levelSAFE: "SAFE",
        levelLOW: "LOW",
        levelMEDIUM: "MEDIUM",
        levelHIGH: "HIGH",
        levelCRITICAL: "CRITICAL",
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
        lonText: "Lon"
    },
    tr: {
        appTitle: "ASA Uzay Hava Durumu",
        loading: "Yükleniyor...",
        finalThreat: "Nihai Tehdit Seviyesi",
        systemStarting: "Sistem Başlatılıyor...",
        magField: "Manyetik Alan (Bz)",
        solarOrientation: "Güneş Rüzgarı Yönü",
        windSpeed: "Rüzgar Hızı",
        earthVelocity: "Dünyaya Yaklaşma Hızı",
        plasmaDensity: "Plazma Yoğunluğu",
        particleCount: "Parçacık Sayısı",
        l1Delay: "L1 Gecikmesi",
        timeToReach: "Dünyaya Ulaşma Süresi",
        chartTitle: "Son 24s Bz ve Hız Geçmişi",
        cmeTitle: "Tespit Edilen KKA (Son 72s)",
        checkingData: "KKA Verileri Kontrol Ediliyor...",
        cmeEmpty: "Son 72 saatte kaydedilmiş bir Koronal Kütle Atımı (KKA/CME) tespit edilmedi.",
        cmeDetailsTitle: "CME Detayları",
        solarSource: "Güneş Yüzeyi Çıkış Noktası",
        earthFacingDisk: "* Dünya'ya dönük yüz / ±90° boylam",
        alertTitle: "YENİ TEHDİT SEVİYESİ",
        acknowledge: "Anladım",
        alertMsgFull: "Uzay Hava Durumu Tehdit Seviyesi {LEVEL} aşamasında! Sistemleri kontrol edin.",

        levelSAFE: "GÜVENLİ",
        levelLOW: "DÜŞÜK",
        levelMEDIUM: "ORTA",
        levelHIGH: "YÜKSEK",
        levelCRITICAL: "KRİTİK",
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
        lonText: "Boylam"
    }
};

let currentLang = 'tr'; // Default logic user requested functionality
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

const modal = document.getElementById("alert-modal");
const alertMsg = document.getElementById("alert-msg");
const closeModalBtn = document.getElementById("close-modal");

const cmeModal = document.getElementById("cme-detail-modal");
const closeCmeModalBtn = document.getElementById("close-cme-modal");
const cmeMarker = document.getElementById("cme-marker");
const cmeInfoList = document.getElementById("cme-detail-info");
const cmeDetailTitle = document.getElementById("cme-detail-title");

let chartInstance = null;
let currentThreatLevel = null;
let globalDataCache = null; // Store latest data to quickly refresh on lang swap

// Language Toggles
document.getElementById("lang-en").addEventListener("click", () => setLang('en'));
document.getElementById("lang-tr").addEventListener("click", () => setLang('tr'));

function setLang(lang) {
    currentLang = lang;
    document.getElementById("lang-en").classList.toggle("active", lang === 'en');
    document.getElementById("lang-tr").classList.toggle("active", lang === 'tr');
    
    // Update static HTML data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.innerText = t(el.getAttribute('data-i18n'));
    });
    
    // Refresh dynamic data
    if (globalDataCache) {
        updateDashboard(globalDataCache);
    }
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
    
    ws.onopen = () => console.log("WebSocket connection established.");
    ws.onmessage = (event) => {
        globalDataCache = JSON.parse(event.data);
        console.log("Live WebSocket Data:", globalDataCache);
        updateDashboard(globalDataCache);
    };
    ws.onclose = () => {
        console.warn("WebSocket closed. Retrying in 5 seconds...");
        setTimeout(setupWebSocket, 5000);
    };
    ws.onerror = (err) => console.error("WebSocket error:", err);
}

function updateDashboard(data) {
    if (!data || !data.final_level) return;

    // 1. Main Banner
    const newTarget = data.final_level;
    const localizedLevel = tLevels(newTarget);
    threatLevelEl.innerText = localizedLevel;
    
    // Clear and set classes
    const classMap = {
        "SAFE": "level-safe",
        "LOW": "level-low",
        "MEDIUM": "level-medium",
        "HIGH": "level-high",
        "CRITICAL": "level-critical",
        "UNKNOWN": "level-unknown"
    };

    threatLevelEl.className = `threat-level ${classMap[newTarget] || 'level-unknown'}`;
    threatDescEl.innerText = `${t('determiner')}: ${data.determiner || '—'} | ${t('lastUpdate')}: ${data.timestamp}`;

    // Alert Modal Logic
    if (["HIGH", "CRITICAL"].includes(newTarget) && newTarget !== currentThreatLevel && currentThreatLevel !== null) {
        alertMsg.innerText = t("alertMsgFull").replace("{LEVEL}", localizedLevel);
        modal.classList.remove("hidden");
    }
    currentThreatLevel = newTarget;

    // 2. NOAA Live Data Panel Update
    const noaa = data.noaa || {};
    
    bzValueEl.innerText = (noaa.bz_gsm !== null && noaa.bz_gsm !== undefined) ? noaa.bz_gsm : "--";
    bzValueEl.className = (noaa.bz_gsm < -5) ? "value status-negative" : "value status-neutral";

    windSpeedEl.innerText = (noaa.speed) ? noaa.speed : "--";
    windSpeedEl.className = (noaa.speed > 600) ? "value status-negative" : "value status-neutral";

    densityEl.innerText = (noaa.density) ? noaa.density : "--";
    densityEl.className = (noaa.density > 15) ? "value status-negative" : "value status-neutral";

    l1DelayEl.innerText = (noaa.l1_delay_str) ? noaa.l1_delay_str : "--";

    // 3. NASA CME List
    let cmeList = data.cme_list || [];
    
    // Sort array so newest is at the top (descending by cme_id since it contains date like 2024-05-10)
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

    // Refresh chart dynamically
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
        const res = await fetch(`${API_BASE}/history/noaa?limit=30`); // Last 30 points
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


// Start
document.addEventListener('DOMContentLoaded', init);

// CME Details Logic
const colorMap = {
    "SAFE": "var(--accent-safe)",
    "LOW": "var(--accent-low)",
    "MEDIUM": "var(--accent-mid)",
    "HIGH": "var(--accent-high)",
    "CRITICAL": "var(--accent-crit)",
    "UNKNOWN": "var(--accent-unknown)"
};

function showCmeDetails(cme) {
    cmeDetailTitle.innerText = `CME: ${cme.cme_id || t('unknown')}`;
    
    const lon = parseFloat(cme.longitude);
    const lat = parseFloat(cme.latitude);
    const textColor = colorMap[cme.level] || colorMap["UNKNOWN"];
    
    // High-contrast marker colors for the sun background
    const markerContrastMap = {
        "SAFE": "#22c55e",       // Bright Green
        "LOW": "#3b82f6",        // Bright Blue
        "MEDIUM": "#a855f7",     // Purple
        "HIGH": "#000000",       // Black
        "CRITICAL": "#ffffff",   // White
        "UNKNOWN": "#64748b"     // Slate
    };
    const markerColor = markerContrastMap[cme.level] || markerContrastMap["UNKNOWN"];
    
    cmeMarker.style.backgroundColor = markerColor;
    cmeMarker.style.border = cme.level === "CRITICAL" ? "3px solid #ef4444" : "3px solid #ffffff";
    cmeMarker.style.boxShadow = "0 0 15px rgba(0,0,0,0.9)";
    
    if (!isNaN(lon) && !isNaN(lat)) {
        let targetTop = 50 - (lat / 90) * 50;
        let targetLeft = 50 + (lon / 90) * 50;
        
        if (targetLeft < 0) targetLeft = 0;
        if (targetLeft > 100) targetLeft = 100;
        if (targetTop < 0) targetTop = 0;
        if (targetTop > 100) targetTop = 100;
        
        cmeMarker.style.top = `${targetTop}%`;
        cmeMarker.style.left = `${targetLeft}%`;
        cmeMarker.style.display = 'block';
    } else {
        cmeMarker.style.display = 'none';
    }
    
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
