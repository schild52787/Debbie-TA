# Google Cloud Platform Deployment

Deploy to Google Cloud Run - serverless, scalable, and reliable.

## Architecture

- **Backend (Web)**: Cloud Run
- **Celery Worker**: Cloud Run (separate service)
- **Celery Beat**: Cloud Run (separate service)
- **Database**: Cloud SQL (PostgreSQL)
- **Cache**: Memorystore (Redis)

## Cost Estimate

- Cloud Run: ~$0-5/month (generous free tier)
- Cloud SQL: ~$10-15/month (db-f1-micro)
- Memorystore: ~$30/month (basic Redis)
- **Total: ~$40-50/month**

## Prerequisites

1. Google Cloud account (free trial includes $300 credit)
2. `gcloud` CLI installed
3. Billing enabled

## Step 1: Install gcloud CLI

### Mac/Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### Windows:
Download from: https://cloud.google.com/sdk/docs/install

### Initialize:
```bash
gcloud init
gcloud auth login
```

## Step 2: Create GCP Project

```bash
# Set your project name
export PROJECT_ID="debbie-ta-prod"

# Create project
gcloud projects create $PROJECT_ID --name="Debbie TA"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required - use console: console.cloud.google.com)
# Go to Billing and link your billing account

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  vpcaccess.googleapis.com
```

## Step 3: Create Cloud SQL (PostgreSQL)

```bash
# Create PostgreSQL instance (takes 5-10 minutes)
gcloud sql instances create debbie-ta-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=CHANGE_THIS_PASSWORD

# Create database
gcloud sql databases create debbie_ta --instance=debbie-ta-db

# Create user
gcloud sql users create debbie_user \
  --instance=debbie-ta-db \
  --password=CHANGE_THIS_PASSWORD

# Get connection name (save this!)
gcloud sql instances describe debbie-ta-db --format="value(connectionName)"
# Output: PROJECT_ID:us-central1:debbie-ta-db
```

## Step 4: Create Memorystore (Redis)

```bash
# Create Redis instance (takes 3-5 minutes)
gcloud redis instances create debbie-ta-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# Get Redis host (save this!)
gcloud redis instances describe debbie-ta-redis \
  --region=us-central1 \
  --format="value(host)"

# Get Redis port
gcloud redis instances describe debbie-ta-redis \
  --region=us-central1 \
  --format="value(port)"
```

## Step 5: Store Secrets in Secret Manager

```bash
# Create secrets for sensitive data
echo -n "your_gmail_client_id" | gcloud secrets create gmail-client-id --data-file=-
echo -n "your_gmail_client_secret" | gcloud secrets create gmail-client-secret --data-file=-
echo -n "your_twilio_sid" | gcloud secrets create twilio-sid --data-file=-
echo -n "your_twilio_token" | gcloud secrets create twilio-token --data-file=-
echo -n "your_openai_key" | gcloud secrets create openai-key --data-file=-
```

## Step 6: Build and Deploy Backend (Web Service)

```bash
# From project root
cd /path/to/Debbie-TA

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/debbie-ta-backend ./backend

# Deploy to Cloud Run
gcloud run deploy debbie-ta-web \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances PROJECT_ID:us-central1:debbie-ta-db \
  --set-env-vars PYTHONPATH=/app,PYTHONUNBUFFERED=1 \
  --set-env-vars DATABASE_URL="postgresql://debbie_user:PASSWORD@/debbie_ta?host=/cloudsql/PROJECT_ID:us-central1:debbie-ta-db" \
  --set-env-vars REDIS_URL="redis://REDIS_HOST:REDIS_PORT/0" \
  --set-env-vars DEBUG=False \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets GMAIL_CLIENT_ID=gmail-client-id:latest \
  --set-secrets GMAIL_CLIENT_SECRET=gmail-client-secret:latest \
  --set-secrets TWILIO_ACCOUNT_SID=twilio-sid:latest \
  --set-secrets TWILIO_AUTH_TOKEN=twilio-token:latest \
  --set-secrets OPENAI_API_KEY=openai-key:latest \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

## Step 7: Deploy Celery Worker

```bash
# Build same image (already done in step 6)

# Deploy worker
gcloud run deploy debbie-ta-worker \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances PROJECT_ID:us-central1:debbie-ta-db \
  --command "./start-worker.sh" \
  --set-env-vars PYTHONPATH=/app,PYTHONUNBUFFERED=1 \
  --set-env-vars DATABASE_URL="postgresql://debbie_user:PASSWORD@/debbie_ta?host=/cloudsql/PROJECT_ID:us-central1:debbie-ta-db" \
  --set-env-vars REDIS_URL="redis://REDIS_HOST:REDIS_PORT/0" \
  --set-secrets GMAIL_CLIENT_ID=gmail-client-id:latest \
  --set-secrets GMAIL_CLIENT_SECRET=gmail-client-secret:latest \
  --set-secrets TWILIO_ACCOUNT_SID=twilio-sid:latest \
  --set-secrets TWILIO_AUTH_TOKEN=twilio-token:latest \
  --memory 512Mi \
  --cpu 1 \
  --no-cpu-throttling
```

## Step 8: Deploy Celery Beat (Scheduler)

```bash
gcloud run deploy debbie-ta-beat \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --add-cloudsql-instances PROJECT_ID:us-central1:debbie-ta-db \
  --command "./start-beat.sh" \
  --set-env-vars PYTHONPATH=/app,PYTHONUNBUFFERED=1 \
  --set-env-vars DATABASE_URL="postgresql://debbie_user:PASSWORD@/debbie_ta?host=/cloudsql/PROJECT_ID:us-central1:debbie-ta-db" \
  --set-env-vars REDIS_URL="redis://REDIS_HOST:REDIS_PORT/0" \
  --memory 256Mi \
  --cpu 1 \
  --no-cpu-throttling
```

## Step 9: Initialize Database

```bash
# Get service URL
gcloud run services describe debbie-ta-web \
  --platform managed \
  --region us-central1 \
  --format="value(status.url)"

# Test health endpoint
curl https://debbie-ta-web-XXXXX.run.app/health

# Initialize database using Cloud Run Jobs
gcloud run jobs create debbie-ta-init-db \
  --image gcr.io/$PROJECT_ID/debbie-ta-backend \
  --region us-central1 \
  --add-cloudsql-instances PROJECT_ID:us-central1:debbie-ta-db \
  --set-env-vars DATABASE_URL="..." \
  --command "python" \
  --args "-c,from app.database import init_db; init_db()"

# Execute the job
gcloud run jobs execute debbie-ta-init-db --region us-central1
```

## Step 10: Deploy Frontend to Netlify

```bash
# Update frontend/.env.production with Cloud Run URL
echo "REACT_APP_API_URL=https://debbie-ta-web-XXXXX.run.app" > frontend/.env.production

# Update netlify.toml redirect
# Edit line with: to = "https://debbie-ta-web-XXXXX.run.app/api/:splat"

# Commit and push
git add .
git commit -m "Update API URL for GCP deployment"
git push

# Deploy to Netlify (see NETLIFY_DEPLOYMENT.md)
```

## Useful Commands

### View Logs
```bash
# Web service logs
gcloud run services logs read debbie-ta-web --limit 50

# Worker logs
gcloud run services logs read debbie-ta-worker --limit 50

# Tail logs (real-time)
gcloud run services logs tail debbie-ta-web
```

### Update Service
```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/debbie-ta-backend ./backend
gcloud run services update debbie-ta-web --image gcr.io/$PROJECT_ID/debbie-ta-backend
```

### View Service Details
```bash
gcloud run services describe debbie-ta-web --region us-central1
```

### Scale Service
```bash
# Increase max instances
gcloud run services update debbie-ta-web \
  --max-instances 20 \
  --region us-central1
```

### Delete Everything (Cleanup)
```bash
# Delete Cloud Run services
gcloud run services delete debbie-ta-web --region us-central1
gcloud run services delete debbie-ta-worker --region us-central1
gcloud run services delete debbie-ta-beat --region us-central1

# Delete database
gcloud sql instances delete debbie-ta-db

# Delete Redis
gcloud redis instances delete debbie-ta-redis --region us-central1

# Delete secrets
gcloud secrets delete gmail-client-id
gcloud secrets delete gmail-client-secret
# etc...
```

## Monitoring

### Cloud Console
Go to: https://console.cloud.google.com/run

- View all services
- Monitor metrics (requests, latency, errors)
- View logs
- Set up alerts

### Set Up Alerts
```bash
# Create alert for errors
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud Run Errors" \
  --condition-display-name="Error rate" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s
```

## Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service debbie-ta-web \
  --domain api.yourdomain.com \
  --region us-central1

# Follow instructions to update DNS
```

## CI/CD with GitHub Actions

Create `.github/workflows/deploy-gcp.yml`:

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Build
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/debbie-ta-backend ./backend

      - name: Deploy
        run: |
          gcloud run deploy debbie-ta-web \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/debbie-ta-backend \
            --region us-central1 \
            --platform managed
```

## Troubleshooting

### Service won't start
- Check logs: `gcloud run services logs read debbie-ta-web --limit 100`
- Verify DATABASE_URL is correct
- Check Redis connection

### Can't connect to Cloud SQL
- Verify `--add-cloudsql-instances` is set
- Check DATABASE_URL format
- Ensure Cloud SQL Admin API is enabled

### Worker not processing tasks
- Check worker logs
- Verify Redis connection
- Ensure `--no-cpu-throttling` is set

### High costs
- Reduce max-instances
- Use smaller machine types
- Consider Cloud SQL shared-core instance

## Advantages of GCP

✅ More reliable than Railway
✅ Better logging and monitoring
✅ Cloud SQL has automatic backups
✅ Serverless (only pay for usage)
✅ Easy to scale
✅ Good documentation
✅ $300 free credit for new users

## Summary

After deployment, you'll have:
- ✅ Web service: `https://debbie-ta-web-XXX.run.app`
- ✅ Managed PostgreSQL database
- ✅ Managed Redis cache
- ✅ Celery worker and beat running
- ✅ Auto-scaling based on traffic
- ✅ Built-in monitoring and logging

Total cost: ~$40-50/month (or free during trial period)
