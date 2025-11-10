# Railway Deployment - Step by Step

This guide will help you deploy the backend to Railway successfully.

## Prerequisites

1. Railway account (sign up at railway.app with GitHub)
2. GitHub repository connected
3. PostgreSQL and Redis added in Railway

## Common Issues & Solutions

### Issue 1: "No Python Application Detected"

**Problem**: Railway can't find your Python app because it's in the `backend/` subdirectory.

**Solution**: Use the config files provided (`railway.toml` and `nixpacks.toml`)

### Issue 2: "Module Not Found" Errors

**Problem**: Python can't find the `config` or `app` modules.

**Solution**: Set `PYTHONPATH=/app/backend` in environment variables.

### Issue 3: Multiple Services Not Working

**Problem**: Need to run web, worker, and beat as separate services.

**Solution**: Deploy 3 separate services from the same repo.

## Step-by-Step Deployment

### 1. Add PostgreSQL Database

1. In Railway dashboard, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway creates it and sets `DATABASE_URL` automatically
4. ✅ Done - no further configuration needed

### 2. Add Redis

1. Click **"New"** → **"Database"** → **"Add Redis"**
2. Railway creates it and sets `REDIS_URL` automatically
3. ✅ Done

### 3. Deploy Web Service (FastAPI)

1. Click **"New"** → **"GitHub Repo"**
2. Select your `Debbie-TA` repository
3. Railway will start deploying - **it will likely fail first time** (that's okay!)

#### Configure Web Service:

4. Click on the service → **"Settings"**
5. Scroll to **"Deploy"** section
6. Set **Custom Start Command**:
   ```bash
   ./start-web.sh
   ```
   OR:
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

7. Scroll to **"Environment Variables"** and add:

```bash
# Python Configuration
PYTHONPATH=/app/backend
PYTHONUNBUFFERED=1

# Application Settings
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=your-secret-key-change-this

# Email & SMS
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+15551234567

# Alerts
ALERT_EMAIL=mom@email.com
ALERT_SMS=+15551234567

# API Keys (optional)
OPENAI_API_KEY=sk-...
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Thresholds
ASIA_MILES_THRESHOLD=60000
ASIA_CASH_THRESHOLD=100000
EUROPE_MILES_THRESHOLD=30000
EUROPE_CASH_THRESHOLD=70000
DEFAULT_AIRPORT=MSP

# CORS (add your Netlify URL when ready)
CORS_ORIGINS=http://localhost:3000,https://your-netlify-site.netlify.app
```

8. Click **"Redeploy"** at the top

9. Wait for deployment to complete (2-5 minutes)

10. Click **"Settings"** → **"Networking"** → **"Generate Domain"**
    - Copy your public URL (e.g., `https://debbie-ta-production.up.railway.app`)

11. Test it: Visit `https://your-url.railway.app/health`
    - Should return: `{"status":"healthy",...}`

### 4. Deploy Celery Worker

1. Click **"New"** → **"GitHub Repo"** → Select `Debbie-TA` again
2. Rename the service to **"celery-worker"**
3. Go to **Settings** → **"Deploy"**
4. Set **Custom Start Command**:
   ```bash
   ./start-worker.sh
   ```
   OR:
   ```bash
   cd backend && celery -A app.tasks.celery_app worker --loglevel=info
   ```

5. **Important**: Scroll to **"Healthcheck"** and:
   - Toggle **"Healthcheck Enabled"** to **OFF**
   - (Workers don't serve HTTP, so healthcheck would fail)

6. Copy **ALL environment variables** from the Web service:
   - Same `PYTHONPATH`, `DATABASE_URL`, `REDIS_URL`, etc.
   - Or use Railway's "Copy variables from another service" feature

7. Click **"Deploy"**

### 5. Deploy Celery Beat (Scheduler)

1. Click **"New"** → **"GitHub Repo"** → Select `Debbie-TA` again
2. Rename the service to **"celery-beat"**
3. Go to **Settings** → **"Deploy"**
4. Set **Custom Start Command**:
   ```bash
   ./start-beat.sh
   ```
   OR:
   ```bash
   cd backend && celery -A app.tasks.celery_app beat --loglevel=info
   ```

5. **Important**: Turn **OFF** healthcheck (Settings → Healthcheck)

6. Copy all environment variables from Web service

7. Click **"Deploy"**

### 6. Initialize Database

Once the Web service is running:

#### Option A: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Select the "web" service when prompted

# Initialize database
railway run python -c "import sys; sys.path.insert(0, 'backend'); from app.database import init_db; init_db()"
```

#### Option B: Railway Shell (Easier)

1. Go to your **Web service** in Railway dashboard
2. Click **"Connect"** tab
3. In the shell, run:
   ```bash
   cd backend
   python -c "from app.database import init_db; init_db()"
   ```

You should see: `Database tables created successfully!`

### 7. Verify Everything Works

#### Check Web Service:
```bash
curl https://your-url.railway.app/health
curl https://your-url.railway.app/api/deals/
curl https://your-url.railway.app/docs  # View in browser
```

#### Check Logs:

1. **Web Service Logs**:
   - Click on web service → "Deployments" → Latest deployment → "View Logs"
   - Should see: "Starting Debbie's Travel Agent Assistant"

2. **Worker Logs**:
   - Click on celery-worker → "Deployments" → "View Logs"
   - Should see: "celery@... ready"

3. **Beat Logs**:
   - Click on celery-beat → "Deployments" → "View Logs"
   - Should see: "Scheduler: Sending due task..."

#### Test Background Tasks:

In the Railway shell (Connect tab):
```bash
cd backend
python -c "from app.tasks.notification_tasks import send_test_alert; send_test_alert()"
```

You should receive a test email/SMS!

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'config'"

**Fix**: Add to environment variables:
```bash
PYTHONPATH=/app/backend
```

### Error: "ModuleNotFoundError: No module named 'app'"

**Fix**: Make sure start command has `cd backend` first:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Error: "Could not import settings"

**Fix**: Check that `config/settings.py` exists and `PYTHONPATH` is set.

### Error: "Database connection failed"

**Fix**:
1. Check PostgreSQL service is running
2. Verify `DATABASE_URL` environment variable is set
3. Check database connection string format

### Error: "Redis connection failed"

**Fix**:
1. Check Redis service is running
2. Verify `REDIS_URL` environment variable is set

### Worker/Beat not starting

**Fix**:
1. Turn OFF healthcheck for worker and beat services
2. Check logs for actual error
3. Verify all environment variables are copied from web service

### "Port already in use" or similar

**Fix**: Use `$PORT` variable, not hardcoded port:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Deployments keep failing

**Fix**: Check build logs carefully:
1. Go to failed deployment
2. Click "View Logs"
3. Look for actual error (usually near the bottom)
4. Common issues:
   - Missing dependencies in requirements.txt
   - Import errors (fix with PYTHONPATH)
   - Environment variables not set

## Service Summary

After successful deployment, you should have:

| Service | Status | URL | Purpose |
|---------|--------|-----|---------|
| PostgreSQL | ✅ Running | Internal | Database |
| Redis | ✅ Running | Internal | Cache/Queue |
| web | ✅ Running | `https://your-app.railway.app` | FastAPI backend |
| celery-worker | ✅ Running | No public URL | Background tasks |
| celery-beat | ✅ Running | No public URL | Task scheduler |

## Next Steps

1. ✅ Copy your Railway web URL
2. ✅ Update `frontend/.env.production` with this URL
3. ✅ Update `netlify.toml` redirect with this URL
4. ✅ Deploy frontend to Netlify (see NETLIFY_DEPLOYMENT.md)

## Monitoring

### View Logs
- Click any service → "Deployments" → "View Logs"

### View Metrics
- Click any service → "Metrics"
- See CPU, memory, network usage

### Database Size
- Click PostgreSQL → "Metrics"
- Monitor database growth

### Set Alerts
- Go to project settings
- Add email for deployment failures

## Cost Management

Railway pricing:
- $5 free credit/month (trial)
- ~$5-10/month for this setup
- Pay only for what you use

To minimize costs:
- Start with smallest database instance
- Scale up only when needed
- Monitor usage in Railway dashboard

## Getting Help

If you're still stuck:

1. **Check Railway Logs**: Most errors are shown there
2. **Railway Discord**: Very helpful community
3. **Railway Docs**: railway.app/docs
4. **GitHub Issues**: Open issue on this repo

## Quick Reference

### Restart a Service
Click service → "Settings" → "Redeploy"

### View Environment Variables
Click service → "Variables"

### Change Start Command
Click service → "Settings" → "Deploy" → "Custom Start Command"

### Add a Custom Domain
Click service → "Settings" → "Networking" → "Custom Domain"

### Database Backups
Click PostgreSQL → "Backups" → "Create Backup"

That's it! Your backend should now be running on Railway. 🎉
