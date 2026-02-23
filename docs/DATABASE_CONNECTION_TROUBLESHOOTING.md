# Database Connection Troubleshooting Guide

## Current Issue: 401 Unauthorized - Database Connection Failed

### Error Symptoms
```
POST /api/v1/auth/login 401 (Unauthorized)
API Error: {"message":"Database connection failed","status":"error"}
```

Backend logs show:
```
DNS resolution failed for db.zjqbgrtnhjesymxmlmoj.supabase.co: [Errno -5] No address associated with hostname
Network is unreachable
Failed to initialize connection pool: connection to server at "db.zjqbgrtnhjesymxmlmoj.supabase.co" port 5432 failed
```

---

## Root Cause

The Render deployment **cannot connect to your Supabase database** because:

1. **Most Likely:** `DATABASE_URL` environment variable is missing or incorrect on Render
2. **Possible:** Supabase database is not configured for external connections
3. **Possible:** Network/firewall blocking access from Render to Supabase
4. **Possible:** Supabase service in a region unreachable from Render's location

---

## Solution Steps

### Step 1: Verify DATABASE_URL on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your **dunkin-demand-intelligence** service
3. Click **Environment** tab
4. Look for `DATABASE_URL` variable
   - ✅ If it exists and looks like: `postgresql://user:password@db.xxx.supabase.co:5432/postgres`
   - ❌ If missing or empty

**If missing:**
```
Go to Step 2 - Get Supabase Connection String
```

**If present but still failing:**
```
See Step 4 - Verify Supabase Configuration
```

---

### Step 2: Get Correct Supabase Connection String

1. Open [Supabase Dashboard](https://app.supabase.com)
2. Select your **dunkin_demand** project
3. Navigate to **Settings** → **Database**
4. In the **Connection String** section, select **URI** tab
5. You should see:
   ```
   postgresql://postgres:[password]@db.[random-id].supabase.co:5432/postgres
   ```
6. Copy the **entire string** (including password)

---

### Step 3: Add DATABASE_URL to Render

1. Back in [Render Dashboard](https://dashboard.render.com)
2. Your **dunkin-demand-intelligence** service → **Environment**
3. Click **+ Add Environment Variable**
4. **Key:** `DATABASE_URL`
5. **Value:** Paste the connection string from Step 2
6. Click **Save** (not Deploy yet)

Example:
```
postgresql://postgres:YOUR_PASSWORD_HERE@db.zjqbgrtnhjesymxmlmoj.supabase.co:5432/postgres
```

---

### Step 4: Verify Environment Variables

Make sure all required variables are set on Render:

```
DATABASE_URL               ✅ Required - PostgreSQL connection string
FLASK_ENV                  ✅ Should be: production
SECRET_KEY                 ✅ Required - JWT signing key
SENDGRID_API_KEY          ✅ If using email features
FRONTEND_URL              ✅ Your Vercel frontend URL
```

---

### Step 5: Redeploy Service

Once you've set the environment variables:

1. In Render dashboard, go to **Deployments** tab
2. Click the **3-dot menu** next to the latest deployment
3. Select **Redeploy**
4. Wait for the deployment to complete (~2-3 minutes)

---

## Testing After Fix

### Test 1: Check Service Health
```bash
curl https://dunkin-demand-intelligence.onrender.com/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "message": "Database connection successful"
  }
}
```

### Test 2: Check Database Connectivity
```bash
curl https://dunkin-demand-intelligence.onrender.com/api/v1/health/db
```

Expected response:
```json
{
  "status": "success",
  "message": "Database connection successful",
  "ping": 1
}
```

### Test 3: Try Login
In your Vercel frontend, try logging in with a valid user account. Should now succeed.

---

## Supabase Configuration Checklist

If tests still fail after setting DATABASE_URL:

### ✅ Verify Supabase Project Settings

1. **Database URL Format** - Must be PostgreSQL URI (not HTTP)
   - ✅ Correct: `postgresql://user:pass@host:5432/db`
   - ❌ Incorrect: `https://xxx.supabase.co` (this is REST API)

2. **Password Encoding** - If your password has special characters, they must be URL-encoded
   - Example: `@` → `%40`, `#` → `%23`
   - Use [URL Encoder](https://www.urlencoder.org/) if unsure

3. **SSL Enabled** - Must use `sslmode=require`
   - Verify connection string ends with: `?sslmode=require`
   - This is automatically included by Supabase

4. **External Connections Allowed** - In Supabase project settings:
   - ✅ Network restrictions should allow external connections
   - Check **Settings** → **Network** → ensure no IP whitelist blocking Render

---

## Common Issues & Solutions

### "DNS resolution failed"
- **Cause:** The hostname cannot be resolved
- **Fix:** 
  - Verify DATABASE_URL is correctly copied from Supabase
  - Check for typos in the hostname
  - Ensure it includes `.supabase.co`

### "Network is unreachable"
- **Cause:** Render cannot reach Supabase server
- **Fix:**
  - Verify Supabase is in a region accessible from Render
  - Check if Supabase has an IP whitelist enabled
  - Try from local machine: `psql [your_database_url]`

### "Connection refused"
- **Cause:** Supabase unavailable or wrong port
- **Fix:**
  - Verify port is 5432
  - Check Supabase project status
  - Verify credentials in connection string

### "FATAL: invalid password"
- **Cause:** Wrong password in DATABASE_URL
- **Fix:**
  - Get fresh connection string from Supabase
  - Make sure special characters are URL-encoded

---

## Manual Database Connection Test

To test directly from your local machine:

```bash
# Copy your DATABASE_URL from Supabase
psql "postgresql://user:password@db.xxx.supabase.co:5432/postgres"

# If successful, you should get a PostgreSQL prompt:
# postgres=> 

# Type \q to exit
```

If this fails locally, the issue is with your Supabase setup, not Render.

---

## Monitoring & Logs

### View Render Logs
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service
3. Click **Logs** tab
4. Look for error messages during service startup

### Key Log Messages to Check
- ✅ `✓ Connection pool initialized successfully` → Database connected
- ❌ `CRITICAL: Could not initialize connection pool` → DATABASE_URL issue
- ❌ `DNS resolution failed` → Hostname not found

---

## Emergency: Use Test Login (Temporary)

If database is down but you need to test frontend:

```bash
# Call test login endpoint (no database required)
curl https://dunkin-demand-intelligence.onrender.com/api/v1/test-login
```

Returns mock user token for testing. **This is for development only!**

---

## Need Help?

1. **Check Supabase Status** → https://www.status.supabase.io/
2. **Render Status** → https://status.render.com/
3. **Test locally** with `psql` command above
4. **Check Render logs** for specific error messages
5. **Verify DATABASE_URL** was not accidentally truncated or modified
