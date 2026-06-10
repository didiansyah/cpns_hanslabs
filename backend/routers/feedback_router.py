from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from models import Feedback
from routers.user_router import require_auth

router = APIRouter(redirect_slashes=False)


class FeedbackReq(BaseModel):
    category: str = Field("other", max_length=40)
    rating: int | None = Field(None, ge=1, le=5)
    message: str = Field(..., min_length=3, max_length=3000)
    path: str | None = Field(None, max_length=255)


@router.post("")
@router.post("/")
def create_feedback(req: FeedbackReq, request: Request, user=Depends(require_auth), db: Session = Depends(get_db)):
    item = Feedback(
        user_id=user.id,
        category=req.category.strip()[:40] or "other",
        rating=req.rating,
        message=req.message.strip(),
        path=(req.path or str(request.url.path))[:255],
        user_agent=(request.headers.get("User-Agent", "") or "")[:500],
        status="open",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"ok": True, "data": {"id": item.id, "status": item.status}}
