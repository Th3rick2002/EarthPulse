# HANDOFF

## Estado

Documentación inicial de TrendScope preparada. El frontend contiene una plantilla Vite/React; `backend/` contiene un Dockerfile basado en Python 3.11 y dependencias iniciales en `requirements.txt`, pero todavía no tiene código de aplicación.

## Siguiente acción

Dar acceso al Project privado a los otros dos devs y acordar con el equipo la primera variable/producto para el caso vertical. El Project ya está enlazado a `Th3rick2002/EarthPulse` y contiene diez tareas iniciales en estado Todo.

## Hechos a tener presentes

- `frontend/` usa pnpm; el lockfile existente es la fuente exacta de versiones.
- Docker fija Python 3.11. El venv local encontrado fue creado con Python 3.14.9 y no define la versión del proyecto.
- Persistencia recomendada para despliegue Cloud Run: Firestore para caché/metadatos; SQLite solo local/prototipo salvo que se añada almacenamiento persistente.
- Microsoft Planetary Computer y Meteomatics son candidatos de integración; comprobar colección, unidades, historial, acceso y términos por variable.
- Trabajar en archivos fuente, nunca en `backend/venv/` ni `frontend/node_modules/`.
- El repositorio y el Project son privados; los colaboradores necesitan acceso al repositorio y al Project para ver/actualizar el tablero.

## Documentos clave

- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Especificaciones: `docs/specs/INDEX.md`, `docs/specs/data-and-api.md`.
- Arranque: `frontend/README.md`, `backend/README.md`.
