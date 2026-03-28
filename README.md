# ASA Takımı — Güneş Fırtınası API

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
# NASA API anahtarını ayarla (PowerShell)
$env:NASA_API_KEY="senin_anahtarin"

# Sunucuyu başlat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint'ler

| Endpoint | Açıklama |
|---|---|
| `GET /` | Sağlık kontrolü |
| `GET /durum` | Anlık tehdit durumu (cache) |
| `GET /durum/taze` | Anlık tehdit durumu (canlı çek) |
| `GET /gecmis` | Son 50 tehdit kaydı |
| `GET /gecmis/noaa` | NOAA ölçüm geçmişi (grafik için) |
| `GET /gecmis/cme` | CME olay geçmişi |
| `GET /istatistik` | DB istatistikleri |
| `WS /ws` | WebSocket canlı akış |

## Swagger Dokümantasyonu

Sunucu çalışırken: http://localhost:8000/docs

## Veritabanı

SQLite dosyası otomatik oluşturulur: `solar.db`

Tablolar:
- `noaa_olcum` — Her NOAA taraması
- `cme_olayi` — Her CME olayı
- `tehdit_gecmisi` — Birleşik tehdit seviyesi geçmişi

## Proje Yapısı

```
solar_api/
├── main.py          ← FastAPI uygulaması
├── database.py      ← SQLAlchemy modelleri
├── veri_motoru.py   ← NASA + NOAA veri çekme/analiz
├── requirements.txt
└── solar.db         ← Otomatik oluşur
```
