# apps/api/routers/organizers.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from apps.api.crud.crud_organizer import list_organizers, get_organizer_by_slug, get_olympiads_for_organizer
from apps.api.models.organizer import Organizer
from apps.api.models_olympiad import Olympiad

router = APIRouter(prefix="/api/v1/organizers", tags=["organizers"])

@router.get("/", response_model=List[Organizer])
def api_list_organizers(limit: int = Query(100, ge=1, le=1000)):
    return list_organizers(limit=limit)

@router.get("/{slug}", response_model=Organizer)
def api_get_organizer(slug: str):
    org = get_organizer_by_slug(slug)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return org

@router.get("/{slug}/olympiads", response_model=List[Olympiad])
def api_get_organizer_olympiads(slug: str):
    ols = get_olympiads_for_organizer(slug)
    return ols
