# Deployment Guide

Complete guide for deploying Dunkin Demand Intelligence to production.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Backend Deployment (Railway/Render)](#backend-deployment-railwayrender)
- [Database Setup (Supabase)](#database-setup-supabase)
- [Email Configuration (SendGrid)](#email-configuration-sendgrid)
- [Environment Variables](#environment-variables)
- [Post-Deployment Checklist](#post-deployment-checklist)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Vercel (Frontend)                      │
│                  React + Vite Application                   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────────┐    ┌──────────────────────┐
│  Railway/Render   │    │   SendGrid (Email)   │
│ (Backend API)     │    │  Password Resets etc │
│   Flask Server    │    └──────────────────────┘
└────────┬──────────┘
         │
         ▼
┌───────────────────────────────┐
│   Supabase PostgreSQL DB      │
│   (Data & Auth Storage)       │
└───────────────────────────────┘
```

---

## Frontend Deployment (Vercel)

### Step 1: Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Connect your GitHub account
4. Select your `Dunkin Demand Intelligence` repository
5. Click "Import"

### Step 2: Configure Build Settings

Vercel should auto-detect settings, but verify:

- **Root Directory:** `frontend/`
- **Build Command:** `npm run build`
- **Output Directory:** `build` or `dist`
- **Install Command:** `npm install`

### Step 3: Set Environment Variables

In Vercel Dashboard:

1. Go to **Settings → Environment Variables**
2. Add variable:
   ```
   Name: VITE_API_URL
   Value: https://your-backend-url.com
   Environments: Production, Preview, Development
   ```

3. Save and redeploy

### Step 4: Deploy

Click **Deploy** - Vercel will:
- Build the React app
- Run tests (if configured)
- Deploy to global CDN
- Assign unique URL

### Production Domain

To use custom domain:
1. Go to **Settings → Domains**
2. Add your domain
3. Update DNS records (Vercel provides instructions)
4. Wait for SSL certificate (automated)

---

## Backend Deployment (Railway/Render)

### Option A: Railway (Recommended)

#### 1. Create Account & Project

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your repository

#### 2. Configure Environment

1. Click "Add service"
2. Select PostgreSQL database
3. Click on Flask app service
4. Go to **Variables** tab
5. Add variables:

   ```env
   DATABASE_URL=postgresql://user:password@host:5432/db
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   SENDGRID_API_KEY=SG.your_key_here
   EMAIL_PROVIDER=sendgrid
   EMAIL_FROM=noreply@dunkindemand.com
   FRONTEND_URL=https://your-frontend-url.com
   ```

#### 3. Configure Start Command

1. Go to **Settings**
2. Set **Start Command:**
   ```
   python -m flask run
   ```

#### 4. Deploy

1. Go to **Deployments**
2. Click deploy (or auto-deploy on git push)
3. View logs and wait for "Running on http://..."

### Option B: Render

#### 1. Create Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +"
4. Select "Web Service"
5. Connect your repo

#### 2. Configure Service

```
Name: dunkin-api
Environment: Python 3
Region: Choose closest to you
Build Command: pip install -r backend/requirements.txt
Start Command: python -m flask run
```

#### 3. Add Environment Variables

1. Click "Environment"
2. Add all variables from Railway step 2

#### 4. Add PostgreSQL Database

1. Click "New +"
2. Select "PostgreSQL"
3. Note connection string
4. Update DATABASE_URL in web service

---

## Database Setup (Supabase)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Enter details:
   - Project name: `dunkin-demand`
   - Password: Strong password
   - Region: Close to users
4. Click "Create new project"

### Step 2: Create Database

1. Wait for project to initialize
2. Go to **SQL Editor**
3. Click "New query"
4. Paste contents of `schema.sql`
5. Click "Run"

### Step 3: Run Migrations

```bash
# Get connection string from Supabase → Settings → Database
# Format: postgresql://user:password@host:5432/postgres

psql postgresql://[user]:[password]@[host.supabase.co]:5432/postgres < schema.sql
```

### Step 4: Get Connection String

1. Go to **Settings → Database**
2. Copy **Connection string** (choose "Connecting to your database")
3. Add to backend environment as `DATABASE_URL`

---

## Email Configuration (SendGrid)

### Step 1: Create SendGrid Account

1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up (free tier = 100 emails/day)
3. Verify email address
4. Create new sender

### Step 2: Generate API Key

1. Go to **Settings → API Keys**
2. Click "Create API Key"
3. Name: `Dunkin Production`
4. Permissions: Mail Send
5. Copy key (save securely)

### Step 3: Add to Environment

In your deployment platform (Railway/Render):

```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_PROVIDER=sendgrid
EMAIL_FROM=noreply@dunkindemand.com
```

### Step 4: Test Email

```bash
curl -X POST "https://api.sendgrid.com/v3/mail/send" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{"to": [{"email": "test@example.com"}]}],
    "from": {"email": "noreply@dunkindemand.com"},
    "subject": "Test Email",
    "content": [{"type": "text/plain", "value": "Hello!"}]
  }'
```

---

## Environment Variables

### Production `.env` File

```env
# ========== DATABASE ==========
DATABASE_URL=postgresql://user:pass@host:5432/dunkin_demand

# ========== FLASK ==========
FLASK_ENV=production
FLASK_APP=backend.app
SECRET_KEY=use-secure-key-from-secrets-manager

# ========== EMAIL (SendGrid) ==========
SENDGRID_API_KEY=SG.your_key_here
EMAIL_PROVIDER=sendgrid
EMAIL_FROM=noreply@dunkindemand.com

# ========== FRONTEND ==========
FRONTEND_URL=https://dunkindemand.com

# ========== SECURITY ==========
CORS_ORIGINS=https://dunkindemand.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# ========== OPTIONAL ==========
DEBUG=false
LOG_LEVEL=INFO
```

### Variable Sources

| Variable | Source | How to Get |
|----------|--------|-----------|
| `DATABASE_URL` | Supabase/Railway | Settings → Database |
| `SECRET_KEY` | Generate new | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `SENDGRID_API_KEY` | SendGrid | Settings → API Keys |
| `FRONTEND_URL` | Your domain | e.g., `https://dunkindemand.com` |

---

## Post-Deployment Checklist

- [ ] Frontend accessible at your domain
- [ ] API responding at backend URL
- [ ] Database connection working
- [ ] Password reset emails sending
- [ ] SSL/HTTPS enabled
- [ ] Monitoring configured
- [ ] Error logging setup
- [ ] Daily backups enabled
- [ ] Database indexes created
- [ ] Test user accounts created
- [ ] Documentation updated
- [ ] Disaster recovery plan documented

---

## Monitoring & Logging

### Enable Sentry (Error Tracking)

1. Create account at [sentry.io](https://sentry.io)
2. Create new project (Python + Flask)
3. Get DSN from project settings
4. Add to backend:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### View Logs

**Railway:** Deployments → Select deployment → Logs
**Render:** Logs → View in browser

### Monitor Database

**Supabase:**
1. Go to **Realtime** for live updates
2. **Stats** for query performance
3. **Backups** for automatic snapshots

---

## SSL/HTTPS

- ✅ **Vercel:** Automatic (dunkindemand.vercel.app)
- ✅ **Railway:** Automatic for `.railway.app` domain
- ✅ **Render:** Automatic for `.onrender.com` domain
- ⚠️ **Custom Domain:** Need to add SSL certificate

For custom domain on Railway:
1. Go to **Settings → Custom Domains**
2. Add domain
3. Update DNS per instructions
4. SSL auto-provisioned (free)

---

## Rollback Procedure

### If Deployment Goes Wrong

**Vercel:**
1. Go to **Deployments**
2. Find last working deployment
3. Click "..." → "Redeploy"

**Railway:**
1. Go to **Deployments**
2. Select previous working version
3. Click "Deploy"

**Database:**
```bash
# Restore from backup
# Supabase: Settings → Backups → Restore
# Or use pg_restore if you have backup file
pg_restore -d dunkin_demand backup.dump
```

---

## Troubleshooting

### Frontend Not Loading

**Check:**
1. Vercel deployment status
2. Environment variable `VITE_API_URL`
3. Browser console for errors
4. Network tab for 404s

**Fix:**
```bash
# Rebuild frontend
vercel --prod  # If using Vercel CLI
```

### API Returns 500 Error

**Check:**
1. Backend deployment logs
2. Database connection string
3. Environment variables set
4. Database tables created

**Fix:**
```bash
# Reconnect to database
psql $DATABASE_URL  # Should connect successfully
```

### Email Not Sending

**Check:**
1. SendGrid API key in environment
2. Email format is valid
3. SendGrid dashboard → Activity
4. Check spam folder

**Test:**
```bash
curl -X POST "https://api.sendgrid.com/v3/mail/send" \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"personalizations":[{"to":[{"email":"test@example.com"}]}],"from":{"email":"noreply@dunkindemand.com"},"subject":"Test","content":[{"type":"text/plain","value":"Test"}]}'
```

### Database Full

**Check:**
```sql
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'dunkin_demand';
```

**Clean up:**
```sql
-- Delete old forecasts (older than 1 year)
DELETE FROM forecasts WHERE created_at < NOW() - INTERVAL '1 year';

-- Delete old audit logs (older than 6 months)
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '6 months';
```

---

## Performance Optimization

### Database Indexes

Already created in schema, but verify:

```sql
SELECT * FROM pg_indexes WHERE schemaname = 'public';
```

### Caching

Add Redis cache layer (optional):

```bash
# Railway dashboard → Services → PostgreSQL → Cache
# Or use Upstash: upstash.com
```

### CDN for Static Assets

Vercel includes automatic CDN for all deployments.

For custom assets, consider:
- Cloudflare
- AWS CloudFront
- Bunny CDN

---

## Security Checklist

- [ ] All environment variables set securely
- [ ] No hardcoded secrets in code
- [ ] HTTPS enabled on all domains
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Regular backups enabled
- [ ] Firewall rules configured
- [ ] DDoS protection enabled (most platforms)
- [ ] SQL injection prevention (using parameterized queries)
- [ ] XSS prevention (React auto-escaping)

---

## Support & Resources

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://docs.render.com
- **Supabase Docs:** https://supabase.com/docs
- **SendGrid Docs:** https://docs.sendgrid.com

---

**Last Updated:** February 13, 2026
