# Completado reciente

- Documentada la estructura inicial `/docs` y las reglas compartidas.
- Analizado el modelo de datos y propuesto persistencia acorde con Cloud Run.
- Añadidas instrucciones de arranque para frontend y backend.
- Creado el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4), enlazado a `Th3rick2002/EarthPulse`, con diez tareas iniciales para las tres áreas.
- Estandarizado el contrato HTTP frontend/backend v1 para mapear las entidades y campos del esquema.
- Separado el Project en catorce historias de implementación exclusivas para Backend, Frontend e Infra, con requerimientos y criterios de terminado.
- Frontend (`feat/frontend-explorer`): pantalla Explorador con panel de consulta (variable, región, intervalo mensual validado por `minYears`), globo 3D con bbox resaltado, gráfica mensual con huecos, tarjeta de veredicto con texto/icono/color, metadatos de consulta y estados de carga/error/sin datos/cobertura insuficiente.
- Frontend: cliente HTTP único (`services/api.ts`) con error común `ApiError` y tipos provisionales (`types/api.ts`) alineados con `data-and-api.md`.