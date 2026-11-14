# Pendiente

## Siguiente paso frontend

1. Abrir PR `feat/frontend-explorer` → `dev`.
2. Tras fijarse el OpenAPI: generar `src/types/api.generated.ts` con `openapi-typescript`, eliminar `src/types/api.ts` y probar contra el backend real.
3. Tarjeta **Agregar región**: formulario (nombre, descripción, lat/lon mín/máx), vista previa del bbox en el globo, `POST /api/v1/regions`, errores junto al campo.
4. Pulir tooltips de definición de variables y botón/caso de demostración (ver `trendscope-plan.md`).
5. Plantear al equipo cómo publicar los pares variable-región soportados en la API; la spec UI pide ofrecer solo combinaciones válidas y el contrato v1 no lo cubre.
6. Pruebas manuales en escritorio, tablet y móvil (orden globo → veredicto → gráfica; teclado y táctil).

## Siguiente paso backend

1. Trabajar la tarjeta **[P0][Dev Backend] Implementar modelos Pydantic y contrato OpenAPI** del [GitHub Project](https://github.com/users/Th3rick2002/projects/4).
2. Alinear la tarjeta **[P0][Dev Backend] Implementar app FastAPI y rutas del esquema** con esos modelos y publicar las rutas bajo `/api/v1`.
3. Corregir el PR #1 antes de integrarlo: sus DTOs/rutas divergen del contrato. Mantener `docs/specs/data-and-api.md` sincronizado.
4. Habilitar CORS para `http://localhost:5173` (desarrollo) y el dominio del frontend desplegado.

## Pendiente de equipo e infraestructura

- Dar acceso al GitHub Project privado a los otros dos devs.
- Preguntar al usuario si el frontend se publicará en GoDaddy o GCP Storage/CDN y agregar la tarea de despliegue correspondiente.
- Configurar credenciales como secretos del entorno y completar despliegue/observabilidad.