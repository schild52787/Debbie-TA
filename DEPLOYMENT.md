# Cloud Deployment Guide

Instructions for deploying Debbie's Travel Agent Assistant to various cloud platforms.

## General Prerequisites

Before deploying to any platform:

1. **Environment Variables**: Prepare all required API keys and credentials
2. **Database**: Set up a PostgreSQL database (managed service recommended)
3. **Redis**: Set up Redis instance for Celery
4. **API Keys**: Have all third-party API keys ready (Gmail, Twilio, etc.)

## Option 1: Heroku Deployment

Heroku is the easiest option for quick deployment.

### Prerequisites

- Heroku account
- Heroku CLI installed

### Steps

1. **Create Heroku App**

```bash
heroku create debbie-ta-app
```

2. **Add Add-ons**

```bash
# PostgreSQL
heroku addons:create heroku-postgresql:mini

# Redis
heroku addons:create heroku-redis:mini
```

3. **Set Environment Variables**

```bash
heroku config:set GMAIL_CLIENT_ID=your_value
heroku config:set GMAIL_CLIENT_SECRET=your_value
heroku config:set TWILIO_ACCOUNT_SID=your_value
heroku config:set TWILIO_AUTH_TOKEN=your_value
heroku config:set TWILIO_PHONE_NUMBER=+15551234567
heroku config:set ALERT_EMAIL=mom@email.com
heroku config:set ALERT_SMS=+15551234567
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set REDDIT_CLIENT_ID=your_value
heroku config:set REDDIT_CLIENT_SECRET=your_value
heroku config:set DEBUG=False
heroku config:set ENVIRONMENT=production
```

4. **Create Procfile**

Create `Procfile` in root directory:

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && celery -A app.tasks.celery_app worker --loglevel=info
beat: cd backend && celery -A app.tasks.celery_app beat --loglevel=info
```

5. **Deploy**

```bash
git push heroku main
```

6. **Scale Workers**

```bash
heroku ps:scale web=1 worker=1 beat=1
```

7. **Initialize Database**

```bash
heroku run python backend/app/database.py init_db
```

8. **View Logs**

```bash
heroku logs --tail
```

### Heroku Frontend Deployment

For the React frontend, deploy separately:

```bash
cd frontend
heroku create debbie-ta-frontend
heroku buildpacks:set heroku/nodejs
git subtree push --prefix frontend heroku main
```

## Option 2: AWS Deployment

### Architecture

- **Backend**: ECS Fargate or EC2
- **Database**: RDS PostgreSQL
- **Redis**: ElastiCache
- **Frontend**: S3 + CloudFront or Amplify
- **Celery**: Separate ECS tasks

### Steps

1. **Create RDS PostgreSQL Instance**

```bash
aws rds create-db-instance \
    --db-instance-identifier debbie-ta-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password <password> \
    --allocated-storage 20
```

2. **Create ElastiCache Redis**

```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id debbie-ta-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

3. **Build and Push Docker Images**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name debbie-ta-backend
aws ecr create-repository --repository-name debbie-ta-frontend

# Build and push backend
cd backend
docker build -t debbie-ta-backend .
docker tag debbie-ta-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/debbie-ta-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/debbie-ta-backend:latest

# Build and push frontend
cd ../frontend
docker build -t debbie-ta-frontend .
docker tag debbie-ta-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/debbie-ta-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/debbie-ta-frontend:latest
```

4. **Create ECS Cluster and Services**

Use AWS Console or CloudFormation to create:
- ECS Cluster
- Task definitions for backend, celery worker, celery beat
- Services for each task

5. **Set Environment Variables**

In ECS task definitions, add all required environment variables.

6. **Frontend Deployment**

Option A: S3 + CloudFront
```bash
cd frontend
npm run build
aws s3 sync build/ s3://debbie-ta-frontend
```

Option B: AWS Amplify
```bash
npm install -g @aws-amplify/cli
amplify init
amplify add hosting
amplify publish
```

## Option 3: Google Cloud Platform

### Architecture

- **Backend**: Cloud Run
- **Database**: Cloud SQL PostgreSQL
- **Redis**: Memorystore
- **Frontend**: Firebase Hosting or Cloud Run
- **Celery**: Cloud Run (separate services)

### Steps

1. **Create Cloud SQL Instance**

```bash
gcloud sql instances create debbie-ta-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1
```

2. **Create Memorystore Redis**

```bash
gcloud redis instances create debbie-ta-redis \
    --size=1 \
    --region=us-central1
```

3. **Build and Deploy Backend**

```bash
cd backend

# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/debbie-ta-backend

# Deploy to Cloud Run
gcloud run deploy debbie-ta-backend \
    --image gcr.io/PROJECT_ID/debbie-ta-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=...,REDIS_URL=...
```

4. **Deploy Celery Worker**

```bash
gcloud run deploy debbie-ta-worker \
    --image gcr.io/PROJECT_ID/debbie-ta-backend \
    --platform managed \
    --region us-central1 \
    --command celery,-A,app.tasks.celery_app,worker,--loglevel=info \
    --no-allow-unauthenticated
```

5. **Deploy Celery Beat**

```bash
gcloud run deploy debbie-ta-beat \
    --image gcr.io/PROJECT_ID/debbie-ta-backend \
    --platform managed \
    --region us-central1 \
    --command celery,-A,app.tasks.celery_app,beat,--loglevel=info \
    --no-allow-unauthenticated
```

6. **Deploy Frontend**

```bash
cd frontend
npm run build

# Option A: Firebase Hosting
firebase init hosting
firebase deploy

# Option B: Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/debbie-ta-frontend
gcloud run deploy debbie-ta-frontend \
    --image gcr.io/PROJECT_ID/debbie-ta-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## Option 4: DigitalOcean App Platform

Simple deployment with managed infrastructure.

### Steps

1. **Create App**

- Go to DigitalOcean Console
- Create new App from GitHub repo
- Select `Debbie-TA` repository

2. **Configure Components**

- **Web Service**: Backend (backend directory)
  - Build command: `pip install -r requirements.txt`
  - Run command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`

- **Worker**: Celery Worker
  - Run command: `celery -A app.tasks.celery_app worker --loglevel=info`

- **Worker**: Celery Beat
  - Run command: `celery -A app.tasks.celery_app beat --loglevel=info`

- **Static Site**: Frontend (frontend directory)
  - Build command: `npm run build`
  - Output directory: `build`

3. **Add Managed Database**

- Add PostgreSQL database
- Add Redis instance

4. **Set Environment Variables**

Add all required environment variables in the App Platform console.

5. **Deploy**

Click "Deploy" - DigitalOcean will build and deploy automatically.

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Verify database connection
- [ ] Test API endpoints (visit /docs)
- [ ] Verify Redis connection
- [ ] Test deal alert sending
- [ ] Test email scanning
- [ ] Verify Celery tasks are running
- [ ] Check Celery beat schedule
- [ ] Test frontend loads correctly
- [ ] Verify API calls from frontend work
- [ ] Set up monitoring/logging
- [ ] Configure domain name (optional)
- [ ] Set up SSL certificate
- [ ] Enable backups for database

## Monitoring & Maintenance

### Health Checks

Backend provides health check endpoint:
```
GET /health
```

### Logs

Set up log aggregation:
- **Heroku**: Use Heroku logs or add-ons like Papertrail
- **AWS**: CloudWatch Logs
- **GCP**: Cloud Logging
- **DigitalOcean**: Built-in logging

### Monitoring

Consider adding:
- **Sentry**: Error tracking
- **New Relic**: Application performance monitoring
- **Datadog**: Infrastructure monitoring

### Database Backups

- **Heroku**: Automatic with paid plans
- **AWS RDS**: Enable automated backups
- **GCP Cloud SQL**: Enable automated backups
- **DigitalOcean**: Enable daily backups

## Cost Estimates

### Heroku (Hobby/Small Business)
- Hobby Postgres: $9/month
- Hobby Redis: $15/month
- Hobby Dynos (3): $21/month
- **Total**: ~$45/month

### AWS (Free Tier + Small)
- RDS t3.micro: ~$15/month
- ElastiCache t3.micro: ~$15/month
- ECS Fargate: ~$20-40/month
- **Total**: ~$50-70/month

### GCP (Small)
- Cloud SQL db-f1-micro: ~$10/month
- Memorystore: ~$30/month
- Cloud Run: ~$5-10/month
- **Total**: ~$45-50/month

### DigitalOcean App Platform
- Basic plan with database: ~$12-25/month
- Managed Database: ~$15/month
- **Total**: ~$27-40/month

## Scaling Considerations

As usage grows:

1. **Database**: Upgrade to larger instance size
2. **Celery Workers**: Add more worker instances
3. **Redis**: Upgrade to cluster for high availability
4. **Backend**: Add more API instances
5. **Caching**: Add caching layer (Redis cache)
6. **CDN**: Use CDN for frontend assets

## Security Best Practices

1. **Environment Variables**: Never commit secrets to git
2. **HTTPS**: Always use HTTPS in production
3. **Database**: Use SSL connections
4. **API Keys**: Rotate regularly
5. **Access Control**: Limit database access by IP
6. **Monitoring**: Set up alerts for unusual activity

## Troubleshooting Production Issues

### Check Service Status
```bash
# Heroku
heroku ps

# AWS
aws ecs describe-services --cluster <cluster-name> --services <service-name>

# GCP
gcloud run services describe <service-name>
```

### View Logs
```bash
# Heroku
heroku logs --tail --app debbie-ta-app

# AWS
aws logs tail /ecs/debbie-ta-backend --follow

# GCP
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Database Issues
```bash
# Heroku
heroku pg:info
heroku pg:diagnose

# AWS
aws rds describe-db-instances

# GCP
gcloud sql operations list --instance debbie-ta-db
```

Need help? Check logs first, then consult the platform-specific documentation.
