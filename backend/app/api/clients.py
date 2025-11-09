"""Client management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import Client

router = APIRouter()


# Pydantic schemas
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    preferred_contact_method: str = "email"
    travel_preferences: dict = {}
    notes: str | None = None
    status: str = "active"


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    preferred_contact_method: str | None = None
    travel_preferences: dict | None = None
    notes: str | None = None
    status: str | None = None


class ClientResponse(ClientBase):
    id: int
    full_name: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ClientResponse])
def get_clients(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """Get all clients"""
    query = db.query(Client)

    if status:
        query = query.filter(Client.status == status)

    clients = query.offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Check if email already exists
    existing = db.query(Client).filter(Client.email == client_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client with email {client_data.email} already exists"
        )

    client = Client(**client_data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing client"""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    # Update only provided fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client"""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    db.delete(client)
    db.commit()

    return None


@router.get("/{client_id}/itineraries")
def get_client_itineraries(client_id: int, db: Session = Depends(get_db)):
    """Get all itineraries for a specific client"""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    return client.itineraries


@router.get("/{client_id}/disputes")
def get_client_disputes(client_id: int, db: Session = Depends(get_db)):
    """Get all disputes for a specific client"""
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )

    return client.disputes
