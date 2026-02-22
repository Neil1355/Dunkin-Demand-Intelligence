# Render/Railway Deployment Configuration

## Critical Environment Variables

The backend deployment on Render or Railway **requires** these environment variables to be configured in your dashboard. Missing any of these will cause 500 errors and CORS issues.

### 1. **DATABASE_URL** (REQUIRED)
The PostgreSQL connection string to Supabase.

```
postgresql://postgres:YOUR_PASSWORD@db.zjqbgrtnhjesymxmlmoj.supabase.co:5432/postgres
```

**Why it matters:**
- Without this, ALL database queries fail (quick-stats, QR codes, daily data entry, etc.)
- Returns cryptic errors like `{"error":"0"}` or generic connection failures
- Set this FIRST before testing anything

**How to find it:**
1. Go to Supabase dashboard → Project settings → Database
2. Copy the connection string (PostgreSQL)
3. Paste into Render/Railway environment variables as `DATABASE_URL`

---

### 2. **JWT_SECRET_KEY** (RECOMMENDED)
Secret key for JWT token signing.

```
your-super-secret-key-change-this-in-production
```

**Default:** `dev-secret-key-change-in-production` (insecure)

**How to set:**
1. Generate a random string: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Add to environment as `JWT_SECRET_KEY`

---

### 3. **FRONTEND_URL** (OPTIONAL)
The frontend URL that QR codes should redirect to.

```
https://dunkin-demand-intelligence.vercel.app
```

**Why it matters:**
- QR codes encode this URL to direct users to the waste submission form
- If set to wrong domain, QR codes show "404 deployment not found"

**Default:** `https://dunkin-demand-intelligence.vercel.app`

**How to set:**
1. Check your Vercel deployment URL
2. Add as `FRONTEND_URL` environment variable
3. Ensure your Vercel project is actually deployed there

---

### 4. **CORS_ORIGINS** (OPTIONAL)
Allowed origins for CORS requests. Hard-coded defaults should work for most cases.

**Hard-coded defaults:**
- `https://dunkin-demand-intelligence-neil-barots-projects-55b3b305.vercel.app`
- `https://dunkin-demand-intelligence-h7bvxrxzh.vercel.app`  
- `https://dunkin-demand-intelligence.vercel.app`
- `http://localhost:*` (for local development)

---

## Step-by-Step Configuration for Render

1. Go to **Render Dashboard** → Your Web Service
2. Click **Environment**
3. Add variables:
   ```
   DATABASE_URL = postgresql://postgres:YOUR_PASSWORD@db.zjqbgrtnhjesymxmlmoj.supabase.co:5432/postgres
   JWT_SECRET_KEY = (your-generated-secret)
   FRONTEND_URL = https://dunkin-demand-intelligence.vercel.app
   ```
4. Click **Save changes**
5. Service will auto-redeploy

---

## Step-by-Step Configuration for Railway

1. Go to **Railway Dashboard** → Your Project
2. Click the **Backend Service**
3. Go to **Variable Reference**
4. Add variables:
   ```
   DATABASE_URL = postgresql://postgres:YOUR_PASSWORD@db.zjqbgrtnhjesymxmlmoj.supabase.co:5432/postgres
   JWT_SECRET_KEY = (your-generated-secret)
   FRONTEND_URL = https://dunkin-demand-intelligence.vercel.app
   ```
5. Save changes
6. Redeploy

---

## Troubleshooting

### "Failed to load quick stats: Error: {error:0}"
- ❌ `DATABASE_URL` not set or incorrect
- ✅ Check that connection string is valid (can connect locally first)

### "QR code shows 404 deployment not found"
- ❌ `FRONTEND_URL` pointing to wrong domain
- ❌ Vercel deployment doesn't exist at that URL
- ✅ Verify Vercel deployment is actually live
- ✅ Set `FRONTEND_URL` to your actual Vercel URL

### "CORS: Response to preflight request doesn't pass access control check"
- ❌ Frontend origin not in allowed list
- ✅ This is now fixed with default CORS configuration
- ✅ If custom frontend URL, add it to `CORS_ORIGINS`

### "Failed to save data: TypeError: Failed to fetch"
- ❌ CORS preflight request being blocked
- ✅ This is now fixed with global OPTIONS handler
- ✅ Ensure `DATABASE_URL` is set (backend needs to respond to preflight)

---

## Verification Checklist

After setting environment variables:

- [ ] Backend starts without "connection pool" warnings
- [ ] GET `https://your-backend.com/api/v1/health` returns 200 OK
- [ ] Dashboard quick-stats endpoint returns data (with auth token)
- [ ] QR code redirects to correct Vercel URL
- [ ] Manual data entry saves without CORS errors

---

**Last Updated:** February 22, 2026
