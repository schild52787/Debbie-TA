#!/bin/bash

# Google Cloud Platform Deployment Script
# This script deploys Debbie's Travel Agent Assistant to GCP

set -e  # Exit on error

echo "======================================"
echo "Deploying to Google Cloud Platform"
echo "======================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI is installed"
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Project: $PROJECT_ID"
echo ""

# Confirm deployment
read -p "Deploy to project '$PROJECT_ID'? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

echo ""
echo "🔨 Building backend container..."
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/debbie-ta-backend -f Dockerfile.cloudrun .
cd ..

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"
echo ""

# Check if service exists
SERVICE_EXISTS=$(gcloud run services list --platform managed --region us-central1 --format="value(metadata.name)" | grep -c "^debbie-ta-web$" || true)

if [ "$SERVICE_EXISTS" -eq "0" ]; then
    echo "🆕 First deployment - creating service..."
    echo ""
    echo "⚠️  IMPORTANT: You need to configure these manually:"
    echo "   1. Cloud SQL connection"
    echo "   2. Redis connection"
    echo "   3. Environment variables and secrets"
    echo ""
    echo "See GCP_DEPLOYMENT.md for full setup instructions"
    echo ""
    read -p "Press Enter to continue with basic deployment..."

    gcloud run deploy debbie-ta-web \
      --image gcr.io/$PROJECT_ID/debbie-ta-backend \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --memory 512Mi \
      --cpu 1 \
      --timeout 300 \
      --max-instances 10 \
      --set-env-vars PYTHONPATH=/app,PYTHONUNBUFFERED=1
else
    echo "♻️  Updating existing service..."
    gcloud run deploy debbie-ta-web \
      --image gcr.io/$PROJECT_ID/debbie-ta-backend \
      --platform managed \
      --region us-central1
fi

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed"
    exit 1
fi

echo ""
echo "✅ Deployment successful!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe debbie-ta-web \
  --platform managed \
  --region us-central1 \
  --format="value(status.url)")

echo "======================================"
echo "🎉 Deployment Complete!"
echo "======================================"
echo ""
echo "Backend URL: $SERVICE_URL"
echo "API Docs: $SERVICE_URL/docs"
echo "Health Check: $SERVICE_URL/health"
echo ""
echo "Test it:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "Next steps:"
echo "1. Configure Cloud SQL and Redis (see GCP_DEPLOYMENT.md)"
echo "2. Set up environment variables and secrets"
echo "3. Deploy worker and beat services"
echo "4. Update frontend with backend URL"
echo "5. Deploy frontend to Netlify"
echo ""
