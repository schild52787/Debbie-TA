"""Travel deals API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models import Deal, DealAlert

router = APIRouter()


# Pydantic schemas
class DealBase(BaseModel):
    source: str
    deal_type: str
    title: str
    description: str | None = None
    origin_airport: str | None = None
    destination_airport: str | None = None
    destination_region: str | None = None
    deal_price: float | None = None
    points_required: int | None = None
    airline: str | None = None
    travel_class: str | None = None


class DealResponse(DealBase):
    id: int
    created_at: datetime
    status: str
    quality_score: float | None = None

    class Config:
        from_attributes = True


class DealAlertResponse(BaseModel):
    id: int
    alert_type: str
    threshold_name: str | None = None
    deal_snapshot: dict
    notification_method: str
    status: str
    sent_at: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[DealResponse])
def get_deals(
    skip: int = 0,
    limit: int = 50,
    origin: Optional[str] = Query(None, description="Origin airport code"),
    region: Optional[str] = Query(None, description="Destination region"),
    deal_type: Optional[str] = Query(None, description="Deal type: flight, hotel, etc."),
    max_price: Optional[float] = Query(None, description="Maximum cash price"),
    max_points: Optional[int] = Query(None, description="Maximum points/miles"),
    status: Optional[str] = Query("active", description="Deal status"),
    db: Session = Depends(get_db)
):
    """Get all deals with optional filters"""
    query = db.query(Deal)

    # Apply filters
    if origin:
        query = query.filter(Deal.origin_airport == origin.upper())

    if region:
        query = query.filter(Deal.destination_region == region)

    if deal_type:
        query = query.filter(Deal.deal_type == deal_type)

    if max_price is not None:
        query = query.filter(Deal.deal_price <= max_price)

    if max_points is not None:
        query = query.filter(Deal.points_required <= max_points)

    if status:
        query = query.filter(Deal.status == status)

    # Order by newest first
    query = query.order_by(Deal.created_at.desc())

    deals = query.offset(skip).limit(limit).all()
    return deals


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get a specific deal by ID"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with ID {deal_id} not found"
        )

    return deal


@router.get("/alerts/", response_model=List[DealAlertResponse])
def get_deal_alerts(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = Query(None, description="Alert status"),
    db: Session = Depends(get_db)
):
    """Get all deal alerts"""
    query = db.query(DealAlert)

    if status:
        query = query.filter(DealAlert.status == status)

    query = query.order_by(DealAlert.created_at.desc())

    alerts = query.offset(skip).limit(limit).all()
    return alerts


@router.get("/search/msp-deals")
def search_msp_deals(
    region: Optional[str] = Query(None, description="Asia, Europe, etc."),
    max_cash: Optional[float] = Query(None),
    max_miles: Optional[int] = Query(None),
    travel_class: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search for deals from MSP with specific criteria"""
    query = db.query(Deal).filter(
        Deal.origin_airport == "MSP",
        Deal.status == "active"
    )

    if region:
        query = query.filter(Deal.destination_region == region)

    if max_cash is not None:
        query = query.filter(Deal.deal_price <= max_cash)

    if max_miles is not None:
        query = query.filter(Deal.points_required <= max_miles)

    if travel_class:
        query = query.filter(Deal.travel_class == travel_class)

    deals = query.order_by(Deal.quality_score.desc()).limit(20).all()

    return {
        "count": len(deals),
        "deals": deals
    }


@router.post("/alerts/{alert_id}/mark-read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    alert = db.query(DealAlert).filter(DealAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )

    alert.read_at = datetime.utcnow()
    db.commit()

    return {"message": "Alert marked as read"}


@router.post("/alerts/{alert_id}/dismiss")
def dismiss_alert(alert_id: int, db: Session = Depends(get_db)):
    """Dismiss an alert"""
    alert = db.query(DealAlert).filter(DealAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )

    alert.status = "dismissed"
    db.commit()

    return {"message": "Alert dismissed"}
