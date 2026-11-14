# HANDOFF

## Estado actual

Backend PR #1 está integrado en `dev`. El contrato FE/BE y catálogo están en `docs/specs/data-and-api.md`; UI/UX en `docs/specs/ui-ux.md`; las tareas compartidas se siguen en el [GitHub Project](https://github.com/users/Th3rick2002/projects/4).

La rama `feat/frontend-explorer` está en rebase sobre `dev`. Se están resolviendo conflictos de documentación y alineando el frontend con el backend integrado.

- API canónica `/api/v1`: `GET /variables`, `GET /regions`, `GET /series`; Swagger `/docs`.
- Catálogo MVP: NDVI/amazon, temperatura del aire/Ártico, precipitación/amazon.
- Los DTOs son camelCase; series mensuales; errores incluyen `requestId`.
- El frontend consume el contrato con `src/services/api.ts`; los tipos aún son manuales.
- El backend no publica las combinaciones válidas variable-región ni tiene `POST /regions`; el frontend debe filtrar pares del catálogo MVP y no ofrecer creación custom todavía.
- Los proveedores siguen siendo esqueletos y pueden devolver 503 hasta integrar credenciales/adaptadores reales.

## Siguiente acción

1. Terminar el rebase de frontend y comprobar que no quedan conflictos.
2. Revisar la UI contra el contrato integrado; ejecutar lint/build porque esta tarea pide verificar el frontend.
3. Actualizar esta nota con el resultado y pendientes concretos.

## Entorno y documentos

- `frontend/` usa pnpm; respetar `pnpm-lock.yaml`.
- Backend fija Python 3.11 en Docker.
- No versionar credenciales ni `.env`; no editar `frontend/node_modules/` o `backend/venv/`.
- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Contrato: `docs/specs/data-and-api.md`; UX: `docs/specs/ui-ux.md`.
- Inicio: `frontend/README.md`, `backend/README.md`.
