# Contexto del proyecto

Este proyecto usa documentación estructurada en `/docs`. Antes de actuar:

1. Lee `/docs/state/HANDOFF.md` para conocer el estado actual y la siguiente acción.
2. Lee `/docs/rules/coding.md` y `/docs/rules/domain.md` para aplicar las convenciones.
3. Consulta `/docs/specs/INDEX.md` y la especificación relacionada si la tarea toca una funcionalidad.
4. Si trabajas en una carpeta con instrucciones más específicas, léelas también.

No leas `/docs/changes/` ni `/docs/decisions/` salvo que se te pida.

Al terminar cada turno, actualiza `/docs/state/HANDOFF.md`. Registra trabajo completado en `DONE.md`, pendientes priorizados en `TODO.md` y decisiones de alcance en `WONTDO.md`. Mantén los documentos breves y enlazados entre sí.

## Coordinación del equipo

- Frontend: `frontend/` y documentación de interfaz/contrato en `/docs/specs/`.
- Backend y datos: `backend/` y documentación de API, fuentes y análisis en `/docs/specs/`.
- Infraestructura e integración: despliegues, configuración compartida y seguimiento en el GitHub Project del repositorio.
- Antes de cambiar un contrato compartido, actualiza la especificación y comunica el cambio en el Project/PR.
- No edites archivos generados ni entornos virtuales/dependencias instaladas.
