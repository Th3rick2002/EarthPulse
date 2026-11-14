# TODO

Las historias y criterios de terminado se gestionan en el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4). Esta lista resume los siguientes pasos.

## Prioridad alta

### Frontend

- [ ] Generar tipos TypeScript desde `/openapi.json` cuando se integre `openapi-typescript`.
- [ ] Completar el formulario de región personalizada cuando backend publique `POST /api/v1/regions`.
- [ ] Pruebas manuales responsivas en escritorio, tablet y móvil.
- [ ] Consumir una futura propiedad de compatibilidad variable-región del catálogo backend, en lugar del mapa MVP temporal del frontend.

### Backend / datos

- [ ] Publicar en catálogo las combinaciones variable-región válidas.
- [ ] Implementar `POST /api/v1/regions` con validación y persistencia.
- [ ] Integrar Meteomatics y Planetary Computer con agregación/calidad reales.
- [ ] Implementar caché TTL de 24 h y completar persistencia de despliegue.

## Prioridad media

- [ ] Confirmar disponibilidad de CHIRPS en el plan Meteomatics.
- [ ] Validar fechas futuras, áreas máximas y bboxes custom.
- [ ] Añadir logging estructurado, métricas y health checks de proveedor.
- [ ] Confirmar CORS para orígenes de desarrollo y despliegue.

## Infraestructura y equipo

- [ ] Dar acceso al GitHub Project privado a los otros dos devs.
- [ ] Definir hosting frontend y configurar credenciales como secretos.
