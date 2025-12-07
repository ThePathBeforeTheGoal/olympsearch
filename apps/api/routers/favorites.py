# apps/api/routers/favorites.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from sqlalchemy.exc import IntegrityError
from shared.db.engine import get_session
from apps.api.models.favorite import Favorite
from auth import get_current_user

router = APIRouter(prefix="/api/v1/favorites", tags=["favorites"])

@router.post("/add", status_code=201)
def add_favorite(payload: dict, session: Session = Depends(get_session), user = Depends(get_current_user)):
    olympiad_id = payload.get("olympiad_id")
    if not olympiad_id:
        raise HTTPException(status_code=400, detail="Missing olympiad_id")
    fav = Favorite(user_id=user.id, olympiad_id=int(olympiad_id))
    try:
        session.add(fav)
        session.commit()
        session.refresh(fav)
        return {"message": "Added", "id": fav.id, "added_at": fav.added_at}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Already added or limit reached")
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not add favorite")

@router.get("/", response_model=List[Favorite])
def get_favorites(session: Session = Depends(get_session), user = Depends(get_current_user)):
    stmt = select(Favorite).where(Favorite.user_id == user.id, Favorite.is_archived == False)
    return session.exec(stmt).all()

@router.delete("/{fav_id}", status_code=204)
def delete_favorite(fav_id: int, session: Session = Depends(get_session), user = Depends(get_current_user)):
    fav = session.get(Favorite, fav_id)
    if not fav or fav.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(fav)
    session.commit()
    return
