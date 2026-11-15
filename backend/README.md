# TrendScope backend

API FastAPI para catálogo, series mensuales y análisis de tendencias. Docker fija Python 3.11; usa esa versión para desarrollo local.

## Requisitos

- Python 3.11 y `venv`.
- pip.

Comprueba la versión:

```bash
python3.11 --version
```

## Instalar dependencias

Desde `backend/`:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Windows PowerShell activa el entorno con `.venv\Scripts\Activate.ps1`.

## Configuración y ejecución

Desde `backend/`, crea el archivo de configuración y edita las credenciales:

```bash
cp .env.example .env
```

La integración consulta la temperatura ERA5 y la precipitación CHIRPS como estadísticas diarias del polígono de la región y las agrega por mes. La cuenta debe tener habilitados los productos históricos `ecmwf-era5` y `chc-chirps3`; el producto también se puede cambiar con `METEOMATICS_TEMPERATURE_SOURCE` y `METEOMATICS_PRECIPITATION_SOURCE`.

NDVI consulta la colección STAC `modis-13Q1-061`, firma los COG públicos, selecciona por tile el compuesto de 16 días más próximo a mitad de cada mes, filtra píxeles con confiabilidad MODIS igual a 0 y aplica escala `0.0001`. No requiere credenciales. Como puede tomar más tiempo que una petición HTTP, se ejecuta en segundo plano; la ruta responde `202` y el cliente consulta el job hasta que termina. Los resultados completados se guardan en memoria por 24 horas. No subas `backend/.env` ni incluyas credenciales en logs.

```bash
uvicorn app.main:app --reload --env-file .env
```

Ejecuta desde `backend/`; la API queda en `http://127.0.0.1:8000`. Swagger está en `/docs` y OpenAPI en `/openapi.json`.

Desde la raíz también puedes levantar backend y frontend juntos con `./scripts/dev.sh`; el script carga `backend/.env` automáticamente.

## Rutas principales

- `GET /api/v1/variables`
- `GET /api/v1/regions`
- `GET /api/v1/series?variableId=...&regionId=...&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD`
- `GET /api/v1/health`

Las fechas de series deben cubrir meses completos. Consulta [`../docs/specs/data-and-api.md`](../docs/specs/data-and-api.md) para el contrato, las fuentes y la cobertura del análisis.
