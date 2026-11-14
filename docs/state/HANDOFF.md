# HANDOFF

## Estado actual

Rama de backend `feat/backend-catalog-and-series`. El contrato FE/BE está definido en `docs/specs/data-and-api.md` y los endpoints canónicos están bajo `/api/v1`.

- Catálogo: variables y regiones MVP desde `backend/app/data/catalog.py`.
- Series: respuesta mensual con DTOs camelCase, `quality` normalizada y análisis Mann-Kendall/Sen cuando cumple la cobertura.
- Fechas: rangos inclusivos de meses completos; análisis requiere `minYears` y al menos 50% de los meses solicitados con calidad `ok`.
- Pendiente en este cambio: revisar el diff. No se han ejecutado pruebas.
- Proveedores: los clientes Meteomatics y Planetary Computer siguen siendo esqueletos. No se devuelve mock como si fueran datos reales: errores se traducen a 502/503/504.
- Errores API: `{error:{code,message,details,requestId}}`, `requestId` único por request y cabecera `X-Request-ID`. Validación FastAPI usa 422. `/api/v1/health` es la excepción exitosa sin `{data:...}`.
- El Sen slope usa tiempo calendario y se expresa en unidad por año.

## Siguiente acción

1. Revisar `git diff` y `git diff --check`; corregir inconsistencias visibles.
2. Compartir los cambios locales para revisión del equipo; no asumir commit ni push.
3. Integrar clientes reales de Meteomatics y Microsoft Planetary Computer según `docs/specs/data-and-api.md`.

## Hechos de entorno

- `frontend/` usa pnpm y el lockfile del repo fija versiones.
- Docker fija Python 3.11; el venv local puede tener otra versión.
- SQLite es el almacenamiento de desarrollo; la integración Firestore sigue pendiente de validar.
- Credenciales Meteomatics se configuran en `backend/.env`; nunca se versionan.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.

## Documentos clave

- Contrato: `docs/specs/data-and-api.md`.
- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.
