"""User preferences and alert threshold models"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, JSON
from .base import Base, TimestampMixin, IDMixin


class UserPreferences(Base, IDMixin, TimestampMixin):
    """User preferences for deal alerts and notifications"""
    __tablename__ = "user_preferences"

    # User identification (for future multi-user support)
    user_name = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))

    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(20), default="immediate")  # immediate, daily, weekly

    # Quiet Hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))  # "08:00"

    # Default Search Preferences
    default_origin_airport = Column(String(10), default="MSP")
    preferred_travel_class = Column(JSON, default=list)  # ["business", "premium_economy"]
    preferred_airlines = Column(JSON, default=list)
    preferred_hotel_chains = Column(JSON, default=list)
    preferred_regions = Column(JSON, default=list)  # ["Europe", "Asia", "South America"]

    # Loyalty Program Numbers
    loyalty_programs = Column(JSON, default=dict)
    # Example: {
    #   "delta_skymiles": "1234567890",
    #   "marriott_bonvoy": "0987654321",
    #   "hyatt": "1122334455",
    #   "chase_ur": "6677889900",
    #   "amex_mr": "5544332211"
    # }

    # Travel Preferences
    flexible_dates = Column(Boolean, default=True)
    max_layovers = Column(Integer, default=1)
    nonstop_only = Column(Boolean, default=False)
    minimum_stay_days = Column(Integer)
    maximum_stay_days = Column(Integer)

    # Advanced Preferences
    preferences_json = Column(JSON, default=dict)
    # Store any additional custom preferences

    # Active Status
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<UserPreferences {self.user_name}>"


class AlertThreshold(Base, IDMixin, TimestampMixin):
    """Configurable alert thresholds for travel deals"""
    __tablename__ = "alert_thresholds"

    # Threshold Identification
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Active Status
    is_active = Column(Boolean, default=True)

    # Geographic Criteria
    origin_airports = Column(JSON, default=list)  # ["MSP"] or ["MSP", "ORD"]
    destination_regions = Column(JSON, default=list)  # ["Europe", "Asia"]
    destination_countries = Column(JSON, default=list)  # ["France", "Japan"]
    destination_cities = Column(JSON, default=list)  # ["Paris", "Tokyo"]

    # Provider Criteria
    airlines = Column(JSON, default=list)
    hotel_chains = Column(JSON, default=list)
    cruise_lines = Column(JSON, default=list)

    # Travel Class
    travel_classes = Column(JSON, default=list)  # ["business", "first"]

    # Price Thresholds - Cash
    max_cash_price = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")

    # Price Thresholds - Miles/Points
    max_miles_price = Column(Integer)
    points_programs = Column(JSON, default=list)  # ["SkyMiles", "Ultimate Rewards"]
    min_cents_per_point = Column(Numeric(5, 2))  # Minimum CPP value to trigger alert

    # Date Constraints
    earliest_travel_date = Column(String(10))  # "2024-06-01" (flexible, not specific year)
    latest_travel_date = Column(String(10))  # "2024-09-30"
    blackout_dates = Column(JSON, default=list)

    # Flexibility
    allow_layovers = Column(Boolean, default=True)
    max_layovers = Column(Integer, default=1)
    nonstop_only = Column(Boolean, default=False)

    # Minimum Deal Quality
    min_quality_score = Column(Numeric(3, 2))  # Only alert if quality score >= this
    exceptional_only = Column(Boolean, default=False)

    # Advanced Criteria
    custom_criteria = Column(JSON, default=dict)
    # Example: {
    #   "min_discount_percentage": 40,
    #   "max_booking_advance_days": 90,
    #   "refundable_only": true,
    #   "direct_flights_only": false
    # }

    # Priority
    priority = Column(Integer, default=5)  # 1-10, higher = more important

    # Notification Override
    override_quiet_hours = Column(Boolean, default=False)  # Alert even during quiet hours

    def __repr__(self):
        return f"<AlertThreshold {self.name} (Active: {self.is_active})>"
