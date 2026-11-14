# ADR 0001: Persistencia del MVP

- Estado: propuesta adoptada para orientar el MVP; revisar al cerrar arquitectura de despliegue.
- Contexto: Cloud Run ejecuta instancias reemplazables y puede escalar a varias réplicas. Los datos/analíticas requieren caché compartida si se persisten.
- Decisión: usar Firestore para caché y metadatos compartidos del MVP desplegado; usar SQLite solo para desarrollo/prototipo local si facilita el trabajo. Aislar persistencia tras un repositorio.
- Consecuencias: no depender del filesystem local para datos durables; diseñar claves idempotentes y expiración de 24 h. Firestore no aplica claves foráneas, por lo que el backend valida referencias. Revisar coste, licencia y política de retención de cada proveedor.
- Alternativa: SQLite en producción solo con almacenamiento persistente gestionado, concurrencia y backups definidos; no es el default para Cloud Run.
