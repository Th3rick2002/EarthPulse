# TrendScope frontend

Frontend React + TypeScript + Vite. El lockfile `pnpm-lock.yaml` define las versiones instaladas; no cambies el gestor a npm ni borres el lockfile.

## Requisitos

- Node.js 24 (versión disponible en el entorno de trabajo; Vite 8 requiere una versión moderna de Node).
- pnpm 12, activado mediante Corepack o instalado en el entorno.

Comprueba las versiones:

```bash
node --version
pnpm --version
```

## Instalar y ejecutar

Desde `frontend/`:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Vite muestra la URL local en la terminal. Para generar la versión de producción:

```bash
pnpm build
pnpm preview
```

`pnpm lint` ejecuta ESLint.

## Estado actual

Esta carpeta todavía contiene la plantilla inicial de Vite. Los componentes del globo, selector, gráfico y conexión al API se implementarán según [`../docs/specs/trendScope-mvp.md`](../docs/specs/trendScope-mvp.md) y [`../docs/specs/data-and-api.md`](../docs/specs/data-and-api.md).

Cuando el backend esté disponible, configura la URL del API mediante una variable `VITE_...`; nunca pongas credenciales de proveedor en el frontend.
