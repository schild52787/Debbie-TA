# Debbie's Travel Agent Assistant - Setup Guide

Complete step-by-step guide to get the application running.

## Prerequisites

Before starting, make sure you have:

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or use Docker)
- Redis (or use Docker)
- Docker & Docker Compose (recommended)

## Quick Start with Docker (Recommended)

This is the easiest way to get started. Everything will run in containers.

### 1. Clone and Setup Environment

```bash
cd /path/to/Debbie-TA
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```bash
# Required for basic functionality
DATABASE_URL=postgresql://debbie_ta:password@db:5432/debbie_ta
REDIS_URL=redis://redis:6379/0

# Email alerts (Gmail)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# SMS alerts (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+15551234567

# Alert recipients
ALERT_EMAIL=your_mom@email.com
ALERT_SMS=+15551234567

# API Keys (optional but recommended)
OPENAI_API_KEY=sk-...
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- FastAPI backend (port 8000)
- Celery worker (background tasks)
- Celery beat (scheduler)
- Flower (Celery monitoring - port 5555)
- React frontend (port 3000)

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Or create tables directly
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Task Monitor)**: http://localhost:5555

## Manual Setup (Without Docker)

If you prefer to run services locally without Docker:

### 1. Setup PostgreSQL

```bash
# Create database
createdb debbie_ta

# Or using psql
psql -U postgres
CREATE DATABASE debbie_ta;
CREATE USER debbie_ta WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE debbie_ta TO debbie_ta;
```

### 2. Setup Redis

```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Or (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your settings

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 4. Setup Celery (Separate Terminals)

```bash
# Terminal 1: Celery Worker
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 2: Celery Beat (Scheduler)
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app beat --loglevel=info

# Terminal 3 (Optional): Flower Monitoring
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app flower --port=5555
```

### 5. Setup Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at http://localhost:3000

## API Keys & Credentials Setup

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and add to `.env`:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
6. Run authentication flow (first time only):
   ```bash
   python backend/scripts/gmail_auth.py
   ```

### Twilio SMS Setup

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get a phone number
3. Find your Account SID and Auth Token
4. Add to `.env`:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

### Reddit API (for dispute research)

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create an app (script type)
3. Add to `.env`:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`

### OpenAI API (for email parsing)

1. Sign up at [OpenAI](https://platform.openai.com/)
2. Create API key
3. Add to `.env`:
   - `OPENAI_API_KEY`

## Configuration

### Setting Up Deal Alerts

The system automatically checks for deals every 12 hours. Configure thresholds in the Settings page or directly in `.env`:

```bash
# Asia
ASIA_MILES_THRESHOLD=60000
ASIA_CASH_THRESHOLD=100000  # $1000 in cents

# Europe
EUROPE_MILES_THRESHOLD=30000
EUROPE_CASH_THRESHOLD=70000  # $700 in cents
```

### Adding Clients

Currently done via API. Example:

```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+15551234567",
    "travel_preferences": {
      "preferred_airlines": ["Delta"],
      "seat_preference": "aisle"
    }
  }'
```

## Testing

### Test Deal Alert

```bash
# Via Docker
docker-compose exec backend python -c "from app.tasks.notification_tasks import send_test_alert; send_test_alert.delay()"

# Or directly
cd backend
python -c "from app.tasks.notification_tasks import send_test_alert; send_test_alert()"
```

### Test RSS Feed Parsing

```bash
docker-compose exec backend python -c "from app.tasks.deal_tasks import parse_rss_feeds; parse_rss_feeds()"
```

### Test Email Scanning

```bash
docker-compose exec backend python -c "from app.tasks.email_tasks import scan_dispute_emails; scan_dispute_emails()"
```

## Monitoring

### View Celery Tasks

Access Flower at http://localhost:5555 to see:
- Active tasks
- Task history
- Worker status
- Task rates

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Connect to database directly
docker-compose exec db psql -U debbie_ta
```

### Celery Not Processing Tasks

```bash
# Check worker status
docker-compose logs celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Gmail Authentication

If Gmail authentication fails:
1. Ensure OAuth credentials are correct
2. Make sure Gmail API is enabled in Google Cloud Console
3. Check that redirect URIs are configured
4. Run the authentication script again

### Twilio SMS Not Sending

1. Verify Twilio credentials
2. Check phone number format (+1XXXXXXXXXX)
3. Ensure Twilio account has sufficient balance
4. Check Twilio console for error messages

## Production Deployment

For production deployment to cloud platforms:

### Environment Variables

Set these in your cloud platform:
- All API keys and credentials
- `DEBUG=False`
- `ENVIRONMENT=production`
- Secure `SECRET_KEY`

### Database

Use a managed PostgreSQL service:
- AWS RDS
- Heroku Postgres
- Google Cloud SQL

### Redis

Use a managed Redis service:
- AWS ElastiCache
- Redis Cloud
- Heroku Redis

### Application Hosting

Options:
- **Heroku**: Easy deployment with Procfile
- **AWS ECS/Fargate**: Container-based deployment
- **Google Cloud Run**: Serverless containers
- **DigitalOcean App Platform**: Simple deployment

## Next Steps

1. ✅ Configure all API credentials
2. ✅ Add your mom's email and phone for alerts
3. ✅ Add initial clients via API
4. ✅ Test deal alerts
5. ✅ Verify email scanning works
6. ✅ Customize deal thresholds in Settings

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- View API docs: http://localhost:8000/docs
- Monitor tasks: http://localhost:5555

Enjoy your automated travel agent assistant!
