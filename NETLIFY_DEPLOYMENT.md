# Netlify + Railway Deployment Guide

Deploy the frontend to Netlify (free) and backend to Railway (affordable).

## Overview

- **Frontend (React)** → Netlify (Free)
- **Backend (FastAPI + Celery)** → Railway ($5-20/month)
- **Database (PostgreSQL)** → Railway (included)
- **Cache (Redis)** → Railway (included)

## Part 1: Deploy Backend to Railway

Railway is the easiest backend host with free trial and affordable pricing.

### Step 1: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Verify your account

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your repos
4. Select `Debbie-TA` repository

### Step 3: Add Services

Railway will detect your project. You need to create these services:

#### A. PostgreSQL Database

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway provisions it automatically
3. Note: Database URL is automatically set in `DATABASE_URL`

#### B. Redis

1. Click "New" → "Database" → "Add Redis"
2. Railway provisions it automatically
3. Note: Redis URL is automatically set in `REDIS_URL`

#### C. Web Service (FastAPI Backend)

1. Click "New" → "GitHub Repo" → Select your repo
2. Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11

#### D. Celery Worker

1. Click "New" → "GitHub Repo" → Select same repo
2. Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `celery -A app.tasks.celery_app worker --loglevel=info`
   - Disable health check (workers don't serve HTTP)

#### E. Celery Beat (Scheduler)

1. Click "New" → "GitHub Repo" → Select same repo
2. Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `celery -A app.tasks.celery_app beat --loglevel=info`
   - Disable health check

### Step 4: Configure Environment Variables

In Railway, go to the **Web Service** and add these variables:

```bash
# Database (automatically set by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Required API Keys
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+15551234567

# Alert Settings
ALERT_EMAIL=mom@email.com
ALERT_SMS=+15551234567
SECONDARY_EMAIL=your@email.com
SECONDARY_SMS=+15559876543

# Optional but Recommended
OPENAI_API_KEY=sk-...
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=DebbieTA/1.0

# Application Settings
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=your_secure_random_key_here

# Deal Thresholds
ASIA_MILES_THRESHOLD=60000
ASIA_CASH_THRESHOLD=100000
EUROPE_MILES_THRESHOLD=30000
EUROPE_CASH_THRESHOLD=70000
DEFAULT_AIRPORT=MSP
```

**Important**: Copy these same environment variables to:
- Celery Worker service
- Celery Beat service

### Step 5: Deploy

1. Railway auto-deploys on every git push
2. Initial deployment starts automatically
3. Wait for all services to show "Active" status
4. Click on Web Service → "Settings" → Copy the public URL
   - It will look like: `https://debbie-ta.railway.app`

### Step 6: Initialize Database

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run database initialization
railway run -s web python -c "from app.database import init_db; init_db()"
```

Or use Railway's web shell:
1. Go to Web Service
2. Click "Connect"
3. Run: `python -c "from app.database import init_db; init_db()"`

### Step 7: Verify Backend

Visit your Railway URL + `/docs`:
- Example: `https://debbie-ta.railway.app/docs`
- You should see the FastAPI documentation

Test the health endpoint:
- `https://debbie-ta.railway.app/health`

## Part 2: Deploy Frontend to Netlify

### Step 1: Update Backend URL

Edit `frontend/.env.production`:

```bash
REACT_APP_API_URL=https://your-railway-url.railway.app
REACT_APP_ENVIRONMENT=production
```

Also update `netlify.toml` redirect:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://your-railway-url.railway.app/api/:splat"
  status = 200
  force = true
```

### Step 2: Commit Changes

```bash
git add .
git commit -m "Configure production API URL for Netlify deployment"
git push origin main
```

### Step 3: Deploy to Netlify

#### Option A: Netlify Dashboard (Easiest)

1. Go to [netlify.com](https://www.netlify.com)
2. Sign up/Login with GitHub
3. Click "Add new site" → "Import an existing project"
4. Choose GitHub and select `Debbie-TA` repo
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
6. Click "Deploy site"
7. Wait for deployment (2-5 minutes)

#### Option B: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize site
cd frontend
netlify init

# Deploy
netlify deploy --prod
```

### Step 4: Configure Custom Domain (Optional)

1. In Netlify dashboard, go to "Domain settings"
2. Add your custom domain
3. Update DNS records as instructed
4. SSL is automatically provisioned

### Step 5: Verify Frontend

1. Visit your Netlify URL (e.g., `https://debbie-ta.netlify.app`)
2. Check that:
   - Dashboard loads
   - Deals page shows data from backend
   - API calls work (check browser console)

## Part 3: Enable CORS on Backend

Make sure your Railway backend URL is in the CORS origins.

Edit `backend/config/settings.py` if needed:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "https://your-netlify-site.netlify.app",  # Add your Netlify URL
]
```

Or set via Railway environment variable:

```bash
CORS_ORIGINS=https://your-netlify-site.netlify.app,http://localhost:3000
```

## Testing the Deployment

### 1. Test Backend Health

```bash
curl https://your-railway-url.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Debbie's Travel Agent Assistant",
  "version": "1.0.0"
}
```

### 2. Test API Endpoints

```bash
# Test deals endpoint
curl https://your-railway-url.railway.app/api/deals/

# Test clients endpoint
curl https://your-railway-url.railway.app/api/clients/
```

### 3. Test Frontend

1. Visit your Netlify URL
2. Open browser DevTools → Network tab
3. Navigate to Deals page
4. Verify API requests go to Railway backend
5. Check for CORS errors (there should be none)

### 4. Test Celery Tasks

Check Railway logs for:
- Celery worker is running
- Celery beat is scheduling tasks
- Tasks execute successfully

```bash
# View logs via Railway CLI
railway logs -s worker
railway logs -s beat
```

### 5. Test Notifications

```bash
# Via Railway CLI
railway run -s web python -c "from app.tasks.notification_tasks import send_test_alert; send_test_alert()"
```

Or use Railway's web shell to run the test.

## Costs Breakdown

### Railway (Backend)
- **Free Trial**: $5 credit to start
- **Hobby Plan**: ~$5/month
- **PostgreSQL**: Included
- **Redis**: Included
- **Bandwidth**: 100GB included

**Estimated Total**: $5-10/month depending on usage

### Netlify (Frontend)
- **Free Tier**:
  - 100GB bandwidth/month
  - Unlimited sites
  - HTTPS included
  - Continuous deployment

**Estimated Total**: $0/month (free tier sufficient)

### Total Monthly Cost: ~$5-10

## Monitoring & Maintenance

### Railway Monitoring

1. **Logs**: View real-time logs in Railway dashboard
2. **Metrics**: CPU, memory, network usage
3. **Alerts**: Set up email alerts for downtime

### Netlify Monitoring

1. **Analytics**: Built-in traffic analytics
2. **Deploy logs**: View build logs for each deployment
3. **Forms**: Can add form submissions (if needed)

### Database Backups

Railway automatically backs up PostgreSQL:
- Daily backups retained for 7 days
- Can manually trigger backup anytime
- One-click restore

## Continuous Deployment

Both platforms support auto-deploy on git push:

1. **Make changes** to code
2. **Commit and push** to GitHub
3. **Railway** auto-deploys backend
4. **Netlify** auto-deploys frontend
5. **Zero downtime** during deployments

## Troubleshooting

### Frontend not connecting to backend

1. Check CORS settings in backend
2. Verify `REACT_APP_API_URL` in `.env.production`
3. Check browser console for errors
4. Verify backend is responding: `curl https://your-railway-url/health`

### Celery tasks not running

1. Check Railway logs for worker/beat services
2. Verify Redis connection
3. Check environment variables are set on all services

### Database connection errors

1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL service is running in Railway
3. View database logs in Railway dashboard

### Email/SMS not sending

1. Verify Gmail API credentials are correct
2. Check Twilio credentials and balance
3. Test with send_test_alert task
4. Check worker logs for errors

## Advanced Configuration

### Custom Domain for Backend

Railway supports custom domains:

1. Go to Web Service → Settings
2. Add custom domain
3. Update DNS records
4. SSL automatically provisioned

### Environment Variables Management

Best practices:
- Keep secrets in Railway/Netlify dashboards, not in git
- Use different values for staging/production
- Rotate API keys regularly

### Scaling

As your usage grows:

**Railway**:
- Upgrade to higher plan for more resources
- Add more Celery workers
- Upgrade database instance

**Netlify**:
- Free tier handles most traffic
- Upgrade for more bandwidth if needed

## Summary

You now have:
- ✅ Frontend deployed to Netlify (free, global CDN)
- ✅ Backend deployed to Railway ($5-10/month)
- ✅ PostgreSQL database (managed, backed up)
- ✅ Redis for Celery (managed)
- ✅ Celery workers and scheduler running
- ✅ Auto-deploy on git push
- ✅ HTTPS on both frontend and backend
- ✅ Production-ready monitoring and logs

Total cost: **~$5-10/month** with Railway free trial to start!
