# HANDOFF

## Estado actual

El backend PR #1 está integrado en `dev`. La rama local `feat/frontend-explorer` ya fue rebasada sobre ese `dev`; resolución y cambios de compatibilidad están en la copia de trabajo.

- API canónica `/api/v1`: `GET /variables`, `GET /regions`, `GET /series`; Swagger `/docs`.
- Catálogo MVP: NDVI/Amazonía, temperatura del aire/Ártico y precipitación/Amazonía.
- El frontend consume camelCase con `src/services/api.ts`; los tipos siguen siendo manuales.
- QueryPanel restringe las regiones a pares soportados por el catálogo MVP. El backend aún no publica esta compatibilidad en el DTO.
- El backend aún no tiene `POST /api/v1/regions`; regiones custom no se pueden crear desde el frontend.
- Meteomatics ahora consulta ERA5 (media diaria de temperatura) y CHIRPS (precipitación diaria) por polígono y los agrega a meses; verificar disponibilidad histórica en la cuenta con una petición real.
- Planetary Computer/NDVI busca páginas STAC de hasta 1000 elementos y selecciona el compuesto Terra más cercano a mitad de mes por tile. El Data API sirve NDVI+QA recortados juntos en GeoTIFF de 256×256; se filtra QA, se escala `0.0001` y se pondera el promedio por área aproximada.
- NDVI de rangos largos corre como job asíncrono (`202` + polling); la UI espera el job sin mantener una petición larga abierta. Resultados terminados se reutilizan 24 horas en memoria del proceso.
- Dependencias geoespaciales disponibles en `backend/venv` (Python 3.14.9 en esta máquina); la imagen Docker fija Python 3.11.
- El error `The planetary-computer integration is not implemented yet` solo puede venir de un backend levantado con código anterior: ese texto ahora existe únicamente en el mapeo de compatibilidad para clientes antiguos que lancen `NotImplementedError`. Reiniciar el backend local o reconstruir la imagen Docker carga el código actualizado.
- Consulta real NDVI/Amazonía del 2021-01 al 2025-12 completada con el código final por el flujo de job en 116.1 s: 60 meses, 56 observaciones válidas y tendencia generada. Una consulta real de un mes respondió en 11.9 s y la repetición usó caché.
- Los jobs viven en memoria y sobreviven consultas repetidas durante 24 h solo dentro del mismo proceso; para despliegues multiinstancia o reinicios hace falta un gestor de jobs/caché compartido.
- `pnpm lint` y `pnpm build` pasan. El build informa que el chunk JS supera 500 kB.
- Scripts de desarrollo: `scripts/dev.sh` (API y Vite locales) y `scripts/dev-docker-backend.sh` (API Docker y Vite local); guía en `scripts/README.md`.
- `scripts/dev.sh` fue ejecutado: `/api/v1/health`, `/api/v1/variables` y Vite respondieron. Docker no está instalado en este entorno, así que no se ejecutó la variante Docker.

## Siguiente acción

1. Revisar cambios y compartir la rama rebasada para continuar el PR frontend. Al haber reescrito historial, actualizar el remoto con `--force-with-lease` cuando se publique.
2. Generar tipos desde `/openapi.json` y quitar los tipos manuales.
3. Acordar con backend cómo exponer pares variable-región y crear regiones custom antes de completar esos flujos UI.
4. Reiniciar backend y frontend para cargar el Data API y el polling NDVI; verificar en la instalación local la consulta Meteomatics y permisos ERA5/CHIRPS.
5. Usar los scripts de `scripts/` para levantar localmente o con backend Docker.

## Entorno y documentos

- `frontend/` usa pnpm; respetar `pnpm-lock.yaml`.
- Backend fija Python 3.11 en Docker.
- No versionar credenciales ni `.env`; no editar `frontend/node_modules/` o `backend/venv/`.
- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Contrato: `docs/specs/data-and-api.md`; UX: `docs/specs/ui-ux.md`.
- Project: [TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4).
- Inicio: `frontend/README.md`, `backend/README.md`.
