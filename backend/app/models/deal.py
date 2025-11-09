"""Deal models for tracking travel deals and alerts"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, JSON, Index
from .base import Base, TimestampMixin, IDMixin


class Deal(Base, IDMixin, TimestampMixin):
    """Travel deal information"""
    __tablename__ = "deals"

    # Source Information
    source = Column(String(100), nullable=False, index=True)  # ThePointsGuy, ThriftyTravel, API, etc.
    source_url = Column(String(500))
    original_post_date = Column(DateTime)

    # Deal Type
    deal_type = Column(String(50), nullable=False)  # flight, hotel, package, cruise, award
    category = Column(String(50))  # business_class, economy, premium_economy, luxury_hotel, etc.

    # Title & Description
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Route/Location Information
    origin_airport = Column(String(10))
    destination_airport = Column(String(10))
    destination_city = Column(String(200))
    destination_country = Column(String(100))
    destination_region = Column(String(100))  # Europe, Asia, South America, etc.

    # Travel Dates
    travel_start_date = Column(DateTime)
    travel_end_date = Column(DateTime)
    booking_deadline = Column(DateTime)
    blackout_dates = Column(JSON, default=list)

    # Pricing - Cash
    original_price = Column(Numeric(10, 2))
    deal_price = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    discount_percentage = Column(Numeric(5, 2))

    # Pricing - Points/Miles
    points_required = Column(Integer)
    points_program = Column(String(100))  # SkyMiles, Ultimate Rewards, etc.
    cash_equivalent_value = Column(Numeric(10, 2))  # CPP calculation

    # Provider Information
    airline = Column(String(100))
    hotel_chain = Column(String(100))
    cruise_line = Column(String(100))
    alliance = Column(String(50))  # SkyTeam, Star Alliance, OneWorld

    # Travel Class
    travel_class = Column(String(50))  # economy, premium_economy, business, first

    # Deal Quality Metrics
    quality_score = Column(Numeric(3, 2))  # 0.0 - 10.0
    is_exceptional = Column(Boolean, default=False)  # Exceptional deal flag
    cents_per_point = Column(Numeric(5, 2))  # For award deals

    # Restrictions & Requirements
    restrictions = Column(JSON, default=dict)
    # Example: {
    #   "minimum_stay": 5,
    #   "advance_booking": 21,
    #   "refundable": false,
    #   "changeable": true,
    #   "segments": 1,
    #   "layovers": ["AMS"]
    # }

    # Status & Tracking
    status = Column(String(20), default="active")  # active, expired, sold_out, verified, false_alarm
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)

    # Expiration
    expires_at = Column(DateTime)

    # Tags for filtering
    tags = Column(JSON, default=list)  # ["msp", "europe", "business", "delta"]

    # Raw Data
    raw_data = Column(JSON, default=dict)  # Store original scraped data

    def __repr__(self):
        return f"<Deal {self.title} ({self.deal_type})>"

    # Indexes for common queries
    __table_args__ = (
        Index('idx_origin_dest', 'origin_airport', 'destination_region'),
        Index('idx_deal_price', 'deal_price'),
        Index('idx_points', 'points_required', 'points_program'),
        Index('idx_status_expiry', 'status', 'expires_at'),
    )


class DealAlert(Base, IDMixin, TimestampMixin):
    """Track when deals matched user criteria and alerts were sent"""
    __tablename__ = "deal_alerts"

    # Deal relationship (nullable because deal might be deleted)
    deal_id = Column(Integer, nullable=True, index=True)

    # Alert Information
    alert_type = Column(String(50), nullable=False)  # threshold_met, custom_criteria, keyword_match
    threshold_name = Column(String(100))  # "Asia under 60K miles", "Europe under $700"

    # Deal snapshot (in case deal is deleted)
    deal_snapshot = Column(JSON, nullable=False)
    # Stores key deal info: title, price, route, dates, etc.

    # Notification Details
    notification_method = Column(String(50), nullable=False)  # email, sms, both
    sent_to_email = Column(String(255))
    sent_to_sms = Column(String(20))

    # Status
    status = Column(String(20), default="sent")  # sent, failed, dismissed, acted_upon
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    acted_upon_at = Column(DateTime)

    # User Actions
    user_action = Column(String(50))  # booked, saved, dismissed, shared
    notes = Column(Text)

    def __repr__(self):
        return f"<DealAlert {self.threshold_name} - {self.status}>"
