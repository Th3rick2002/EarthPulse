# Scripts de desarrollo

Ejecuta desde la raíz del repositorio. Los scripts requieren Bash y no instalan dependencias: sigue las instrucciones de `frontend/README.md` y `backend/README.md` si falta algo.

## Frontend y backend locales

```bash
./scripts/dev.sh
```

Usa el entorno Python de `backend/.venv` o `backend/venv`, levanta FastAPI en `http://localhost:8000` y Vite en `http://localhost:5173`. Detén ambos procesos con Ctrl+C.

## Backend en Docker y frontend local

```bash
./scripts/dev-docker-backend.sh
```

Construye la imagen con `backend/Dockerfile`, publica el puerto interno 8080 como `localhost:8000` y levanta Vite en `localhost:5173`. Si existe `backend/.env`, lo pasa al contenedor. Detén frontend y contenedor con Ctrl+C.

Ambas opciones permiten consultar el catálogo y `/docs`. Las series usan Meteomatics para temperatura y precipitación, y Microsoft Planetary Computer (MODIS Terra) para NDVI. Meteomatics requiere credenciales y acceso histórico a ERA5/CHIRPS en la cuenta; Planetary Computer usa datos públicos y no requiere credenciales.

La primera consulta NDVI de varios años puede tardar alrededor de dos minutos. El endpoint responde `202` de inmediato y el frontend consulta el progreso hasta recibir la serie; la respuesta completada se reutiliza durante 24 horas mientras siga vivo el mismo proceso backend.

Si el backend estaba levantado antes de actualizar el código, reinícialo para cargar la integración NDVI. Para Docker, vuelve a construir y levantar el contenedor con `./scripts/dev-docker-backend.sh`; para ejecución local, detén el proceso anterior con Ctrl+C y corre `./scripts/dev.sh` desde la raíz.
