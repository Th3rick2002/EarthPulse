# HANDOFF

## Estado

El contrato FE/BE canónico está visible en la tarjeta P0 **Implementar modelos Pydantic y contrato OpenAPI** del [GitHub Project](https://github.com/users/Th3rick2002/projects/4); `docs/specs/data-and-api.md` debe mantenerse sincronizado con esa tarjeta. La UI/UX MVP está en `docs/specs/ui-ux.md`.

El PR #1 (`feat/backend-catalog-and-series`, backend) sigue abierto hacia `dev` y requiere alinear rutas y DTOs con el contrato antes de integrarse.

Frontend: la rama `feat/frontend-explorer` contiene la pantalla **Explorador** (panel de consulta, globo 3D, veredicto, gráfica, metadatos y estados inicial/carga/error/cobertura insuficiente/sin observaciones). Consume `/api/v1/variables`, `/api/v1/regions` y `/api/v1/series` mediante `src/services/api.ts`; no usa datos simulados. Los tipos de `src/types/api.ts` son un espejo manual provisional del contrato.

Verificación: `pnpm lint` y `pnpm build` ejecutados localmente; flujo completo con backend real pendiente porque el API aún no cumple el contrato.

## Siguiente acción

1. Abrir el PR `feat/frontend-explorer` → `dev` y pedir revisión.
2. Cuando el backend publique el OpenAPI bajo `/api/v1`: instalar `openapi-typescript`, generar `src/types/api.generated.ts`, borrar `src/types/api.ts` y probar el flujo completo.
3. Implementar **Agregar región** (`POST /api/v1/regions`) con vista previa del bbox en el globo.
4. Confirmar con backend/infra que CORS permite `http://localhost:5173`.
5. Dar acceso al Project privado a los otros dos devs. Preguntar al usuario por el hosting frontend (GoDaddy o GCP Storage).

## Hechos a tener presentes

- `frontend/` usa pnpm; el lockfile existente es la fuente exacta de versiones.
- Variable de entorno del frontend: `VITE_API_URL` (por defecto `http://localhost:8000`). `.env` no se sube a Git; `.env.example` sí.
- El frontend nunca llama a Microsoft, Meteomatics ni Firestore; solo al backend.
- Los meses `missing` dejan hueco en la gráfica (`value: null`), nunca cero.
- El panel ofrece todas las regiones para cualquier variable: el contrato v1 no expone los pares soportados (ver `TODO.md`).
- Docker fija Python 3.11. El venv local con Python 3.14.9 no define la versión del proyecto.
- Persistencia recomendada en Cloud Run: Firestore para caché/metadatos; SQLite solo local.
- Catálogo: NDVI MODIS (`modis-13Q1-061`), temperatura del aire ERA5 (`t_2m:C`), precipitación CHIRPS v3 (`precip_24h:mm`); LST MODIS es posterior.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.
- Repositorio y Project son privados; los colaboradores necesitan acceso a ambos.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/ui-ux.md`, `docs/specs/data-and-api.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.