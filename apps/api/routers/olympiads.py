# apps/api/routers/olympiads.py
from fastapi import APIRouter, HTTPException
from typing import List
from apps.api.models_olympiad import Olympiad
from apps.api.crud_olympiad import create_olympiad, list_olympiads, get_olympiad

router = APIRouter(prefix="/api/v1/olympiads", tags=["olympiads"])

@router.post("/", response_model=Olympiad)
def create(item: Olympiad):
    return create_olympiad(item)

@router.get("/", response_model=List[Olympiad])
def read_all(limit: int = 100):
    return list_olympiads(limit=limit)

@router.get("/{olympiad_id}", response_model=Olympiad)
def read_one(olympiad_id: int):
    obj = get_olympiad(olympiad_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj
