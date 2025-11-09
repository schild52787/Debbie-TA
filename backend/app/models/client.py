"""Client model for managing travel agency clients"""
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, IDMixin


class Client(Base, IDMixin, TimestampMixin):
    """Client information"""
    __tablename__ = "clients"

    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20))

    # Contact Preferences
    preferred_contact_method = Column(String(20), default="email")  # email, phone, sms

    # Travel Preferences
    travel_preferences = Column(JSON, default=dict)  # Store preferences as JSON
    # Example: {
    #   "preferred_airlines": ["Delta", "United"],
    #   "preferred_hotels": ["Marriott", "Hyatt"],
    #   "seat_preference": "aisle",
    #   "meal_preference": "vegetarian",
    #   "special_requests": "...",
    #   "loyalty_programs": {
    #       "delta": "1234567890",
    #       "marriott": "0987654321"
    #   }
    # }

    # Notes
    notes = Column(Text)

    # Status
    status = Column(String(20), default="active")  # active, inactive, archived

    # Relationships
    itineraries = relationship("Itinerary", back_populates="client", cascade="all, delete-orphan")
    disputes = relationship("Dispute", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.first_name} {self.last_name} ({self.email})>"

    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
