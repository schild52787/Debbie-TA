# Quick Start: Deploy to Google Cloud Platform

Fast deployment guide - get your app running on GCP in 15 minutes.

## Prerequisites

1. Google Cloud account (sign up gets $300 free credit)
2. Credit card (required even for free tier)

## Step 1: Install gcloud CLI (2 minutes)

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

**Initialize:**
```bash
gcloud init
# Follow prompts to login and select/create project
```

## Step 2: Setup Project (2 minutes)

```bash
# Set your project
export PROJECT_ID="debbie-ta-$(whoami)"
gcloud config set project $PROJECT_ID

# Enable required services (this takes ~1 minute)
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com
```

## Step 3: Create Database & Redis (5 minutes)

```bash
# PostgreSQL (this takes ~5 minutes, runs in background)
gcloud sql instances create debbie-ta-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=ChangeMe123! &

# Redis (takes ~3 minutes, runs in background)
gcloud redis instances create debbie-ta-redis \
  --size=1 \
  --region=us-central1 &

# Wait for both to complete
wait

echo "Databases ready!"
```

## Step 4: Deploy Backend (3 minutes)

```bash
# From your project directory
cd /path/to/Debbie-TA

# Run deployment script
./deploy-gcp.sh
```

The script will:
- Build your container
- Deploy to Cloud Run
- Give you your backend URL

## Step 5: Get Your URLs

```bash
# Get your backend URL
gcloud run services describe debbie-ta-web \
  --platform managed \
  --region us-central1 \
  --format="value(status.url)"

# Save this URL - you'll need it for frontend!
```

## Step 6: Configure Environment (3 minutes)

```bash
# Get connection details
SQL_CONN=$(gcloud sql instances describe debbie-ta-db --format="value(connectionName)")
REDIS_HOST=$(gcloud redis instances describe debbie-ta-redis --region=us-central1 --format="value(host)")

# Update service with environment variables
gcloud run services update debbie-ta-web \
  --region us-central1 \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars DATABASE_URL="postgresql://postgres:ChangeMe123!@/postgres?host=/cloudsql/$SQL_CONN" \
  --set-env-vars REDIS_URL="redis://$REDIS_HOST:6379/0" \
  --set-env-vars PYTHONPATH=/app \
  --set-env-vars DEBUG=False
```

## Step 7: Test It

```bash
# Get your URL
URL=$(gcloud run services describe debbie-ta-web --region us-central1 --format="value(status.url)")

# Test health endpoint
curl $URL/health

# Should return: {"status":"healthy",...}

# View API docs in browser
open $URL/docs  # Mac
# or visit: https://your-url.run.app/docs
```

## Step 8: Deploy Frontend to Netlify

```bash
# Update frontend config
echo "REACT_APP_API_URL=$URL" > frontend/.env.production

# Update netlify.toml (replace YOUR_URL with actual URL)
# Then push to GitHub

git add .
git commit -m "Configure for GCP deployment"
git push

# Deploy to Netlify (see NETLIFY_DEPLOYMENT.md)
```

## All Done! 🎉

You now have:
- ✅ Backend running on Cloud Run
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Public HTTPS URL

**Your backend URL:** Check with `gcloud run services describe debbie-ta-web --region us-central1 --format="value(status.url)"`

## Next Steps

### Add API Credentials

```bash
# Create secrets
echo -n "your_gmail_client_id" | gcloud secrets create gmail-client-id --data-file=-
echo -n "your_gmail_client_secret" | gcloud secrets create gmail-client-secret --data-file=-
echo -n "your_twilio_sid" | gcloud secrets create twilio-sid --data-file=-
echo -n "your_twilio_token" | gcloud secrets create twilio-token --data-file=-

# Attach to service
gcloud run services update debbie-ta-web \
  --region us-central1 \
  --set-secrets GMAIL_CLIENT_ID=gmail-client-id:latest \
  --set-secrets GMAIL_CLIENT_SECRET=gmail-client-secret:latest \
  --set-secrets TWILIO_ACCOUNT_SID=twilio-sid:latest \
  --set-secrets TWILIO_AUTH_TOKEN=twilio-token:latest
```

### Deploy Worker & Beat

```bash
# Deploy worker
gcloud run deploy debbie-ta-worker \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars DATABASE_URL="..." \
  --set-env-vars REDIS_URL="..." \
  --command "./start-worker.sh" \
  --no-cpu-throttling

# Deploy beat
gcloud run deploy debbie-ta-beat \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances $SQL_CONN \
  --set-env-vars DATABASE_URL="..." \
  --set-env-vars REDIS_URL="..." \
  --command "./start-beat.sh" \
  --no-cpu-throttling
```

## Common Issues

### "Permission denied" errors
```bash
# Make sure you're authenticated
gcloud auth login
```

### "Billing not enabled"
- Go to console.cloud.google.com
- Enable billing for your project
- Even free tier requires billing setup

### Service won't start
```bash
# Check logs
gcloud run services logs read debbie-ta-web --limit 50
```

### Can't connect to database
- Make sure `--add-cloudsql-instances` is set
- Check DATABASE_URL format

## Costs

With $300 free credit:
- **First year: FREE** (covered by credit)
- **After credit**: ~$40-50/month
  - Cloud Run: $0-5 (generous free tier)
  - Cloud SQL: $10-15
  - Redis: $30

## View Everything

**Cloud Console:** https://console.cloud.google.com/run

- View services
- Check logs
- Monitor metrics
- Manage databases

## Update Your App

```bash
# Make changes to code
# Then redeploy
./deploy-gcp.sh
```

## Delete Everything

```bash
# If you want to start over
gcloud run services delete debbie-ta-web --region us-central1
gcloud sql instances delete debbie-ta-db
gcloud redis instances delete debbie-ta-redis --region us-central1
```

## Need Help?

- Full guide: `GCP_DEPLOYMENT.md`
- GCP docs: https://cloud.google.com/run/docs
- Support: Open GitHub issue

That's it! Your app is live on Google Cloud! 🚀
