# DONE

## Backend MVP - Catálogo y Series (Dev 1)

### ✅ [P0] Registrar catálogo MVP de variables y regiones
- **Archivo**: `backend/app/data/catalog.py`
- Variables implementadas:
  - `ndvi`: Planetary Computer modis-13Q1-061, asset 250m_16_days_NDVI, escala 0.0001, agregado mensual (mean)
  - `air_temperature`: Meteomatics source=ecmwf-era5, t_2m:C, media mensual
  - `precipitation`: Meteomatics source=chc-chirps3, precip_24h:mm, suma mensual
  - `land_surface_temperature`: Dejado para después (documentado)
- Regiones implementadas:
  - `amazon`: bbox WGS84 (-20.0, 5.0, -80.0, -50.0), para NDVI/precipitación
  - `arctic`: bbox WGS84 (66.5, 90.0, -180.0, 180.0), para temperatura del aire
- Endpoints: `GET /variables`, `GET /regions` entregan catálogo completo
- Validación de bbox y conversión de orden por proveedor (STAC vs Meteomatics)

### ✅ [P0] Cerrar contrato GET /series
- **Archivos**: `backend/app/schemas/series.py`, `backend/app/routers/series.py`
- Request: `GET /series?variableId=...&regionId=...&startDate=...&endDate=...`
- Response incluye: variable, region/bbox, source, unit, frequency, coverage, observations[], analysis{}
- Validación: 400 para fechas/bbox/parámetros inválidos, 404 para catálogo inexistente
- Cobertura < 5 años: devuelve `insufficientReason` y `analysis: null`, no inventa análisis
- Análisis: Mann-Kendall con p < 0.05, pendiente de Sen, interpretación en lenguaje natural

### ✅ Esquemas Pydantic y validación
- `backend/app/schemas/catalog.py`: VariableResponse, RegionResponse
- `backend/app/schemas/series.py`: SeriesRequest, SeriesResponse, Observation, Coverage, SourceInfo, Analysis

### ✅ Servicios de análisis y proveedores
- `backend/app/services/analysis.py`: Mann-Kendall + Sen's slope usando `pymannkendall`
- `backend/app/services/providers.py`: Protocol + esqueletos MeteomaticsClient, PlanetaryComputerClient, MockProvider

### ✅ Capa de repositorio (persistencia)
- `backend/app/repositories/sqlite_repo.py`: SQLite para desarrollo local
- `backend/app/repositories/firestore_repo.py`: Interfaz Firestore para Cloud Run
- `backend/app/repositories/base.py`: Interfaces abstractas

### ✅ Documentación actualizada
- `docs/specs/data-and-api.md`: Contratos finales con ejemplos JSON válido/insuficiente

### Verificación
- Todos los endpoints responden correctamente (200, 400, 404)
- OpenAPI spec generado en `/docs`
- Tests manuales pasados para ndvi/amazon, air_temperature/arctic, precipitation/amazon