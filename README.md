#  SpatialHub – IoT Telemetry Platform for Indoor Farming

**SpatialHub** is a full-stack cloud-enabled telemetry system for real-time monitoring and management of indoor farms. It integrates remote IoT devices, Google Cloud services, a Django REST API, and a modern React + TypeScript dashboard. The system ingests sensor data from distributed hubs, enriches it with farm metadata, stores it in PostgreSQL, and visualizes it for operational insight.

---

##  Tech Stack

###  Backend
- **Django 4.2** + **Django REST Framework**
- **PostgreSQL** (Google Cloud SQL)
- **Google Cloud Run** (Django API hosting)
- **Google Cloud Functions** (Data ingestion + enrichment)
- **Google Cloud Pub/Sub** (Telemetry stream)
- **Docker** (Deployment containerization)

###  Frontend
- **React 18+** with **TypeScript**
- **Vite** for fast builds
- **Axios** for HTTP communication
- **Chart.js + react-chartjs-2** (for visualization - WIP)
- **Tailwind CSS** (optional styling)

---

##  System Architecture

```plaintext
IoT Devices (Raspberry Pi)
   |
   | HTTP POST (Sensor Readings)
   |
Cloud Function: ingest_data_publisher
   |
   | Publishes to Pub/Sub (spatialhub-ingest)
   |
Cloud Function: enrich_data_subscriber
   |--> raw_sensor_data (PostgreSQL)
   |--> enriched_sensor_data (PostgreSQL with metadata)
   |
Django API (Cloud Run)
   |
   |--> /api/raw/          (20 per page)
   |--> /api/enriched/     (20 per page)
   |--> /api/hub/          (GET/POST hub metadata)
   |--> /api/send-command/ (Issue control commands)
   |
React Frontend (Firebase Hosting)

```
## Database Schema

### `hub_config` – Stores hub metadata

| Column   | Type   | Description               |
|----------|--------|---------------------------|
| id       | INT    | Auto-increment primary key|
| hub_id   | STRING | Unique 20-character ID    |
| location | STRING | Physical location         |
| owner    | JSON   | Owner(s) as array         |
| workers  | JSON   | Worker(s) as array        |

---

### `raw_sensor_data` – Unprocessed telemetry readings

| Column      | Type      |
|-------------|-----------|
| id          | INT       |
| hub_id      | STRING    |
| sensor_name | STRING    |
| device_addr | STRING    |
| sensor_val  | FLOAT     |
| datetime    | TIMESTAMP |
| sensor_id   | STRING    |

---

### `enriched_sensor_data` – Includes raw + joined metadata

| Column      | Type      |
|-------------|-----------|
| id          | INT       |
| hub_id      | STRING    |
| sensor_name | STRING    |
| device_addr | STRING    |
| sensor_val  | FLOAT     |
| datetime    | TIMESTAMP |
| sensor_id   | STRING    |
| location    | STRING    |
| owner       | JSON      |
| workers     | JSON      |

---

## REST API Endpoints

| Method | Endpoint             | Description                            |
|--------|----------------------|----------------------------------------|
| GET    | `/api/raw/`          | Paginated raw telemetry (20/page)      |
| GET    | `/api/enriched/`     | Paginated enriched telemetry (20/page) |
| GET    | `/api/hub/`          | List all registered hubs               |
| POST   | `/api/hub/`          | Provision new hub metadata             |
| POST   | `/api/send-command/` | Send command to hub via Pub/Sub        |

---

## Backend Setup

### Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Google Cloud Deployment

```bash
gcloud builds submit --tag gcr.io/interviewing-457222/spatialhub-backend

gcloud run deploy spatialhub-backend \
  --image gcr.io/interviewing-457222/spatialhub-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "DEBUG=False,DB_HOST=...,DB_NAME=...,DB_USER=...,DB_PASS=..."
```

## CORS & CSRF Setup (Backend)
In settings.py:
```bash
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://interviewing-457222.web.app"
]

CSRF_TRUSTED_ORIGINS = [
    "https://spatialhub-backend-823061962201.us-central1.run.app"
]
```
## Frontend Setup

### Prerequisites

- Node.js 18+

---

### Development Setup

```bash
git clone https://github.com/your-org/spatialhub-frontend.git
cd spatialhub-frontend

npm install
npm install axios react-router-dom chart.js react-chartjs-2

npm run dev
```
Visit in browser: http://localhost:5173

### Frontend Project Structure
```
spatialhub-frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── api/api.ts
    ├── components/
    │   ├── HubProvisionForm.tsx
    │   └── PaginatedTable.tsx
    └── pages/
        ├── ProvisionHub.tsx
        ├── RawSensorData.tsx
        └── EnrichedSensorData.tsx
```
### Frontend Routes

| Route        | Component            | Description                              |
|--------------|----------------------|------------------------------------------|
| `/provision` | `ProvisionHub`       | Submit new hub metadata                  |
| `/raw`       | `RawSensorData`      | View paginated raw sensor readings       |
| `/enriched`  | `EnrichedSensorData` | View paginated enriched telemetry + meta |
| `/graphs`    | _(Coming Soon)_      | Charts and timeseries visualizations     |

---

## Known Issues

- CSRF errors fixed using `CSRF_TRUSTED_ORIGINS`
- DRF UI 404s (static file paths) are cosmetic
- All endpoints confirmed functional via frontend + API tools
- Sensor payloads must be in valid JSON structure

---

## Live URLs

- **Backend (Cloud Run):** [https://spatialhub-backend-823061962201.us-central1.run.app](https://spatialhub-backend-823061962201.us-central1.run.app)
- **Frontend (Firebase Hosting):** [https://interviewing-457222.web.app](https://interviewing-457222.web.app)

---

## Development Utilities

Run these SQL commands in **Cloud SQL Console** or via `psql`:

```sql
-- Clear data
DELETE FROM enriched_sensor_data;
DELETE FROM raw_sensor_data;

-- View data
SELECT * FROM raw_sensor_data;
SELECT * FROM enriched_sensor_data;



