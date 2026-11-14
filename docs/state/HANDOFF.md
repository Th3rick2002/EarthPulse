# HANDOFF

## Estado

Backend MVP implementado y funcional:
- **Catálogo** (`GET /variables`, `GET /regions`): 3 variables (ndvi, air_temperature, precipitation) y 2 regiones (amazon, arctic) con metadatos completos
- **Series** (`GET /series`): Endpoint completo con validación, datos mock mensuales, cobertura, y análisis Mann-Kendall
- **Esquemas Pydantic**: Contratos definidos para request/response con validación de tipos
- **Capa de repositorio**: SQLite para desarrollo local, interfaz Firestore para producción
- **Clientes proveedores**: Esqueletos para Meteomatics y Planetary Computer (con fallback mock)
- **Documentación**: `docs/specs/data-and-api.md` actualizado con esquemas finales y ejemplos

## Siguiente acción

1. **Dev 2 (Frontend)**: Integrar tipos TypeScript desde OpenAPI spec y consumir endpoints
2. **Dev 3 (Integración)**: Confirmar acceso Meteomatics y validar CHIRPS habilitado en cuenta
3. **Dev 1 (Backend)**: Implementar clientes reales Meteomatics/Planetary Computer cuando credenciales estén disponibles

## Hechos a tener presentes

- `frontend/` usa pnpm; el lockfile existente es la fuente exacta de versiones.
- Docker fija Python 3.11. El venv local usa Python 3.14.7 para desarrollo.
- Persistencia: SQLite en `backend/data/trendscope.db` para desarrollo; Firestore para Cloud Run.
- Microsoft Planetary Computer y Meteomatics son candidatos de integración; clientes listos para implementar.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.
- El repositorio y el Project son privados; los colaboradores necesitan acceso al repositorio y al Project.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/data-and-api.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.