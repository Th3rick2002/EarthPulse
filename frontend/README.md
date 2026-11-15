# TrendScope frontend

Explorador web con React, TypeScript y Vite. `pnpm-lock.yaml` fija las versiones de dependencias; usa pnpm y no regeneres el lockfile con npm.

## Requisitos

- Node.js 24.
- pnpm 12.
- Backend TrendScope en `http://localhost:8000` para consultar datos.

## Instalar y ejecutar

Desde `frontend/`:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Vite inicia normalmente en `http://localhost:5173`. La URL del backend se configura con `VITE_API_URL`; si no se define, el cliente usa `http://localhost:8000`.

```bash
VITE_API_URL=http://localhost:8000 pnpm dev
```

No configures credenciales de Planetary Computer o Meteomatics en el frontend. La app solo consume `/api/v1/*` del backend.

## Verificación y build

```bash
pnpm lint
pnpm build
pnpm preview
```

## Funcionalidad

La pantalla Explorador consulta variables, regiones y series; presenta un globo 3D, gráfica mensual, veredicto estadístico y estados de carga/error/sin datos. Actualmente los tipos son manuales y la selección de región sigue los pares disponibles del catálogo MVP. Consulta el contrato en [`../docs/specs/data-and-api.md`](../docs/specs/data-and-api.md) y UI/UX en [`../docs/specs/ui-ux.md`](../docs/specs/ui-ux.md).
