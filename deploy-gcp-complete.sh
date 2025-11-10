#!/bin/bash

# Complete GCP Deployment Script
# This script will deploy everything to Google Cloud Platform

set -e  # Exit on error

echo "======================================"
echo "🚀 Deploying Debbie TA to GCP"
echo "======================================"
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
echo "📦 Project: $PROJECT_ID"
echo ""

# Step 1: Enable services
echo "1️⃣  Enabling required services..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com --quiet
echo "✅ Services enabled"
echo ""

# Step 2: Create Redis (in background)
echo "2️⃣  Creating Redis instance..."
if gcloud redis instances describe debbie-ta-redis --region=us-central1 &>/dev/null; then
    echo "✅ Redis already exists"
else
    gcloud redis instances create debbie-ta-redis \
      --size=1 \
      --region=us-central1 \
      --redis-version=redis_7_0 &
    REDIS_PID=$!
    echo "⏳ Redis creating in background (PID: $REDIS_PID)..."
fi
echo ""

# Step 3: Wait for database (should be running already)
echo "3️⃣  Checking database..."
while ! gcloud sql instances describe debbie-ta-db &>/dev/null; do
    echo "⏳ Waiting for database to be ready..."
    sleep 10
done
echo "✅ Database is ready"
echo ""

# Step 4: Get connection details
echo "4️⃣  Getting connection details..."
SQL_CONN=$(gcloud sql instances describe debbie-ta-db --format="value(connectionName)")
echo "   Database: $SQL_CONN"

# Wait for Redis if it was being created
if [ ! -z "$REDIS_PID" ]; then
    echo "⏳ Waiting for Redis to complete..."
    wait $REDIS_PID || true
fi

REDIS_HOST=$(gcloud redis instances describe debbie-ta-redis --region=us-central1 --format="value(host)" 2>/dev/null || echo "PENDING")
echo "   Redis: $REDIS_HOST"
echo ""

# Step 5: Build container
echo "5️⃣  Building container image..."
cd backend
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/debbie-ta-backend \
  --timeout=20m .
cd ..
echo "✅ Build complete"
echo ""

# Step 6: Deploy to Cloud Run
echo "6️⃣  Deploying to Cloud Run..."

# Wait for Redis host if still pending
while [ "$REDIS_HOST" == "PENDING" ]; do
    echo "⏳ Waiting for Redis host..."
    sleep 10
    REDIS_HOST=$(gcloud redis instances describe debbie-ta-redis --region=us-central1 --format="value(host)" 2>/dev/null || echo "PENDING")
done

gcloud run deploy debbie-ta-web \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars "PYTHONPATH=/app" \
  --set-env-vars "PYTHONUNBUFFERED=1" \
  --set-env-vars "DATABASE_URL=postgresql://postgres:ChangeMe123!@/postgres?host=/cloudsql/$SQL_CONN" \
  --set-env-vars "REDIS_URL=redis://$REDIS_HOST:6379/0" \
  --set-env-vars "DEBUG=False" \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "DEFAULT_AIRPORT=MSP" \
  --set-env-vars "ASIA_MILES_THRESHOLD=60000" \
  --set-env-vars "ASIA_CASH_THRESHOLD=100000" \
  --set-env-vars "EUROPE_MILES_THRESHOLD=30000" \
  --set-env-vars "EUROPE_CASH_THRESHOLD=70000" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --quiet

echo "✅ Deployed to Cloud Run"
echo ""

# Step 7: Get service URL
SERVICE_URL=$(gcloud run services describe debbie-ta-web \
  --platform managed \
  --region us-central1 \
  --format="value(status.url)")

echo "7️⃣  Testing deployment..."
sleep 5  # Give service a moment to start

# Test health endpoint
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo "✅ Service is healthy!"
else
    echo "⚠️  Service might need a moment to start..."
fi
echo ""

# Step 8: Initialize database
echo "8️⃣  Initializing database..."

# Create and run database init job
gcloud run jobs delete debbie-ta-init --region us-central1 --quiet 2>/dev/null || true

gcloud run jobs create debbie-ta-init \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars "DATABASE_URL=postgresql://postgres:ChangeMe123!@/postgres?host=/cloudsql/$SQL_CONN" \
  --set-env-vars "PYTHONPATH=/app" \
  --command "python" \
  --args "-c" \
  --args "from app.database import init_db; init_db()" \
  --quiet

echo "⏳ Running database initialization..."
gcloud run jobs execute debbie-ta-init --region us-central1 --wait --quiet

echo "✅ Database initialized"
echo ""

# Done!
echo "======================================"
echo "🎉 Deployment Complete!"
echo "======================================"
echo ""
echo "Your backend is live at:"
echo "  $SERVICE_URL"
echo ""
echo "Test it:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "API Documentation:"
echo "  $SERVICE_URL/docs"
echo ""
echo "Next steps:"
echo "1. Add API credentials (Gmail, Twilio, etc.)"
echo "2. Deploy worker and beat services"
echo "3. Update frontend with this URL"
echo "4. Deploy frontend to Netlify"
echo ""
echo "See NEXT_STEPS.md for detailed instructions"
echo ""
