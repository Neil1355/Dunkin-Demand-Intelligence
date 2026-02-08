-- Migration: add password_hash column to users
-- Adds a nullable text column `password_hash` to store bcrypt hashes
ALTER TABLE IF EXISTS users
  ADD COLUMN IF NOT EXISTS password_hash text;

-- NOTE: existing rows will have NULL for password_hash. After deploying,
-- run a one-off script to set passwords for test users or require password reset.
