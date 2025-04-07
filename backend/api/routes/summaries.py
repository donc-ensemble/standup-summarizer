from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.summary import Summary
from db.schemas.summary import SummaryCreate, SummaryResponse

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
def create_summary(summary: SummaryCreate, db: Session = Depends(get_db)):
    db_summary = Summary(**summary.model_dump())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

@router.get("/{summary_id}", response_model=SummaryResponse)
def read_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.get("/", response_model=list[SummaryResponse])
def read_summaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Summary).offset(skip).limit(limit).all()

@router.get("/channel/{channel_id}", response_model=list[SummaryResponse])
def read_summaries_by_channel(channel_id: int, db: Session = Depends(get_db)):
    return db.query(Summary).filter(Summary.channel_id == channel_id).all()