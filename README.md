# Tecnología para Gente Normal

Proyecto MVP de una plataforma de soluciones tecnológicas orientada a personas no expertas, estudiantes, emprendedores y pequeños negocios.

## Stack

- Python 3.14
- FastAPI
- Jinja2
- SQLAlchemy
- SQLite para desarrollo inicial

## Ejecución

1. Instala dependencias:
   `python -m pip install -r requirements.txt`
2. Ejecuta el servidor:
   `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
3. Abre:
   `http://localhost:8000`

## Admin

- Ruta: `/admin`
- El contenido se puede crear desde la interfaz administrativa.

## SEO y calidad

El proyecto incluye una arquitectura básica para:

- sitemap.xml
- robots.txt
- buscador interno
- páginas legales
- página de auditoría de calidad
- estructura de categorías y contenido útil

## Nota

Este es un MVP funcional y preparado para crecer. El contenido visible es realista y útil, pero debe revisarse antes de publicación final en producción.
