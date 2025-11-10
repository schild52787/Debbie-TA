# Deploy to Google Cloud Platform - Complete Guide

This project is configured for full deployment to Google Cloud Platform (GCP).

## 🏗️ Architecture Overview

**Backend & Infrastructure (all on GCP):**
- **Web Service**: Cloud Run (FastAPI backend)
- **Celery Worker**: Cloud Run (background tasks)
- **Celery Beat**: Cloud Run (task scheduler)
- **Database**: Cloud SQL PostgreSQL
- **Cache**: Memorystore Redis

**Frontend:**
- **Hosting**: Netlify (free tier)
- **CDN**: Netlify global CDN

## 💰 Cost Estimate

- **First Year**: FREE with $300 GCP credit
- **After Credit**: ~$40-50/month
  - Cloud Run: $0-5/month (generous free tier)
  - Cloud SQL: $10-15/month
  - Memorystore Redis: $30/month
- **Netlify**: FREE (frontend hosting)

**Total**: ~$40-50/month after free credit expires

## 🚀 Quick Deployment (15 minutes)

### Prerequisites
1. Google Cloud account (get $300 free credit)
2. Install gcloud CLI: `curl https://sdk.cloud.google.com | bash`
3. GitHub account (for Netlify)

### Step 1: Setup GCP Project (2 min)

```bash
# Login and initialize
gcloud init
gcloud auth login

# Set project (use existing or create new)
export PROJECT_ID="debbie-ta-prod"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com
```

### Step 2: Create Database & Redis (5 min)

```bash
# Create PostgreSQL (runs in background, ~5 min)
gcloud sql instances create debbie-ta-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=ChangeMe123! &

# Create Redis (runs in background, ~3 min)
gcloud redis instances create debbie-ta-redis \
  --size=1 \
  --region=us-central1 &

# Wait for both to complete
wait
```

### Step 3: Deploy Backend (5 min)

```bash
# Run the automated deployment script
./deploy-gcp-complete.sh
```

This script will:
- Build your Docker container
- Deploy to Cloud Run
- Initialize the database
- Give you your backend URL

### Step 4: Get Your Backend URL

```bash
# Get the URL (save this for frontend config!)
gcloud run services describe debbie-ta-web \
  --region us-central1 \
  --format="value(status.url)"

# Example: https://debbie-ta-web-abc123-uc.a.run.app
```

### Step 5: Configure Frontend (2 min)

```bash
# Update frontend config with your actual Cloud Run URL
BACKEND_URL="https://debbie-ta-web-YOUR_ID.run.app"

# Update .env.production
echo "REACT_APP_API_URL=$BACKEND_URL" > frontend/.env.production
echo "REACT_APP_ENVIRONMENT=production" >> frontend/.env.production

# Update netlify.toml redirect (use sed or manual edit)
sed -i "s|https://your-backend-url.run.app|$BACKEND_URL|g" netlify.toml
```

### Step 6: Deploy Frontend to Netlify (1 min)

```bash
# Commit frontend config changes
git add frontend/.env.production netlify.toml
git commit -m "Configure frontend for GCP backend"
git push

# Deploy to Netlify (via web UI)
# 1. Go to netlify.com and login with GitHub
# 2. "Add new site" → "Import existing project"
# 3. Select Debbie-TA repository
# 4. Settings auto-detected from netlify.toml
# 5. Click "Deploy"
```

## ✅ Verify Deployment

```bash
# Test backend health
curl https://your-backend-url.run.app/health

# Should return: {"status":"healthy","service":"Debbie's Travel Agent Assistant"}

# View API docs
open https://your-backend-url.run.app/docs

# Test frontend
# Visit your Netlify URL (e.g., debbie-ta.netlify.app)
```

## 🔐 Add API Credentials

After initial deployment, add your API keys:

```bash
# Create secrets in GCP Secret Manager
echo -n "your_gmail_client_id" | gcloud secrets create gmail-client-id --data-file=-
echo -n "your_gmail_secret" | gcloud secrets create gmail-client-secret --data-file=-
echo -n "your_twilio_sid" | gcloud secrets create twilio-sid --data-file=-
echo -n "your_twilio_token" | gcloud secrets create twilio-token --data-file=-
echo -n "your_openai_key" | gcloud secrets create openai-key --data-file=-

# Update Cloud Run service with secrets
gcloud run services update debbie-ta-web \
  --region us-central1 \
  --set-secrets GMAIL_CLIENT_ID=gmail-client-id:latest \
  --set-secrets GMAIL_CLIENT_SECRET=gmail-client-secret:latest \
  --set-secrets TWILIO_ACCOUNT_SID=twilio-sid:latest \
  --set-secrets TWILIO_AUTH_TOKEN=twilio-token:latest \
  --set-secrets OPENAI_API_KEY=openai-key:latest
```

## 🔄 Deploy Celery Worker & Beat

For full functionality (background tasks), deploy worker and beat:

```bash
# Get connection strings
SQL_CONN=$(gcloud sql instances describe debbie-ta-db --format="value(connectionName)")
REDIS_HOST=$(gcloud redis instances describe debbie-ta-redis --region=us-central1 --format="value(host)")

# Deploy Celery Worker
gcloud run deploy debbie-ta-worker \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars DATABASE_URL="postgresql://postgres:ChangeMe123!@/postgres?host=/cloudsql/$SQL_CONN" \
  --set-env-vars REDIS_URL="redis://$REDIS_HOST:6379/0" \
  --command "./start-worker.sh" \
  --memory 512Mi \
  --no-cpu-throttling

# Deploy Celery Beat (scheduler)
gcloud run deploy debbie-ta-beat \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars DATABASE_URL="postgresql://postgres:ChangeMe123!@/postgres?host=/cloudsql/$SQL_CONN" \
  --set-env-vars REDIS_URL="redis://$REDIS_HOST:6379/0" \
  --command "./start-beat.sh" \
  --memory 256Mi \
  --no-cpu-throttling
```

## 📊 Monitor Your Deployment

**GCP Console**: https://console.cloud.google.com/run

View:
- Service metrics (requests, latency, errors)
- Real-time logs
- Resource usage
- Cost breakdown

**View Logs**:
```bash
# Web service logs
gcloud run services logs read debbie-ta-web --limit 50

# Worker logs
gcloud run services logs read debbie-ta-worker --limit 50

# Tail logs (real-time)
gcloud run services logs tail debbie-ta-web
```

## 🔄 Update Your App

When you make code changes:

```bash
# Make changes to your code
# Then redeploy:

./deploy-gcp-complete.sh

# Or manually:
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/debbie-ta-backend
gcloud run services update debbie-ta-web \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1
```

## 🔧 Troubleshooting

### Service won't start
```bash
# Check logs
gcloud run services logs read debbie-ta-web --limit 100

# Common issues:
# - DATABASE_URL format incorrect
# - Redis host unreachable
# - Missing environment variables
```

### Database connection failed
```bash
# Verify Cloud SQL is running
gcloud sql instances describe debbie-ta-db

# Make sure --add-cloudsql-instances is set
gcloud run services describe debbie-ta-web \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Frontend can't reach backend
```bash
# Check CORS settings in backend/config/settings.py
# Make sure your Netlify URL is in CORS_ORIGINS

# Verify API redirect in netlify.toml
cat netlify.toml | grep "to ="
```

## 📁 File Structure

**GCP Deployment Files:**
```
Debbie-TA/
├── deploy-gcp-complete.sh      # Automated deployment script
├── deploy-gcp.sh               # Simple deployment script
├── GCP_DEPLOYMENT.md           # Detailed GCP guide
├── GCP_QUICKSTART.md          # Quick start guide
├── cloudbuild.yaml            # Cloud Build config
├── backend/
│   └── Dockerfile.cloudrun    # Optimized for Cloud Run
├── start-web.sh               # Web service entrypoint
├── start-worker.sh            # Worker entrypoint
└── start-beat.sh              # Beat scheduler entrypoint
```

**Frontend Deployment:**
```
frontend/
├── .env.production            # GCP backend URL
└── netlify.toml              # Netlify config
```

## 🆘 Need Help?

1. **Detailed Guides**:
   - `GCP_DEPLOYMENT.md` - Step-by-step manual deployment
   - `GCP_QUICKSTART.md` - Quick reference

2. **GCP Documentation**:
   - Cloud Run: https://cloud.google.com/run/docs
   - Cloud SQL: https://cloud.google.com/sql/docs

3. **Support**:
   - Open GitHub issue
   - Check Cloud Run logs
   - GCP Support Console

## 🎉 You're Done!

Your app is now running on Google Cloud Platform:

- ✅ **Backend**: Cloud Run (auto-scaling, serverless)
- ✅ **Frontend**: Netlify (global CDN)
- ✅ **Database**: Managed PostgreSQL
- ✅ **Cache**: Managed Redis
- ✅ **Monitoring**: Built-in metrics and logs
- ✅ **Security**: HTTPS everywhere
- ✅ **Cost**: ~$40-50/month (free for first year with credits)

**Backend URL**: `https://debbie-ta-web-XXXXX.run.app`
**Frontend URL**: `https://debbie-ta.netlify.app`

Enjoy your travel agent assistant! ✈️
