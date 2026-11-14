# HANDOFF

## Estado

El contrato FE/BE canónico está visible en la tarjeta P0 **Implementar modelos Pydantic y contrato OpenAPI** del [GitHub Project](https://github.com/users/Th3rick2002/projects/4); `docs/specs/data-and-api.md` debe mantenerse sincronizado con esa tarjeta. La UI/UX MVP está definida en `docs/specs/ui-ux.md` y reflejada en las cuatro historias Frontend del Project. El Project tiene catorce tarjetas por área. El PR #1 (`feat/backend-catalog-and-series`) está abierto hacia `dev` y requiere alinear rutas y DTOs antes de integrarlo. El frontend contiene una plantilla Vite/React; la rama local y el PR remoto pueden tener estados distintos.

## Siguiente acción

Continuar el PR #1 según la tarjeta P0 de contrato en GitHub Project: alinear DTOs/OpenAPI, prefijo `/api/v1`, respuestas y errores. Usar la tarjeta del Project como fuente operativa compartida; mantener `docs/specs/data-and-api.md` sincronizado. Dar acceso al Project privado a los otros dos devs. Preguntar al usuario por el hosting frontend (GoDaddy o GCP Storage) antes de agregar una tarea de despliegue estático. El contrato usa los campos de `variables`, `regions`, `time_series`, `trend_analysis` y `cache`; cache es interna.

## Hechos a tener presentes

- `frontend/` usa pnpm; el lockfile existente es la fuente exacta de versiones.
- Docker fija Python 3.11. El venv local encontrado fue creado con Python 3.14.9 y no define la versión del proyecto.
- Persistencia recomendada para despliegue Cloud Run: Firestore para caché/metadatos; SQLite solo local/prototipo salvo que se añada almacenamiento persistente.
- Planetary Computer STAC y Meteomatics REST son las APIs previstas; comprobar colección, unidades, historial, acceso y términos por variable.
- Catálogo definido como NDVI MODIS (`modis-13Q1-061`), temperatura del aire ERA5 (`t_2m:C`) y precipitación CHIRPS v3 (`precip_24h:mm`); LST MODIS (`modis-11A2-061`) es posterior y no equivale a temperatura del aire.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.
- El repositorio y el Project son privados; los colaboradores necesitan acceso al repositorio y al Project para ver/actualizar el tablero.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/ui-ux.md`, `docs/specs/data-and-api.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.
