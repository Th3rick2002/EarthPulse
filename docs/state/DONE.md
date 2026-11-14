# DONE

## Backend: contrato canónico FE/BE

- DTOs Pydantic y rutas `/api/v1/variables`, `/api/v1/regions`, `/api/v1/series` y `/api/v1/health`.
- Contrato documentado en `docs/specs/data-and-api.md`, con envoltura `{data:...}` y excepción de health.
- Catálogo MVP de variables y regiones en `backend/app/data/catalog.py`.
- Series mensuales, calidades `ok`/`missing`/`interpolated` y análisis Mann-Kendall/Sen.
- SQLite para desarrollo y estructura de repositorios existente.

## Ajustes del contrato aplicados en esta rama

- Validación de bbox, fechas mensuales completas, relación entre `value` y `quality`, rango de `pValue` y consistencia de `significant`.
- Error envelope uniforme para HTTP, validación y excepciones internas; `requestId` único también se expone como `X-Request-ID`.
- OpenAPI declara respuestas de error de catálogo, series y health.
- Criterio de análisis: requiere `minYears` y 50% de meses observados (`quality=ok`).
- Fallos de proveedor: ausencia de credenciales, integraciones no implementadas, timeout o fallo producen 502/503/504 en vez de datos sintéticos.
- Sen slope expresado por año calendario; fechas faltantes no comprimen el eje temporal.
- Amazon bbox alineado con la especificación (`lonMax=-45`).

## Verificación de este cambio

- Aún no se ejecutaron pruebas ni `git diff --check` para esta tanda.
