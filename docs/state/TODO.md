# TODO

Las historias y criterios de terminado se gestionan en el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4). Esta lista resume los siguientes pasos.

## Prioridad alta

### Frontend

- [ ] Generar tipos TypeScript desde `/openapi.json` cuando se integre `openapi-typescript`.
- [ ] Pruebas manuales responsivas en escritorio, tablet y móvil.

### Backend / datos

- [ ] Publicar en catálogo las combinaciones variable-región válidas.
- [ ] Implementar persistencia de regiones guardadas (`POST /api/v1/regions`) si se necesita conservar las zonas dibujadas entre sesiones; hoy son temporales a una comparación.
- [ ] Persistir jobs y compartirlos entre instancias; ahora los jobs asíncronos viven en memoria.
- [ ] Montar volumen `backend/data` en Docker/despliegue para conservar caché SQLite al recrear contenedores.

## Prioridad media

- [ ] Confirmar disponibilidad de CHIRPS y ERA5 histórico en el plan Meteomatics y probar consultas reales.
- [ ] Validar cobertura temporal histórica y límites de resolución en las cuatro zonas soportadas.
- [ ] Añadir logging estructurado, métricas y health checks de proveedor.
- [ ] Confirmar CORS para orígenes de desarrollo y despliegue.

## Infraestructura y equipo

- [ ] Dar acceso al GitHub Project privado a los otros dos devs.
- [ ] Definir hosting frontend y configurar credenciales como secretos.
