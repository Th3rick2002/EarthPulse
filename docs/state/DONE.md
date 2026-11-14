# DONE

## Backend MVP - Contrato canónico FE/BE (Dev 1)

### ✅ [P0] Implementar modelos Pydantic y contrato OpenAPI
- **Archivos nuevos**:
  - `backend/app/schemas/contract.py` - DTOs exactos del contrato (VariableDTO, RegionDTO, BBoxDTO, TimeSeriesPointDTO, TrendAnalysisDTO, ErrorDetail, ErrorResponse, HealthResponse, wrappers)
  - `backend/app/routers/contract_catalog.py` - GET /api/v1/variables, GET /api/v1/regions
  - `backend/app/routers/contract_series.py` - GET /api/v1/series
  - `backend/app/routers/health.py` - GET /api/v1/health
- **Contrato implementado campo por campo**:
  - Variable: `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears`
  - Region: `regionId`, `name`, `bbox` (objeto con latMin/latMax/lonMin/lonMax), `description`, `type`
  - TimeSeries: `seriesId`, `variableId`, `regionId`, `date`, `value` (nullable), `quality` ("ok"|"missing"|"interpolated")
  - TrendAnalysis: `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope` (unidad/año), `pValue`, `significant`, `interpretation`, `createdAt`
  - ApiError: `error.{code,message,details,requestId}`
- **Rutas**: `/api/v1/variables`, `/api/v1/regions`, `/api/v1/series`, `/api/v1/health`
- **Envoltura**: `{data: ...}` en respuestas exitosas, `{error: ...}` en errores
- **OpenAPI**: `/openapi.json` describe exactamente estos nombres y tipos

### ✅ [P0] Catálogo MVP de variables y regiones (actualizado a contrato)
- **Archivo**: `backend/app/data/catalog.py` (fuente de verdad interna)
- Variables: ndvi (PC MODIS), air_temperature (Meteomatics ERA5), precipitation (Meteomatics CHIRPS)
- Regiones: amazon (NDVI/precip), arctic (air_temp) con bbox WGS84
- Conversión bbox interna → contrato (objeto latMin/latMax/lonMin/lonMax)

### ✅ [P0] GET /api/v1/series con validación y análisis
- **Request**: `variableId`, `regionId`, `startDate`, `endDate` (inclusivas, meses completos)
- **Response**: `{data: {variable, region, timeSeries[], trendAnalysis|null}}`
- **Validación**: 400 (fechas, combinación variable-región), 404 (catálogo inexistente)
- **Cobertura < 5 años**: `trendAnalysis: null` (no inventa análisis)
- **Análisis**: Mann-Kendall + Sen's slope (pymannkendall), p < 0.05, slope en unidad/año

### ✅ Servicios de análisis y proveedores
- `backend/app/services/analysis.py`: Mann-Kendall + Sen's slope
- `backend/app/services/providers.py`: Protocol + MeteomaticsClient, PlanetaryComputerClient, MockProvider (credenciales en `.env`)

### ✅ Capa de repositorio
- `backend/app/repositories/sqlite_repo.py`: SQLite para desarrollo
- `backend/app/repositories/firestore_repo.py`: Interfaz Firestore para Cloud Run

### ✅ Documentación actualizada
- `docs/specs/data-and-api.md`: Contrato canónico completo con ejemplos JSON válido/insuficiente/error

### Verificación
- Todos los endpoints `/api/v1/*` responden correctamente (200, 400, 404, 500)
- OpenAPI spec en `/openapi.json` genera tipos TypeScript sin mapeo de campos
- Tests manuales pasados: ndvi/amazon, air_temperature/arctic, precipitation/amazon
- Cobertura insuficiente → `trendAnalysis: null`
- Errores devuelven formato `{error: {code, message, details, requestId}}`