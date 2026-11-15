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
- [ ] Persistir jobs y caché fuera de memoria para soportar reinicios y múltiples instancias; hoy el resultado se reutiliza 24 h solo en el proceso actual.

## Prioridad media

- [ ] Confirmar disponibilidad de CHIRPS y ERA5 histórico en el plan Meteomatics y probar consultas reales.
- [ ] Validar fechas futuras, áreas máximas y bboxes custom.
- [ ] Añadir logging estructurado, métricas y health checks de proveedor.
- [ ] Confirmar CORS para orígenes de desarrollo y despliegue.

## Infraestructura y equipo

- [ ] Dar acceso al GitHub Project privado a los otros dos devs.
- [ ] Definir hosting frontend y configurar credenciales como secretos.
