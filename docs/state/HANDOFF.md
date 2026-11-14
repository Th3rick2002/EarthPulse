# HANDOFF

## Estado actual

La rama backend `feat/backend-catalog-and-series` está integrándose con `dev` para resolver el PR #1. El contrato FE/BE vive en `docs/specs/data-and-api.md`; la especificación UI/UX del MVP está en `docs/specs/ui-ux.md` y las historias del equipo están en el GitHub Project.

- API canónica bajo `/api/v1`; Swagger UI `/docs`, OpenAPI `/openapi.json`.
- Catálogo MVP: NDVI (Planetary Computer), temperatura (Meteomatics ERA5) y precipitación (Meteomatics CHIRPS), con Amazonía y Ártico.
- Series mensuales con DTOs camelCase; tendencia Mann-Kendall/Sen con fechas mensuales completas, mínimo `minYears` y 50% de meses con `quality=ok`.
- Errores usan envelope común, `requestId` único y cabecera `X-Request-ID`.
- Proveedores reales siguen pendientes; el flujo no sustituye sus errores por datos mock.
- `/api/v1/health` es la excepción exitosa al wrapper `{data:...}`.

## Siguiente acción

1. Finalizar la resolución del merge: revisar archivos, confirmar ausencia de marcadores, ejecutar `git diff --check` y actualizar estos documentos con el resultado.
2. Confirmar el merge commit en `feat/backend-catalog-and-series` y subir la resolución al PR #1 en GitHub.
3. Después, continuar integraciones reales y caché según las tareas del GitHub Project.

## Hechos de entorno

- `frontend/` usa pnpm y el lockfile fija versiones.
- Docker fija Python 3.11; un venv local puede usar otra versión.
- SQLite sirve para desarrollo; persistencia Firestore para despliegue requiere completar/validar su integración.
- Credenciales Meteomatics se configuran en `backend/.env` o secretos del entorno; no se versionan.
- Nunca editar `backend/venv/` ni `frontend/node_modules/`.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/data-and-api.md`, `docs/specs/ui-ux.md`.
- Project: [TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4).
- Arranque: `frontend/README.md`, `backend/README.md`.
