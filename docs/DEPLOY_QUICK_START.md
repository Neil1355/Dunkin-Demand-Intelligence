# 🚀 Quick Start: Deploy QR Code & Security Features

**Time to Deploy:** ~15 minutes  
**Difficulty:** Easy  
**Risk Level:** Low (backward-compatible)

---

## Step 1: Update Backend Dependencies (2 min)

```bash
cd backend

# Install new packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "Flask-Limiter|Pillow"
```

**New Packages:**
- Flask-Limiter (3.5.0) - Rate limiting
- Pillow (10.1.0) - QR image generation
- requests (2.31.0) - HTTP utilities

---

## Step 2: Run Database Migrations (5 min)

```bash
# Apply QR code tables
psql $DATABASE_URL < backend/migrations/0003_add_qr_codes_table.sql

# Apply audit & stores tables
psql $DATABASE_URL < backend/migrations/0004_add_audit_log_and_stores.sql

# Verify new tables exist
psql $DATABASE_URL -c "\dt" 

# Should show new tables:
# qr_codes, qr_access_log, audit_log, stores
```

### Verify Migrations

```bash
# Check qr_codes table
psql $DATABASE_URL -c "\d qr_codes"

# Check audit_log table
psql $DATABASE_URL -c "\d audit_log"

# Count rows (should be 0)
psql $DATABASE_URL -c "SELECT COUNT(*) FROM qr_codes;"
```

---

## Step 3: Verify Environment Variables (2 min)

Update `backend/.env`:

```env
# Required (should already exist)
DATABASE_URL=postgresql://...
FLASK_ENV=production
SECRET_KEY=your-secret-key

# Verify SendGrid is set
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_FROM=noreply@dunkindemand.com
FRONTEND_URL=https://dunkin-demand-intelligence.vercel.app

# New: Rate limiting (optional in production)
LIMITER_STORAGE_URL=memory://  # Use Redis for multi-server
```

---

## Step 4: Test Locally (3 min)

```bash
# Start backend
cd backend
python -m flask --app app run --debug

# In another terminal, test QR endpoint
curl http://localhost:5000/api/v1/qr/store/1
```

**Expected Response:**
```json
{
  "store_id": 1,
  "qr_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "qr_url": "https://dunkin-demand-intelligence.vercel.app/waste/submit?store_id=1",
  "status": "created"
}
```

---

## Step 5: Deploy to Production (3 min)

### Frontend (Vercel - Auto-Deploy)

```bash
cd frontend
npm install  # Install new dependencies (if any)
git add .
git commit -m "feat: Add QR code management and security enhancements"
git push
# Auto-deploys to Vercel
```

### Backend (Railway/Render)

```bash
cd backend
git add .
git commit -m "feat: Add QR code, rate limiting, audit logging"
git push
# Auto-deploys and runs migrations (if set up)
# Or manually run migrations on Railway/Render:
```

**Manual Migration (if needed):**
```bash
# Railway
railway run psql $DATABASE_URL < migrations/0003_add_qr_codes_table.sql
railway run psql $DATABASE_URL < migrations/0004_add_audit_log_and_stores.sql

# Render - use Render Dashboard → Logs → Run custom command
psql $DATABASE_URL < migrations/0003_add_qr_codes_table.sql
```

---

## Step 6: Verify Production Deployment (2 min)

```bash
# Test QR creation
curl https://your-api.com/api/v1/qr/store/1

# Test rate limiting (this should fail after 5 attempts)
for i in {1..6}; do
  curl -X POST https://your-api.com/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}'
  echo "Attempt $i"
done
# 6th request should return 429 Too Many Requests

# Check database tables exist
psql $DATABASE_URL -c "\dt" | grep -E "qr_codes|audit_log|stores"
```

---

## Step 7: Test QR Feature in UI (3 min)

1. **Navigate** to Manager Dashboard
2. **Find** QR Code Management section
3. **Click** "Create QR Code"
4. **Download** with header
5. **View** in image viewer - should show:
   - "Submit Waste for Today"
   - "By Scanning QR Code Below"
   - QR code
   - "Store ID: 1"

---

## 🎯 Features Now Available

### ✅ QR Code Management
- One QR per store
- Download with custom header
- Access audit trail
- Regenerate if needed

### ✅ Rate Limiting
- 5 login attempts/minute max
- 3 signup attempts/minute max
- Protects against brute force

### ✅ Audit Logging
- All user actions logged
- 16 action types tracked
- Query user activity: `SELECT * FROM audit_log WHERE user_id=123`

### ✅ Input Validation
- Email validation
- Password strength checking
- Null byte removal

---

## 📊 Database Changes Summary

**New Tables:** 4
- `qr_codes` - One per store, base64 PNG
- `qr_access_log` - Download/scan tracking
- `audit_log` - User action logging (16 types)
- `stores` - Store locations & managers

**New Size:** ~50MB (minimal impact)

**New Indexes:** 7 (performance optimized)

---

## ⚠️ Rollback Plan (If Needed)

If something breaks, rollback is easy:

```sql
-- Drop new tables (if migration failed)
DROP TABLE IF EXISTS qr_access_log;
DROP TABLE IF EXISTS qr_codes;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS stores;

-- Everything else still works fine
```

**Note:** Rollback loses QR/audit data from after migration. Keep backups!

---

## 🔍 Troubleshooting

### Problem: Migration Fails

```bash
# Check if migrations were already applied
psql $DATABASE_URL -c "SELECT * FROM qr_codes LIMIT 1;"

# If table exists, migration already ran (safe to ignore)
# If table doesn't exist, run migration again
psql $DATABASE_URL < backend/migrations/0003_add_qr_codes_table.sql
```

### Problem: QR Download Returns Error

```
Error: "QR code not found"
Solution: Create QR first with GET /api/v1/qr/store/{store_id}
```

### Problem: Rate Limiting Too Strict

```python
# Edit backend/utils/security.py, change limits:
RATE_LIMITS = {
    'auth_login': "10 per minute",  # Changed from 5
    ...
}
```

### Problem: Audit Log Growing Too Large

```sql
-- Archive old logs (> 90 days)
CREATE TABLE audit_log_archive AS
  SELECT * FROM audit_log WHERE created_at < NOW() - INTERVAL '90 days';

DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '90 days';

-- Result: Smaller table, faster queries
```

---

## ✅ Deployment Checklist

- [ ] New Python packages installed (`pip install -r requirements.txt`)
- [ ] Database migrations ran successfully (`psql ... < migrations/...`)
- [ ] New tables verified in database (`\dt`)
- [ ] Environment variables set (SENDGRID_API_KEY, FRONTEND_URL)
- [ ] Backend deployed (git push)
- [ ] Frontend deployed (git push)
- [ ] QR endpoint tested locally (`curl localhost:5000/api/v1/qr/store/1`)
- [ ] QR endpoint tested in production
- [ ] QR feature tested in UI (create → download → verify)
- [ ] Rate limiting tested (too many login attempts fails)
- [ ] Audit log populated (check: SELECT * FROM audit_log LIMIT 5)
- [ ] No errors in server logs

---

## 🎓 What's New

### For Managers
- **New Feature:** QR Code Management
  - Location: Manager Dashboard → QR Codes
  - Download with header for printing
  - One per store

### For Employees
- **New Feature:** Scan to Submit Waste
  - Scan QR code in store
  - Opens mobile form
  - Auto-fills store ID

### For Admins
- **New Feature:** Audit Logging
  - All user actions tracked
  - Query: `SELECT * FROM audit_log`
  - 16 action types logged

### For Security
- **New Feature:** Rate Limiting
  - Protects against brute force
  - Per-IP per-endpoint limits
  - Configurable in `/backend/utils/security.py`

---

## 📚 Documentation

Key files to review:

```
docs/SECURITY.md                  ← Security features explained
docs/DATABASE_OPTIMIZATION.md      ← Table consolidation guide
IMPLEMENTATION_NOTES.md            ← Complete implementation details
PASSWORD_RESET_GUIDE.md            ← Authentication details
```

---

## 🚀 Next Steps

**Today:**
- [ ] Deploy and verify QR feature works

**This Week:**
- [ ] Monitor rate limiting (check: `SELECT * FROM audit_log WHERE action_type='login_failed'`)
- [ ] Verify QR downloads working
- [ ] Check audit logs for patterns

**This Month:**
- [ ] Get user feedback on QR feature
- [ ] Consider table consolidation (optional)
- [ ] Review PRODUCTION_CHECKLIST.md

---

## ❓ Quick Reference

```bash
# Check if QR code exists for store 1
curl https://your-api.com/api/v1/qr/status/1

# Create/get QR code
curl https://your-api.com/api/v1/qr/store/1

# Download QR with header
curl https://your-api.com/api/v1/qr/download/1 > qr.png

# View recent audit logs
psql $DATABASE_URL -c \
  "SELECT action_type, user_id, created_at FROM audit_log ORDER BY created_at DESC LIMIT 10;"

# View user activity for user 123
psql $DATABASE_URL -c \
  "SELECT * FROM audit_log WHERE user_id=123 ORDER BY created_at DESC;"

# Test rate limiting (should fail on 6th attempt)
for i in {1..6}; do 
  curl -X POST https://your-api.com/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"x","password":"x"}'
done
```

---

**Status:** ✅ Ready to Deploy  
**Time:** ~15 minutes  
**Risk:** Low (backward-compatible)  
**Support:** See IMPLEMENTATION_NOTES.md

---

**Questions?** Review the full documentation in `/docs/` folder!
