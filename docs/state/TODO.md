# Pendiente

## Siguiente paso backend

1. Trabajar la tarjeta **[P0][Dev Backend] Implementar modelos Pydantic y contrato OpenAPI** del [GitHub Project](https://github.com/users/Th3rick2002/projects/4). La tarjeta contiene el DTO FE/BE completo, las rutas, la envoltura `data`, enums, nullability y criterios de aceptación; ese contenido es la referencia visible para los tres devs.
2. Alinear la tarjeta **[P0][Dev Backend] Implementar app FastAPI y rutas del esquema** con esos modelos y publicar las rutas bajo `/api/v1`.
3. Corregir el PR #1 antes de integrarlo: sus DTOs/rutas divergen del contrato de la tarjeta P0. Revisar campo por campo contra el Project y mantener `docs/specs/data-and-api.md` sincronizado.
4. Después de fijar el OpenAPI, el dev frontend genera tipos y consume ese contrato desde su tarjeta P0 del Project.

## Pendiente de equipo e infraestructura

- Dar acceso al GitHub Project privado a los otros dos devs.
- Preguntar al usuario si el frontend se publicará en GoDaddy o GCP Storage/CDN y agregar la tarea de despliegue correspondiente.
- Configurar credenciales como secretos del entorno y completar despliegue/observabilidad.
