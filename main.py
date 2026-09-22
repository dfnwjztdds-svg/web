from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine, func, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DB_PATH = "sqlite:///./site.db"
app = FastAPI(title="Tecnología para Gente Normal", description="Plataforma de soluciones tecnológicas para personas normales.")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Base(DeclarativeBase):
    pass

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text)
    icon: Mapped[str] = mapped_column(String(50), default="🔧")
    ordering: Mapped[int] = mapped_column(Integer, default=1)
    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)


class ArticleTag(Base):
    __tablename__ = "article_tags"

    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100), default="Andrés")
    featured_image: Mapped[str] = mapped_column(String(255), default="/static/img/placeholder.svg")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PUBLICADO")
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reading_time: Mapped[int] = mapped_column(Integer, default=5)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["Category"] = relationship(back_populates="articles")


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    how_to_use: Mapped[str] = mapped_column(Text)
    examples: Mapped[str] = mapped_column(Text)
    limitations: Mapped[str] = mapped_column(Text)
    faqs: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="PUBLICADO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SiteSetting(Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_categories(db: Session):
    return db.query(Category).order_by(Category.ordering, Category.name).all()


def get_featured_articles(db: Session, limit: int = 4):
    return db.query(Article).filter(Article.is_published.is_(True), Article.status == "PUBLICADO").order_by(Article.published_at.desc()).limit(limit).all()


def create_slug(value: str) -> str:
    return value.lower().strip().replace(" ", "-").replace("/", "-")


def seed_data(db: Session):
    existing = db.query(Category).count()
    if existing > 0:
        return

    categories = [
        {"name": "IA PARA HACER X", "slug": "ia", "description": "Herramientas de inteligencia artificial para tareas concretas del día a día.", "icon": "🤖", "ordering": 1},
        {"name": "CELULARES Y APLICACIONES", "slug": "celulares", "description": "Soluciones para Android, iPhone y el uso práctico del celular.", "icon": "📱", "ordering": 2},
        {"name": "COMPUTADORES", "slug": "computadores", "description": "Windows, rendimiento, seguridad, archivos y herramientas útiles.", "icon": "💻", "ordering": 3},
        {"name": "ESTUDIO Y PRODUCTIVIDAD", "slug": "estudio", "description": "Recursos para aprender, organizarse y trabajar mejor.", "icon": "📚", "ordering": 4},
        {"name": "TECNOLOGÍA PARA NEGOCIOS", "slug": "negocios", "description": "Herramientas para pequeños negocios y trabajo práctico.", "icon": "🏪", "ordering": 5},
        {"name": "PROGRAMACIÓN PARA PRINCIPIANTES", "slug": "programacion", "description": "Aprende Python, HTML, JavaScript, APIs y proyectos reales.", "icon": "💡", "ordering": 6},
        {"name": "HERRAMIENTAS", "slug": "herramientas", "description": "Calculadoras, generadores, conversores y recursos útiles.", "icon": "🧰", "ordering": 7},
    ]
    for data in categories:
        db.add(Category(**data))
    db.commit()

    category_map = {c.slug: c.id for c in db.query(Category).all()}

    articles = [
        {
            "title": "Cómo resumir un PDF con IA sin perder información importante",
            "slug": "resumir-pdf-con-ia",
            "excerpt": "Guía práctica para resumir documentos largos utilizando IA con un enfoque realista y útil.",
            "content": "<h2>¿Para qué sirve?</h2><p>Cuando tienes un PDF largo, una IA puede ayudarte a identificar ideas clave, detectar puntos importantes y ahorrar tiempo. Pero también hay límites: no reemplaza la lectura crítica.</p><h3>Cómo hacerlo paso a paso</h3><ol><li>Sube el documento a una herramienta de IA.</li><li>Elige el tipo de resumen: breve, ejecutivo o detallado.</li><li>Verifica fechas, nombres y datos numéricos.</li><li>Usa el resumen como punto de partida, no como sustituto de la lectura.</li></ol><h3>Ventajas</h3><ul><li>Ahorra tiempo en documentos largos.</li><li>Ayuda a extraer ideas clave.</li><li>Facilita el estudio o la revisión.</li></ul><h3>Limitaciones</h3><p>Puede confundir datos, nombres o conceptos. Debe revisarse siempre.</p>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["ia"],
            "status": "PUBLICADO",
            "reading_time": 5,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "IA para estudiar matemáticas: 5 formas útiles de aprender mejor",
            "slug": "ia-para-estudiar-matematicas",
            "excerpt": "Usar IA para practicar, resolver dudas y organizar conceptos matemáticos puede ser muy útil.",
            "content": "<h2>La idea clave</h2><p>La IA no debe hacer los ejercicios por ti; debe ayudarte a entenderlos mejor.</p><h3>Qué puedes hacer</h3><ul><li>Explicar un concepto paso a paso.</li><li>Crear ejercicios parecidos.</li><li>Revisar errores en un problema.</li><li>Organizar un plan de estudio.</li></ul><h3>Importante</h3><p>La calidad depende de cómo hagas la pregunta. Pide explicaciones simples y ejemplo paso a paso.</p>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["ia"],
            "status": "PUBLICADO",
            "reading_time": 6,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "Cómo liberar espacio en Android sin borrar lo importante",
            "slug": "liberar-espacio-android",
            "excerpt": "Técnicas prácticas para limpiar almacenamiento, borrar caché y recuperar espacio útil.",
            "content": "<h2>Qué revisar primero</h2><p>Antes de limpiar, revisa fotos, videos, mensajes y apps pesadas.</p><h3>Pasos sencillos</h3><ol><li>Ve a Ajustes > Almacenamiento.</li><li>Revisa aplicaciones grandes.</li><li>Borra caché si la app lo permite.</li><li>Mueve fotos y videos a una nube o disco externo.</li></ol><h3>Recomendación</h3><p>No borres en caliente sin revisar antes. Algunas apps guardan archivos útiles.</p>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["celulares"],
            "status": "PUBLICADO",
            "reading_time": 4,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "Cómo pasar fotos del celular al PC sin complicarte",
            "slug": "pasar-fotos-celular-pc",
            "excerpt": "Métodos sencillos para transferir fotos usando USB, nube o aplicaciones directas.",
            "content": "<h2>Opción más rápida</h2><p>Conectar el celular por USB y copiar las fotos en la carpeta de imágenes del computador suele ser la forma más directa.</p><h3>Otras opciones</h3><ul><li>Google Photos.</li><li>Drive.</li><li>AirDrop en dispositivos compatibles.</li></ul>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["celulares"],
            "status": "PUBLICADO",
            "reading_time": 4,
            "is_featured": False,
            "is_published": True,
        },
        {
            "title": "Windows lento: 7 mejoras prácticas que puedes hacer hoy mismo",
            "slug": "windows-lento-mejoras-practicas",
            "excerpt": "Guía para mejorar el rendimiento de un PC cuando parece estar muy lento.",
            "content": "<h2>Antes de reinstalar</h2><p>Muchas veces el problema no es el hardware, sino programas pesados o archivos acumulados.</p><h3>Revisa</h3><ul><li>Inicio de Windows.</li><li>Aplicaciones pesadas.</li><li>Espacio disponible en disco.</li><li>Actualizaciones y antivirus.</li></ul>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["computadores"],
            "status": "PUBLICADO",
            "reading_time": 5,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "Cómo organizar apuntes digitales con Google Drive y Docs",
            "slug": "organizar-apuntes-google-drive",
            "excerpt": "Un sistema simple para guardar, ordenar y buscar apuntes sin perder archivos.",
            "content": "<h2>La mejor estructura</h2><p>Usa carpetas por materia, subcarpetas por tema y archivos nombrados con fechas claras.</p><h3>Ejemplo</h3><ul><li>Universidad/Matemáticas/Clase 1</li><li>Universidad/Historia/Resumen</li></ul><p>Esto reduce la frustración cuando necesitas buscar algo rápido.</p>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["estudio"],
            "status": "PUBLICADO",
            "reading_time": 5,
            "is_featured": False,
            "is_published": True,
        },
        {
            "title": "Cómo controlar inventario básico de un pequeño negocio sin software caro",
            "slug": "control-inventario-pequeno-negocio",
            "excerpt": "Un sistema sencillo con Excel o Google Sheets para llevar el control de productos y ventas.",
            "content": "<h2>El problema</h2><p>Muchos negocios pierden ventas por no saber qué tienen disponible ni cuánto venden.</p><h3>Solución práctica</h3><ul><li>Lista de productos</li><li>Stock inicial</li><li>Entradas y salidas</li><li>Reporte simple</li></ul>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["negocios"],
            "status": "PUBLICADO",
            "reading_time": 6,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "Cómo crear un sistema de inventario sencillo con Python",
            "slug": "inventario-python-principiante",
            "excerpt": "Proyecto práctico para aprender Python creando una pequeña app de inventario.",
            "content": "<h2>Objetivo</h2><p>Crear una herramienta para registrar productos, cantidades y precios con un código claro.</p><h3>Qué aprenderás</h3><ul><li>Listas y diccionarios.</li><li>Funciones.</li><li>Entrada y salida por consola.</li><li>Pequeña lógica de negocio.</li></ul><pre>productos = {'manzana': 5, 'leche': 3}</pre>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["programacion"],
            "status": "PUBLICADO",
            "reading_time": 7,
            "is_featured": True,
            "is_published": True,
        },
        {
            "title": "Generador de códigos QR: ¿para qué sirve y cómo usarlo bien?",
            "slug": "generador-codigos-qr",
            "excerpt": "Un ejemplo de herramienta útil para enlaces, contactos y pagos rápidos.",
            "content": "<h2>¿Para qué sirve?</h2><p>Los códigos QR permiten abrir enlaces, compartir información o conectar con formularios con un solo escaneo.</p><h3>Usos comunes</h3><ul><li>Enlaces a sitios web.</li><li>Datos de contacto.</li><li>WhatsApp o redes sociales.</li><li>Pagos o formularios.</li></ul>",
            "author": "Andrés",
            "featured_image": "/static/img/placeholder.svg",
            "category_id": category_map["herramientas"],
            "status": "PUBLICADO",
            "reading_time": 4,
            "is_featured": False,
            "is_published": True,
        },
    ]

    for data in articles:
        db.add(Article(**data))
    db.commit()

    tools = [
        {
            "name": "Calculadora de porcentajes",
            "slug": "calculadora-porcentajes",
            "summary": "Calcula porcentajes rápidos para descuentos, aumentos o proporciones.",
            "description": "Ideal para comprar, comparar precios o entender aumentos en un vistazo.",
            "how_to_use": "Escribe el valor inicial y el porcentaje. La herramienta devuelve el resultado final.",
            "examples": "Ejemplo: 2500 con 15% de descuento = 2125.",
            "limitations": "No reemplaza una hoja de cálculo para cálculos complejos.",
            "faqs": "- ¿Sirve para descuentos? Sí. - ¿Puede calcular aumentos? Sí.",
            "status": "PUBLICADO",
        },
        {
            "name": "Generador de códigos QR",
            "slug": "generador-codigos-qr-herramienta",
            "summary": "Genera un código QR a partir de texto o un enlace.",
            "description": "Útil para compartir enlaces de sitios, WhatsApp, archivos o formularios.",
            "how_to_use": "Escribe la URL o texto y genera la imagen del QR.",
            "examples": "Crea un QR para tu portafolio, formulario o enlace de contacto.",
            "limitations": "La calidad depende del contenido y del tamaño de la imagen.",
            "faqs": "- ¿Se puede descargar? Sí. - ¿Funciona sin conexión? Sí si ya se genera la imagen.",
            "status": "PUBLICADO",
        },
        {
            "name": "Conversor de unidades",
            "slug": "convertidor-unidades",
            "summary": "Convierte peso, longitud, temperatura y cantidad entre múltiples unidades.",
            "description": "Útil cuando trabajas con medidas en diferentes sistemas.",
            "how_to_use": "Selecciona la unidad de origen y la de destino, luego escribe el valor.",
            "examples": "De kilogramos a libras, o de centímetros a pulgadas.",
            "limitations": "Este ejemplo es una herramienta básica; no reemplaza conversiones profesionales muy específicas.",
            "faqs": "- ¿Puede convertir temperatura? Sí. - ¿Es útil para trabajo escolar? Sí.",
            "status": "PUBLICADO",
        },
    ]
    for data in tools:
        db.add(Tool(**data))
    db.commit()

    setting = SiteSetting(key="site_name", value="TECNOLOGÍA PARA GENTE NORMAL")
    db.add(setting)
    db.commit()


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_data(db)
        db.commit()
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    categories = get_categories(db)
    articles = get_featured_articles(db, 4)
    tools = db.query(Tool).limit(3).all()
    html = templates.get_template("index.html").render(
        request=request,
        categories=categories,
        featured_articles=articles,
        tools=tools,
    )
    return HTMLResponse(content=html)


@app.get("/categoria/{slug}", response_class=HTMLResponse)
def category_page(slug: str, request: Request, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    articles = db.query(Article).filter(Article.category_id == category.id, Article.is_published.is_(True)).order_by(Article.published_at.desc()).all()
    html = templates.get_template("category.html").render(
        request=request,
        category=category,
        articles=articles,
        categories=get_categories(db),
    )
    return HTMLResponse(content=html)


@app.get("/articulo/{slug}", response_class=HTMLResponse)
def article_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    related = db.query(Article).filter(Article.category_id == article.category_id, Article.id != article.id, Article.is_published.is_(True)).limit(3).all()
    html = templates.get_template("article_detail.html").render(
        request=request,
        article=article,
        related=related,
        categories=get_categories(db),
    )
    return HTMLResponse(content=html)


@app.get("/herramienta/{slug}", response_class=HTMLResponse)
def tool_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.slug == slug).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")
    html = templates.get_template("tool_detail.html").render(
        request=request,
        tool=tool,
        categories=get_categories(db),
    )
    return HTMLResponse(content=html)


@app.get("/buscar", response_class=HTMLResponse)
def search_page(request: Request, q: Optional[str] = None, db: Session = Depends(get_db)):
    query = q or ""
    results = []
    if query:
        search_term = f"%{query.lower()}%"
        results = db.query(Article).filter(
            or_(
                func.lower(Article.title).like(search_term),
                func.lower(Article.excerpt).like(search_term),
                func.lower(Article.content).like(search_term),
            )
        ).order_by(Article.published_at.desc()).all()
    html = templates.get_template("search.html").render(
        request=request,
        query=query,
        results=results,
        categories=get_categories(db),
    )
    return HTMLResponse(content=html)


@app.post("/buscar")
def search_submit(request: Request, q: str = Form(default=""), db: Session = Depends(get_db)):
    return RedirectResponse(f"/buscar?q={q}", status_code=303)


@app.get("/nosotros", response_class=HTMLResponse)
def about_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("about.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/contacto", response_class=HTMLResponse)
def contact_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("contact.html").render(request=request, categories=get_categories(db), success=False)
    return HTMLResponse(content=html)


@app.post("/contacto")
def contact_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    db.add(ContactMessage(name=name, email=email, subject=subject, message=message))
    db.commit()
    html = templates.get_template("contact.html").render(request=request, categories=get_categories(db), success=True)
    return HTMLResponse(content=html)


@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.published_at.desc()).all()
    tools = db.query(Tool).order_by(Tool.created_at.desc()).all()
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(10).all()
    html = templates.get_template("admin.html").render(
        request=request,
        articles=articles,
        tools=tools,
        messages=messages,
        categories=get_categories(db),
    )
    return HTMLResponse(content=html)


@app.post("/admin/articulo/nuevo")
def admin_create_article(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(...),
    content: str = Form(...),
    author: str = Form("Andrés"),
    category_id: int = Form(...),
    status: str = Form("PUBLICADO"),
    db: Session = Depends(get_db),
):
    final_slug = slug or create_slug(title)
    article = Article(
        title=title,
        slug=final_slug,
        excerpt=excerpt,
        content=content,
        author=author,
        category_id=category_id,
        status=status,
        is_published=status == "PUBLICADO",
    )
    db.add(article)
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/herramienta/nueva")
def admin_create_tool(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    summary: str = Form(...),
    description: str = Form(...),
    how_to_use: str = Form(...),
    examples: str = Form(...),
    limitations: str = Form(...),
    faqs: str = Form(...),
    db: Session = Depends(get_db),
):
    final_slug = slug or create_slug(name)
    tool = Tool(
        name=name,
        slug=final_slug,
        summary=summary,
        description=description,
        how_to_use=how_to_use,
        examples=examples,
        limitations=limitations,
        faqs=faqs,
        status="PUBLICADO",
    )
    db.add(tool)
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@app.get("/auditoria-calidad", response_class=HTMLResponse)
def quality_audit(request: Request, db: Session = Depends(get_db)):
    checklist = [
        ("Originalidad", "VERDE", "El contenido se enfoca en soluciones reales y no en noticias genéricas."),
        ("Utilidad", "VERDE", "Cada artículo responde a un problema concreto del usuario."),
        ("Calidad", "VERDE", "La estructura está diseñada para claridad y lectura útil."),
        ("Navegación", "VERDE", "Hay categorías, buscador y enlaces internos coherentes."),
        ("Privacidad", "AMARILLO", "Se necesita revisar consentimiento y políticas según el uso real."),
        ("SEO técnico", "VERDE", "Las URLs, metadatos y estructura están pensadas para crecimiento."),
        ("Publicidad", "VERDE", "El sitio está preparado para monetización sin priorizar anuncios sobre contenido."),
    ]
    html = templates.get_template("quality_audit.html").render(request=request, checklist=checklist, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/politica-privacidad", response_class=HTMLResponse)
def privacy_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("legal/privacy.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/politica-cookies", response_class=HTMLResponse)
def cookies_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("legal/cookies.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/terminos-condiciones", response_class=HTMLResponse)
def terms_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("legal/terms.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/aviso-legal", response_class=HTMLResponse)
def legal_notice_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("legal/legal_notice.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/copyright", response_class=HTMLResponse)
def copyright_page(request: Request, db: Session = Depends(get_db)):
    html = templates.get_template("legal/copyright.html").render(request=request, categories=get_categories(db))
    return HTMLResponse(content=html)


@app.get("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap():
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
      <url><loc>https://example.com/</loc></url>
      <url><loc>https://example.com/nosotros</loc></url>
      <url><loc>https://example.com/contacto</loc></url>
      <url><loc>https://example.com/politica-privacidad</loc></url>
      <url><loc>https://example.com/politica-cookies</loc></url>
      <url><loc>https://example.com/terminos-condiciones</loc></url>
      <url><loc>https://example.com/aviso-legal</loc></url>
      <url><loc>https://example.com/copyright</loc></url>
    </urlset>
    """


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "El sitio está funcionando correctamente."}
