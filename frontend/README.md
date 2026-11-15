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

La pantalla Explorador permite elegir una variable, un periodo de 1 a 50 años y dibujar hasta cuatro rectángulos independientes en el mapa Leaflet. Cada rectángulo se consulta por separado; los resultados incluyen gráfica mensual, veredicto estadístico y una ficha lateral con fuente, periodo y coordenadas. Leaflet carga teselas de OpenStreetMap, por lo que el mapa necesita conexión a internet y conserva la atribución visible a sus colaboradores.

El proyecto usa Leaflet 1.9.4 y React Leaflet 5.0.0. Consulta el contrato de `POST /api/v1/series/compare` en [`../docs/specs/data-and-api.md`](../docs/specs/data-and-api.md) y las decisiones de interfaz en [`../docs/specs/ui-ux.md`](../docs/specs/ui-ux.md).
