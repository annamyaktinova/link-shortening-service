from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from db.models import Link
from schemas.link import ShortenRequest, LinkResponse, StatsResponse, UpdateLinkRequest
from services.shortener import generate_short_code
from db.database import get_db
from dependencies import get_current_user
import redis
from config import REDIS_HOST, REDIS_PORT

router = APIRouter()

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True, socket_timeout=2.0, socket_connect_timeout=2.0)

CACHE_TTL = 3600  # сек

@router.post("/links/shorten", response_model=LinkResponse)
async def shorten_url(
    request: ShortenRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):

    if request.custom_alias:
        existing = db.query(Link).filter(Link.custom_alias == request.custom_alias).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom alias already exists")
    
    if request.custom_alias:
        short_code = request.custom_alias
    else:
        attempts = 0
        short_code = generate_short_code()
        while db.query(Link).filter(Link.short_code == short_code).first() and attempts < 10:
            short_code = generate_short_code()
            attempts += 1
        if db.query(Link).filter(Link.short_code == short_code).first():
            raise HTTPException(status_code=500, detail="Unable to generate unique short code, try again")
    link = Link(
        original_url=request.original_url,
        short_code=short_code,
        custom_alias=request.custom_alias,
        expires_at=request.expires_at,
        user_id=current_user["id"] if current_user else None
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    try:
        cache.setex(f"link:{short_code}", CACHE_TTL, link.original_url)
    except Exception:
        pass
    return LinkResponse.from_orm(link)

@router.get("/links/{short_code}")
async def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    # Try cache first
    cached = None
    try:
        cached = cache.get(f"link:{short_code}")
    except Exception:
        cached = None

    link = db.query(Link).filter(
        (Link.short_code == short_code) | (Link.custom_alias == short_code)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        db.delete(link)
        db.commit()
        try:
            cache.delete(f"link:{short_code}")
        except Exception:
            pass
        raise HTTPException(status_code=410, detail="Link expired")
    
    link.clicks += 1
    link.last_accessed = datetime.now(timezone.utc)
    db.commit()

    try:
        if not cached:
            cache.setex(f"link:{short_code}", CACHE_TTL, link.original_url)
    except Exception:
        pass

    return RedirectResponse(url=link.original_url)

@router.delete("/links/{short_code}")
async def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    link = db.query(Link).filter(
        (Link.short_code == short_code) | (Link.custom_alias == short_code)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if current_user and link.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(link)
    db.commit()
    try:
        cache.delete(f"link:{short_code}")
        if link.custom_alias:
            cache.delete(f"link:{link.custom_alias}")
    except Exception:
        pass
    return {"message": "Link deleted"}

@router.put("/links/{short_code}", response_model=LinkResponse)
async def update_link(
    short_code: str,
    request: UpdateLinkRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    link = db.query(Link).filter(
        (Link.short_code == short_code) | (Link.custom_alias == short_code)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if current_user and link.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if request.original_url:
        link.original_url = request.original_url
    if request.custom_alias:
        existing = db.query(Link).filter(Link.custom_alias == request.custom_alias).first()
        if existing and existing.id != link.id:
            raise HTTPException(status_code=400, detail="Custom alias already exists")
        link.custom_alias = request.custom_alias
    db.commit()
    db.refresh(link)
    try:
        cache.setex(f"link:{link.short_code}", CACHE_TTL, link.original_url)
        if link.custom_alias:
            cache.setex(f"link:{link.custom_alias}", CACHE_TTL, link.original_url)
    except Exception:
        pass
    return LinkResponse.from_orm(link)

@router.get("/links/{short_code}/stats", response_model=StatsResponse)
async def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(
        (Link.short_code == short_code) | (Link.custom_alias == short_code)
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    return StatsResponse(
        original_url=link.original_url,
        created_at=link.created_at,
        clicks=link.clicks,
        last_accessed=link.last_accessed
    )

@router.get("/links/search")
async def search_by_original_url(
    original_url: str = Query(...),
    db: Session = Depends(get_db)
):
    links = db.query(Link).filter(Link.original_url == original_url).all()
    if not links:
        raise HTTPException(status_code=404, detail="No links found for this URL")
    
    return [LinkResponse.from_orm(link) for link in links]