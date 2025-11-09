# Debbie's Travel Agent Assistant

A comprehensive travel agent management system designed for organizing client itineraries, filing dispute claims, tracking travel deals, and automating research.

## Features

### 1. Client & Itinerary Management
- Organize client travel itineraries
- Track flights, hotels, cruises, and activities
- Store confirmation numbers and traveler details

### 2. Dispute Claims System
- Automated email parsing from Gmail
- Legal research integration (DOT, EU261, airline contracts)
- Social media scraping for dispute resolution strategies
- Support for: flight cancellations/delays, lost luggage, hotel issues, refunds

### 3. Travel Deal Aggregation
- RSS feed monitoring from ThePointsGuy, ThriftyTravel, and other top travel sites
- Automated deal discovery every 12 hours
- Focus on deals from MSP airport

### 4. Smart Deal Alerts
- Configurable thresholds:
  - Asia: <60,000 MQDs or <$1,000 cash
  - Europe: <30,000 MQDs or <$700 cash
- Email and SMS notifications
- Support for Delta, Marriott, Hyatt, Chase, and Amex points

### 5. Travel Partners Covered
- Airlines: Delta (primary), major carriers
- Hotels: Marriott, Hyatt, Melia, mainstream chains
- Cruises: Viking, luxury cruise lines
- Vacation Packages: Apple Vacations

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- SQLAlchemy + PostgreSQL
- Celery + Redis (task queue)
- Gmail API, Twilio SMS

**Frontend:**
- React 18
- Material-UI
- React Router
- Axios

**Infrastructure:**
- Docker & Docker Compose
- Cloud-ready (AWS/Heroku/GCP)

## Project Structure

```
debbie-ta/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Celery background tasks
│   │   └── utils/        # Utilities
│   ├── config/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
└── docker/
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis
- Docker (optional, recommended)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/debbie_ta

# Gmail API
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# Twilio SMS
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Alert Recipients
ALERT_EMAIL=your_mom@email.com
ALERT_SMS=+1234567890

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (for flight/hotel searches)
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret
```

### Quick Start with Docker

```bash
# Build and start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat (scheduled tasks, separate terminal)
celery -A app.tasks.celery_app beat --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## Usage

### For Your Mom (Simple Interface)
1. Navigate to the dashboard
2. View client itineraries
3. Check latest deals and alerts
4. File dispute claims with one click

### For You (Advanced Features)
1. Access admin panel via `/admin`
2. Configure deal thresholds
3. Manage RSS feeds
4. Customize alert rules
5. View detailed analytics

## Key Workflows

### Filing a Dispute
1. System scans Gmail for client emails
2. AI extracts relevant details (flight numbers, dates, issues)
3. Fetches current airline policies and legal regulations
4. Scrapes social media for successful resolution strategies
5. Generates dispute claim document
6. Sends to appropriate airline/hotel with tracking

### Deal Monitoring
1. Every 12 hours, Celery tasks run
2. RSS feeds are parsed for new deals
3. Flight APIs are queried for MSP deals
4. Deals are filtered by thresholds
5. Matching deals trigger email/SMS alerts

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

See `DEPLOYMENT.md` for detailed cloud deployment instructions.

## Support

For issues or questions, contact: [Your Email]

## License

MIT
