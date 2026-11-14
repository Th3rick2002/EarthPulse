# DONE

## Estructura y coordinación

- Documentación de `/docs` y reglas compartidas.
- Instrucciones de instalación y arranque en README de frontend y backend.
- Creado el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4) con historias separadas por Backend, Frontend e Infra.
- Contrato HTTP FE/BE y decisiones UI/UX documentadas en `docs/specs/data-and-api.md` y `docs/specs/ui-ux.md`.

## Backend: contrato canónico

- DTOs Pydantic y rutas `/api/v1/variables`, `/api/v1/regions`, `/api/v1/series` y `/api/v1/health`.
- Catálogo MVP de variables y regiones en `backend/app/data/catalog.py`.
- Series mensuales, calidades `ok`/`missing`/`interpolated` y análisis Mann-Kendall/Sen.
- Validaciones de bbox, fechas mensuales, relación entre `value` y `quality`, rango de p-value y consistencia de significancia.
- Errores uniformes para HTTP, validación y excepciones internas; ID único en `requestId` y `X-Request-ID`.
- Cobertura mínima: `minYears` y al menos 50% de meses solicitados con `quality=ok`.
- Fallos de proveedor explícitos; no usar datos mock como sustituto silencioso.
- Sen slope expresado por año calendario; Amazon bbox con `lonMax=-45`.
- Swagger UI `/docs` y esquema OpenAPI `/openapi.json` provistos por FastAPI.

## Integración de ramas

- Al resolver el PR #1 se incorporan también `.env.example`, dependencias de Planetary Computer y la especificación UI/UX que ya estaban en `dev`.
- La resolución conserva el contrato actualizado y las tareas pendientes de integración real.

## Verificación

- No se ejecutaron pruebas en esta tanda de resolución de conflictos.
