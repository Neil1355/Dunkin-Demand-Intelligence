# Password Reset System - Integration Guide

## What Was Added ✅

### Backend Changes
1. **Database Migration** → `migrations/0003_add_password_reset_tokens.sql`
   - New table for secure password reset tokens
   - 1-hour expiration window
   - One-time use (prevents token reuse)

2. **User Model Functions** → `models/user_model.py`
   - `request_password_reset(email)` - Generate reset token
   - `validate_reset_token(token)` - Verify token is valid & not expired
   - `reset_password(token, new_password)` - Update password

3. **Auth Routes** → `routes/auth.py`
   - `POST /auth/forgot-password` - Request reset link
   - `POST /auth/validate-reset-token` - Check token validity
   - `POST /auth/reset-password` - Complete password reset

4. **Email Service** → `services/email_service.py`
   - SendGrid integration (ready to configure)
   - Mailgun integration (alternative)
   - Beautiful email templates

### Frontend Changes
1. **New Components**
   - `frontend/src/pages/auth/ForgotPassword.tsx` - Request reset link page
   - `frontend/src/pages/auth/ResetPassword.tsx` - Set new password page

2. **Updated Components**
   - `frontend/src/pages/auth/LoginSignup.tsx` - Added "Forgot Password?" link
   - `frontend/src/App.tsx` - Integrated forgot/reset password flows

---

## 🚀 To Get It Working

### Step 1: Run Database Migration
```bash
# Connect to your database and run:
psql -d dunkin_demand -f backend/migrations/0003_add_password_reset_tokens.sql
```

### Step 2: Test Without Email (Optional)
The system works without email configured - you can test it:

1. Request password reset → Backend generates token
2. Frontend will show "Check your email" message
3. Manually get the token from database for testing:
```sql
SELECT token FROM password_reset_tokens WHERE user_id = 1 ORDER BY created_at DESC LIMIT 1;
```
4. Access reset page: `http://localhost:3000?token=YOUR_TOKEN_HERE`

### Step 3: Configure Email (Recommended)
Choose one of these services:

#### Option A: SendGrid (Recommended - Free tier available)
```bash
# 1. Sign up at sendgrid.com
# 2. Create API key
# 3. Add to .env:
export SENDGRID_API_KEY="SG.your_key_here"
export EMAIL_PROVIDER="sendgrid"
export EMAIL_FROM="noreply@dunkindemand.com"

# 4. Install package:
pip install sendgrid

# 5. Uncomment in routes/auth.py lines 56-58:
from services.email_service import send_password_reset_email

if result.get("status") == "success":
    frontend_url = os.getenv('FRONTEND_URL', 'https://your-domain.com')
    send_password_reset_email(email, result.get('token'), frontend_url)
```

#### Option B: Mailgun (Good alternative)
```bash
# 1. Sign up at mailgun.com
# 2. Add to .env:
export MAILGUN_DOMAIN="mg.yourdomain.com"
export MAILGUN_API_KEY="key-your_key_here"
export EMAIL_PROVIDER="mailgun"

# 3. Install package:
pip install requests

# 4. Uncomment email sending in routes/auth.py
```

### Step 4: Test the Flow
1. Start backend: `python -m flask --app backend.app run`
2. Start frontend: `npm run dev`
3. Click "Login" → "Forgot Password?"
4. Enter email → "Check your email" message
5. If email configured: Check inbox for reset link
6. Click link → Enter new password → Success!

---

## 🔒 Security Features Included

✅ **Token Expiration** - Links expire after 1 hour
✅ **One-Time Use** - Each token can only be used once
✅ **Secure Generation** - Uses `secrets.token_urlsafe(32)` 
✅ **Bcrypt Hashing** - Passwords hashed, not encrypted
✅ **Rate Limiting Ready** - Easy to add (see PRODUCTION_CHECKLIST.md)
✅ **User Privacy** - Doesn't reveal if email exists
✅ **Same-Size Hashes** - Prevents timing attacks

---

## 📝 API Documentation

### 1. Request Password Reset
```bash
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}

Response (200):
{
  "status": "success",
  "message": "If email exists, reset link will be sent"
}
```

### 2. Validate Token
```bash
POST /auth/validate-reset-token
Content-Type: application/json

{
  "token": "token_string_here"
}

Response (200) - Valid:
{
  "status": "success",
  "user_id": 123,
  "email": "user@example.com",
  "name": "John Doe"
}

Response (400) - Invalid/Expired:
{
  "status": "error",
  "message": "Invalid or expired token"
}
```

### 3. Reset Password
```bash
POST /auth/reset-password
Content-Type: application/json

{
  "token": "token_string_here",
  "password": "NewPassword123"
}

Response (200):
{
  "status": "success",
  "message": "Password reset successfully"
}

Response (400):
{
  "status": "error",
  "message": "Invalid or already-used token"
}
```

---

## 🎨 Frontend URLs

The reset link format in email will be:
```
https://your-domain.com?token=abc123xyz...
```

OR if using a dedicated reset page:
```
https://your-domain.com/reset-password?token=abc123xyz...
```

The `ResetPassword` component automatically:
- Extracts token from URL
- Validates it with backend
- Shows success/error messages
- Redirects to login on success

---

## 🧪 Testing Checklist

- [ ] Migration runs without errors
- [ ] Forgot password link appears on login page
- [ ] Clicking it shows the forgot password form
- [ ] Submitting shows "Check your email" message
- [ ] Database has new password_reset_tokens row
- [ ] Token has 1-hour expiration
- [ ] Manual token validation works
- [ ] Reset password form validates password length (8+ chars)
- [ ] New password can be set
- [ ] Token is marked as `used_at` after reset
- [ ] Same token can't be used twice
- [ ] Can login with new password
- [ ] Expired tokens show error message

---

## 🔗 Troubleshooting

### "No reset token provided"
- User didn't have `?token=...` in URL
- Frontend couldn't extract from query params

### "Invalid or expired reset link"
- Token doesn't exist in database
- Token expired (older than 1 hour)
- Token was already used
- Check: `SELECT * FROM password_reset_tokens WHERE token = 'xxx';`

### "Token has expired" (from backend)
- Older than 1 hour (3600 seconds)
- User waited too long
- Solution: Request a new reset link

### Email not sending
- SendGrid API key is invalid
- Email format is wrong in database
- Check logs: `flask logs --tail=50`

### Password won't reset
- "Passwords do not match" - Confirm password different
- "Password must be at least 8 characters" - Make it longer
- Check network tab for actual backend errors

---

## 🚀 Next Steps to Production

1. **Deploy migration**: Run on production database
2. **Add rate limiting**: Prevent brute force attempts (see PRODUCTION_CHECKLIST.md #1)
3. **Configure email**: Use SendGrid or Mailgun
4. **Test end-to-end**: Especially email delivery
5. **Add logging**: Track password reset requests
6. **Security headers**: Add CSP, X-Frame-Options (see PRODUCTION_CHECKLIST.md)
7. **Monitor**: Set up error tracking (Sentry)

---

## 📊 Database Schema

```sql
-- New table created by migration
CREATE TABLE password_reset_tokens (
  id SERIAL PRIMARY KEY,                      -- Unique ID
  user_id INTEGER NOT NULL,                   -- Which user
  token TEXT NOT NULL UNIQUE,                 -- The emailed link
  expires_at TIMESTAMP NOT NULL,              -- 1 hour from creation
  created_at TIMESTAMP DEFAULT NOW(),         -- When generated
  used_at TIMESTAMP DEFAULT NULL              -- When used (null = unused)
);
```

Indexes for performance:
- `idx_password_reset_tokens_token` - Fast lookups by token
- `idx_password_reset_tokens_user_id` - Find user's tokens
- `idx_password_reset_tokens_expires_at` - Cleanup expired tokens

---

## 💡 Pro Tips

1. **Clean up expired tokens** (recommended daily):
```sql
DELETE FROM password_reset_tokens 
WHERE expires_at < NOW() AND used_at IS NULL;
```

2. **Prevent token enumeration** - Rate limit `/forgot-password`:
```python
@limiter.limit("3 per minute")
@auth_bp.post("/forgot-password")
def forgot_password():
    # ...
```

3. **Log password resets** for audit trail:
```python
INSERT INTO audit_logs (user_id, action, created_at)
VALUES (user_id, 'PASSWORD_RESET', NOW());
```

4. **Send notification email** after successful reset:
```
Subject: "Your password was just changed"
Body: "If this wasn't you, click here to secure your account"
```

---

Questions? Check the docs or the code - it's all documented! 🎉
