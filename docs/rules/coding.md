# Convenciones de código

## Compartidas

- Mantener cambios pequeños y enfocados; usar ramas y PRs hacia `main`.
- Actualizar la especificación cuando cambie un contrato entre frontend y backend.
- No incluir credenciales, tokens ni archivos `.env` en Git. Mantener `.env.example` sin secretos.
- Registrar fechas en ISO 8601 y unidades explícitas; validar entradas en los límites de cada capa.

## Frontend

- Usar React con TypeScript y componentes funcionales.
- Mantener llamadas HTTP y tipos de API en módulos reutilizables; representar carga, error y falta de datos.
- Instalar dependencias con pnpm y respetar `pnpm-lock.yaml`.

## Backend

- Usar Python 3.11 según `backend/Dockerfile`, FastAPI y modelos Pydantic.
- Separar routers, integración con proveedores, transformación/análisis y persistencia.
- Mantener clientes externos detrás de servicios; manejar timeout, errores de proveedor y datos faltantes.
- Declarar y mantener dependencias en `backend/requirements.txt`.

## Infraestructura

- El servicio en Render debe escuchar en `0.0.0.0` y respetar el puerto proporcionado por `PORT`.
- El filesystem de Render es efímero por defecto. SQLite en producción requiere un disco persistente montado y limita el servicio a una instancia; no asumir que el archivo se comparte entre instancias.
