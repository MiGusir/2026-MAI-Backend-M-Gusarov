"""FastAPI app for final mini-NetBox project."""

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

import models
import schemas
from database import get_db


app = FastAPI(title="Mini NetBox ALL", version="1.0.0")


@app.get("/health", response_class=JSONResponse)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/", response_class=JSONResponse)
def root() -> JSONResponse:
    return JSONResponse(
        {
            "message": "Mini NetBox final project",
            "web_path": "/web/",
            "api_path": "/api/",
        }
    )


@app.get("/web/", response_class=HTMLResponse)
def web_home() -> str:
    return """
    <html>
      <head><title>Mini NetBox ALL</title></head>
      <body>
        <h1>Mini NetBox ALL</h1>
        <p>FastAPI + PostgreSQL + Alembic + Docker Compose + Nginx</p>
      </body>
    </html>
    """


@app.get("/api/users", response_class=JSONResponse)
def get_users(db: Session = Depends(get_db)) -> JSONResponse:
    users = db.query(models.User).all()
    data = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    return JSONResponse({"status": "ok", "count": len(data), "data": data})


def _create_user(payload: schemas.UserCreate, db: Session) -> JSONResponse:
    user = models.User(username=payload.username, email=payload.email)
    db.add(user)
    db.flush()
    profile = models.Profile(
        user_id=user.id,
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return JSONResponse({"status": "ok", "data": {"id": user.id, "username": user.username}})


@app.post("/api/users/create", response_class=JSONResponse)
def create_user_alias(payload: schemas.UserCreate, db: Session = Depends(get_db)) -> JSONResponse:
    return _create_user(payload, db)


@app.get("/api/categories", response_class=JSONResponse)
def get_categories(db: Session = Depends(get_db)) -> JSONResponse:
    categories = db.query(models.Category).all()
    data = [{"id": c.id, "slug": c.slug, "title": c.title} for c in categories]
    return JSONResponse({"status": "ok", "count": len(data), "data": data})


def _create_category(payload: schemas.CategoryCreate, db: Session) -> JSONResponse:
    category = models.Category(slug=payload.slug, title=payload.title)
    db.add(category)
    db.commit()
    db.refresh(category)
    return JSONResponse({"status": "ok", "data": {"id": category.id, "slug": category.slug}})


@app.post("/api/categories/create", response_class=JSONResponse)
def create_category_alias(payload: schemas.CategoryCreate, db: Session = Depends(get_db)) -> JSONResponse:
    return _create_category(payload, db)


@app.get("/api/servers", response_class=JSONResponse)
def get_servers(db: Session = Depends(get_db)) -> JSONResponse:
    servers = db.query(models.Server).all()
    data = [
        {
            "id": s.id,
            "hostname": s.hostname,
            "ip_address": s.ip_address,
            "status": s.status,
            "category_id": s.category_id,
            "owner_id": s.owner_id,
        }
        for s in servers
    ]
    return JSONResponse({"status": "ok", "count": len(data), "data": data})


def _create_server(payload: schemas.ServerCreate, db: Session) -> JSONResponse:
    category = db.query(models.Category).filter(models.Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="category not found")
    owner = db.query(models.User).filter(models.User.id == payload.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="owner not found")

    server = models.Server(
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        status=payload.status,
        category_id=payload.category_id,
        owner_id=payload.owner_id,
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return JSONResponse({"status": "ok", "data": {"id": server.id, "hostname": server.hostname}})


@app.post("/api/servers/create", response_class=JSONResponse)
def create_server_alias(payload: schemas.ServerCreate, db: Session = Depends(get_db)) -> JSONResponse:
    return _create_server(payload, db)


@app.get("/search", response_class=JSONResponse)
def search_entities(q: str = Query(..., min_length=1), db: Session = Depends(get_db)) -> JSONResponse:
    pattern = f"%{q}%"

    users = db.query(models.User).filter(
        or_(
            models.User.username.ilike(pattern),
            models.User.email.ilike(pattern),
        )
    ).all()
    categories = db.query(models.Category).filter(
        or_(
            models.Category.slug.ilike(pattern),
            models.Category.title.ilike(pattern),
        )
    ).all()
    servers = db.query(models.Server).filter(
        or_(
            models.Server.hostname.ilike(pattern),
            models.Server.ip_address.ilike(pattern),
        )
    ).all()

    data = {
        "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users],
        "categories": [{"id": c.id, "slug": c.slug, "title": c.title} for c in categories],
        "servers": [
            {
                "id": s.id,
                "hostname": s.hostname,
                "ip_address": s.ip_address,
                "status": s.status,
                "category_id": s.category_id,
                "owner_id": s.owner_id,
            }
            for s in servers
        ],
    }
    total = len(data["users"]) + len(data["categories"]) + len(data["servers"])
    return JSONResponse({"status": "ok", "query": q, "count": total, "data": data})
