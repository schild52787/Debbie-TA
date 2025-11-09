"""Itinerary models for managing travel plans"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, IDMixin


class Itinerary(Base, IDMixin, TimestampMixin):
    """Main itinerary container"""
    __tablename__ = "itineraries"

    # Client relationship
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    client = relationship("Client", back_populates="itineraries")

    # Basic Information
    trip_name = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    destination = Column(String(200))

    # Status
    status = Column(String(20), default="planned")  # planned, confirmed, in_progress, completed, cancelled

    # Total Cost
    total_cost = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")

    # Notes
    notes = Column(Text)

    # Special Requirements
    special_requirements = Column(JSON, default=dict)
    # Example: {"wheelchair_access": true, "dietary": "gluten-free"}

    # Relationships
    flights = relationship("Flight", back_populates="itinerary", cascade="all, delete-orphan")
    hotels = relationship("Hotel", back_populates="itinerary", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="itinerary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Itinerary {self.trip_name} for Client {self.client_id}>"


class Flight(Base, IDMixin, TimestampMixin):
    """Flight details within an itinerary"""
    __tablename__ = "flights"

    # Itinerary relationship
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    itinerary = relationship("Itinerary", back_populates="flights")

    # Flight Information
    airline = Column(String(100), nullable=False)
    flight_number = Column(String(20), nullable=False)
    confirmation_number = Column(String(50))

    # Route
    departure_airport = Column(String(10), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)

    # Booking Details
    booking_class = Column(String(20))  # economy, premium_economy, business, first
    seat_number = Column(String(10))
    frequent_flyer_number = Column(String(50))

    # Cost
    cost = Column(Numeric(10, 2))
    miles_used = Column(Integer)  # If booked with miles
    currency = Column(String(3), default="USD")

    # Status
    status = Column(String(20), default="confirmed")  # confirmed, checked_in, boarded, completed, cancelled, delayed

    # Additional Info
    terminal = Column(String(10))
    gate = Column(String(10))
    baggage_allowance = Column(String(100))
    notes = Column(Text)

    def __repr__(self):
        return f"<Flight {self.airline} {self.flight_number} {self.departure_airport}-{self.arrival_airport}>"


class Hotel(Base, IDMixin, TimestampMixin):
    """Hotel booking within an itinerary"""
    __tablename__ = "hotels"

    # Itinerary relationship
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    itinerary = relationship("Itinerary", back_populates="hotels")

    # Hotel Information
    hotel_name = Column(String(200), nullable=False)
    hotel_chain = Column(String(100))  # Marriott, Hyatt, etc.
    confirmation_number = Column(String(50))

    # Location
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    phone = Column(String(20))

    # Dates
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)

    # Room Details
    room_type = Column(String(100))
    number_of_rooms = Column(Integer, default=1)
    number_of_guests = Column(Integer, default=1)

    # Loyalty Program
    loyalty_program_number = Column(String(50))

    # Cost
    cost_per_night = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    points_used = Column(Integer)  # If booked with points
    currency = Column(String(3), default="USD")

    # Status
    status = Column(String(20), default="confirmed")  # confirmed, checked_in, checked_out, cancelled

    # Additional Info
    amenities = Column(JSON, default=list)  # ["wifi", "breakfast", "parking"]
    special_requests = Column(Text)
    notes = Column(Text)

    def __repr__(self):
        return f"<Hotel {self.hotel_name} in {self.city}>"


class Activity(Base, IDMixin, TimestampMixin):
    """Activities, tours, or other bookings within an itinerary"""
    __tablename__ = "activities"

    # Itinerary relationship
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    itinerary = relationship("Itinerary", back_populates="activities")

    # Activity Information
    activity_type = Column(String(50))  # cruise, tour, car_rental, restaurant, event, etc.
    name = Column(String(200), nullable=False)
    provider = Column(String(200))  # Viking Cruise, Enterprise, etc.
    confirmation_number = Column(String(50))

    # Date & Time
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    duration = Column(String(50))  # "2 hours", "7 days", etc.

    # Location
    location = Column(String(500))
    meeting_point = Column(String(500))

    # Participants
    number_of_participants = Column(Integer, default=1)

    # Cost
    cost = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")

    # Status
    status = Column(String(20), default="confirmed")  # confirmed, completed, cancelled

    # Additional Details
    details = Column(JSON, default=dict)
    # Example for cruise: {
    #   "ship_name": "Viking Star",
    #   "cabin_number": "5042",
    #   "deck": "5",
    #   "dining_time": "late"
    # }
    notes = Column(Text)

    def __repr__(self):
        return f"<Activity {self.activity_type}: {self.name}>"
