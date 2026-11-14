# TrendScope – NASA Space Apps Challenge 2026

## Challenge: Be An Earth System Trend Detective!

Crear una herramienta que seleccione variables de ciencia de la Tierra, visualice cómo cambian en el tiempo para una región, y determine la tasa de cambio y su significancia estadística (Mann-Kendall, t-test, intervalos de confianza).

---

## Stack Tecnológico

| Capa | Tecnología | Recurso |
|---|---|---|
| Frontend | React + TypeScript + Vite, Three.js (globo 3D), Recharts | GoDaddy (hosting gratis 1 año) |
| Backend | Python 3.11 + FastAPI | GCP Cloud Run |
| Datos | Microsoft Planetary Computer (STAC API), Meteomatics Weather API | Global Offers gratuitos |
| Análisis | pymannkendall, scipy, pandas, numpy | — |
| Deploy | GCP Cloud Run (backend), GoDaddy/GCP Storage (frontend) | GCP $300/90 días |

---

## Requerimientos Mínimos (MVP)

### Cumplimiento del reto
- ✅ Seleccionar variables de ciencia de la Tierra (temperatura, precipitación, NDVI, clorofila, etc.)
- ✅ Adquirir datos para una región específica (bbox)
- ✅ Generar y visualizar serie temporal (mínimo 5 años de datos)
- ✅ Análisis estadístico: tasa de cambio (slope) + test de Mann-Kendall (p < 0.05)
- ✅ Definiciones simples de variables (tooltips)
- ✅ Ejemplo demo precargado (ej. temperatura del Ártico)

### Fuera de alcance
- Tendencias no lineales
- Remoción de ciclos estacionales
- Análisis complejos más allá de tendencias lineales

---

## Esquema de Base de Datos (Firestore – opcional, caché)

**Colección `variables`** (catálogo):
```
variableId, name, description, unit, source, category
```

**Colección `regions`** (regiones predefinidas):
```
regionId, name, bbox (lat/lon), description
```

**Colección `series_cache`** (caché de series temporales, TTL 24h):
```
cacheId, variableId, regionId, startDate, endDate, data[], fetchedAt, trendResult (slope, pValue, significant)
```

---

## Pipeline de Transformación de Datos

```
1. Fuente (Planetary Computer STAC / Meteomatics / Giovanni)
   ↓
2. Backend FastAPI: descarga datos crudos (JSON/NetCDF)
   ↓
3. Transformación: filtrar por región (bbox), resamplear a mensual, limpiar NaN
   ↓
4. Análisis: Mann-Kendall (pymannkendall) → slope, p-value, significant
   ↓
5. Caché (Firestore o memoria) con TTL 24h
   ↓
6. API REST → Frontend (JSON: {dates[], values[], slope, pValue, significant, interpretation})
   ↓
7. Frontend: Three.js (globo 3D con punto de región) + Recharts (serie temporal) + tarjeta de veredicto
```

---

## Reglas del Proyecto

### Reglas de dominio
- Los datos siempre vienen de fuentes NASA o agencias asociadas.
- Toda serie temporal debe tener mínimo 5 años de datos para análisis válido.
- Test de significancia: Mann-Kendall (p < 0.05 = significativo).
- Máximo 5 regiones predefinidas y 4-5 variables (MVP manejable).

### UI/UX
- Visual primero: globo 3D en Three.js como elemento principal, gráfico temporal debajo.
- Veredicto claro: tarjeta con color (verde = significativo, amarillo = no significativo, gris = sin datos suficientes) + texto en lenguaje simple.
- Definiciones simples: cada variable tiene tooltip de 1-2 líneas.
- Ejemplo demo: botón "Ver ejemplo" con caso precargado.
- Responsive en desktop y tablet.

### Reglas de código
- Backend: Python 3.11 + FastAPI, tipado con Pydantic.
- Frontend: React + TypeScript, componentes funcionales.
- Deploy: GCP Cloud Run (backend), GoDaddy/GCP Storage (frontend).
- Commits frecuentes, rama main protegida, PRs para merge.
- Sin autenticación compleja en MVP.

---

## Estructura del Monorepo

```
trendscope/
├── frontend/
│   ├── src/
│   │   ├── components/       # Globe3D, TimeSeriesChart, VerdictCard, VariableSelector
│   │   ├── pages/            # Home, Explorer
│   │   ├── services/         # api.ts
│   │   ├── types/            # interfaces TS
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/          # series.py, variables.py
│   │   ├── services/         # planetary.py, meteomatics.py, analysis.py
│   │   └── models/           # pydantic schemas
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── .gitignore
```

---

## Pasos para Comenzar

### 1. Crear repo y estructura
```bash
mkdir trendscope && cd trendscope
mkdir -p frontend/src/{components,pages,services,types} backend/app/{routers,services,models}
```

### 2. Backend (Python FastAPI)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn httpx pymannkendall pandas numpy python-dotenv
```

**Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3. Frontend (React + Vite + Three.js)
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install three @react-three/fiber @react-three/drei recharts axios
```

### 4. Deploy backend en GCP Cloud Run
```bash
gcloud run deploy trendscope-api --source ./backend --region us-central1 --allow-unauthenticated
```

### 5. Deploy frontend
- GoDaddy hosting (gratis 1 año) o GCP Cloud Storage + CDN.
```bash
cd frontend && npm run build
```

### 6. Variables de entorno
```env
# backend/.env
PLANETARY_COMPUTER_TOKEN=xxx
METEOMATICS_USER=xxx
METEOMATICS_PASS=xxx
```

---

## Primeros archivos a crear

1. `backend/app/main.py` – FastAPI app con CORS y router de series.
2. `backend/app/routers/series.py` – Endpoint `GET /series?variable=temperature&region=arctic`.
3. `backend/app/services/analysis.py` – Mann-Kendall + slope + p-value.
4. `frontend/src/components/Globe3D.tsx` – Globo Three.js con punto de región.
5. `frontend/src/components/TimeSeriesChart.tsx` – Gráfico Recharts.

---

## Plan de 2 Días

### Día 1 – Construcción base
| Persona | Tarea |
|---|---|
| Dev 1 (Backend) | FastAPI + endpoint `/series` + integración Planetary Computer/Meteomatics + Mann-Kendall |
| Dev 2 (Frontend) | React + Three.js globo 3D + selector de variable/región + gráfico temporal |
| Dev 3 (Infra) | Deploy backend en Cloud Run + deploy frontend + dominio GoDaddy |

**Checkpoint fin Día 1:** Backend retorna serie temporal + análisis; Frontend muestra globo y gráfico con datos mock.

### Día 2 – Integración y pulido
| Persona | Tarea |
|---|---|
| Dev 1 | Caché + manejo de errores + optimización de queries |
| Dev 2 | Tarjeta de veredicto + tooltips + ejemplo demo + pulido visual |
| Dev 3 | Deploy final + dominio + README + video demo |

**Checkpoint fin Día 2:** App funcional en producción con dominio, datos reales, análisis de tendencia y visualización 3D.

### Regla de oro
> No agregar features nuevas después del mediodía del Día 2. Solo pulir, corregir bugs y preparar la demo.
