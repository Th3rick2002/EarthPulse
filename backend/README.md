# TrendScope backend

Backend planificado con FastAPI y Python 3.11. `Dockerfile` fija `python:3.11-slim`; usa esa versión para desarrollo local. El entorno virtual `venv/` que pueda existir en tu equipo no se comparte ni se versiona.

## Requisitos

- Python 3.11 y `venv`.
- pip.

Comprueba la versión:

```bash
python3.11 --version
```

## Crear entorno e instalar dependencias

Desde `backend/`:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Windows PowerShell activa el entorno con `.venv\Scripts\Activate.ps1`.

## Ejecutar

Una vez creado `app/main.py` con el objeto `app` de FastAPI:

```bash
uvicorn app.main:app --reload
```

La API local quedará en `http://127.0.0.1:8000`; FastAPI publica documentación interactiva en `/docs`.

## Estado actual

El backend aún no incluye `app/main.py` ni routers. La lista inicial de dependencias cubre el stack del plan; no hay que crear secretos reales en el repositorio. Usa `.env.example` como plantilla y variables de entorno para credenciales.

Consulta [`../docs/specs/data-and-api.md`](../docs/specs/data-and-api.md) para el contrato, los datos y las fuentes.
