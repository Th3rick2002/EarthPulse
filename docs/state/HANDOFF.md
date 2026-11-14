# HANDOFF

## Estado

Backend MVP implementado con **contrato canónico FE/BE** (`/api/v1/` prefix, envoltura `{data: ...}`, camelCase):

- **Catálogo** (`GET /api/v1/variables`, `GET /api/v1/regions`): 3 variables (ndvi, air_temperature, precipitation) y 2 regiones (amazon, arctic) con metadatos completos
- **Series** (`GET /api/v1/series`): Endpoint con validación, timeSeries mensual (quality: ok/missing/interpolated), trendAnalysis (Mann-Kendall + Sen's slope, slope por año) o `null` si cobertura < 5 años
- **Health** (`GET /api/v1/health`): Estado del servicio
- **Errores**: Formato estándar `{error: {code, message, details, requestId}}` (400, 404, 500)
- **Esquemas Pydantic**: `backend/app/schemas/contract.py` - DTOs exactos del contrato (VariableDTO, RegionDTO, TimeSeriesPointDTO, TrendAnalysisDTO, etc.)
- **Capa de repositorio**: SQLite para desarrollo local, interfaz Firestore para producción
- **Clientes proveedores**: Esqueletos Meteammatics/PlanetaryComputer con fallback mock (credenciales en `.env`)
- **Documentación**: `docs/specs/data-and-api.md` actualizado con contrato canónico y ejemplos JSON

## Siguiente acción

1. **Dev 2 (Frontend)**: Generar tipos TypeScript desde `/openapi.json` y consumir endpoints `/api/v1/*`
2. **Dev 3 (Integración)**: Confirmar acceso Meteomatics y validar CHIRPS habilitado en cuenta
3. **Dev 1 (Backend)**: Implementar clientes reales Meteomatics/PlanetaryComputer cuando credenciales estén listas

## Hechos a tener presentes

- `frontend/` usa pnpm; el lockfile existente es la fuente exacta de versiones.
- Docker fija Python 3.11. El venv local usa Python 3.14.7 para desarrollo.
- Persistencia: SQLite en `backend/data/trendscope.db` para desarrollo; Firestore para Cloud Run.
- Credenciales Meteomatics en `backend/.env` (no commitear).
- Microsoft Planetary Computer y Meteomatics son candidatos de integración; clientes listos para implementar.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.
- El repositorio y el Project son privados; los colaboradores necesitan acceso al repositorio y al Project.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/data-and-api.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.