# TrendScope

TrendScope explora tendencias de variables de ciencias de la Tierra por región.

- **Frontend:** React, TypeScript, Vite, Three.js y Recharts (`/frontend`).
- **Backend:** Python 3.11 y FastAPI; consulta fuentes y calcula tendencias (`/backend`).
- **Fuentes previstas:** Microsoft Planetary Computer y Meteomatics; Giovanni queda sujeto a validar producto/API.
- **MVP:** series mensuales con al menos cinco años, slope y Mann-Kendall, gráfico, globo y veredicto.
- **Equipo:** frontend, backend/datos e infraestructura/integración. Seguimiento en [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4) (privado).
- **Inicio:** instrucciones locales en `frontend/README.md` y `backend/README.md`.
- **Reglas:** [`rules/`](rules/); **especificaciones:** [`specs/`](specs/).
- **Estado para reanudar:** [`state/HANDOFF.md`](state/HANDOFF.md).
- **Cambios narrativos:** [`changes/`](changes/); **decisiones:** [`decisions/`](decisions/).

El plan original está en [`../trendscope-plan.md`](../trendscope-plan.md). La carpeta backend solo tiene Dockerfile por ahora; no asumir que el API ya está implementado.
