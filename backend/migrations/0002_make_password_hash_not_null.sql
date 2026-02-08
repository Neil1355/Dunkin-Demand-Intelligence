-- Migration: make password_hash NOT NULL after backfilling existing rows
-- IMPORTANT: Only apply this migration after all existing users have non-NULL password_hash values.
-- Example backfill procedure:
-- 1) Run backend/scripts/seed_users.py to create test users or
-- 2) Prompt users to reset passwords and set password_hash via create_user
-- Once backfilled, run the ALTER TABLE below.

-- ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Note: The ALTER is commented out to avoid accidental application.
