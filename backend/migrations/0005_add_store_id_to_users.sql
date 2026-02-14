-- Migration: Add store_id to users table for multi-store support
-- This allows users to be associated with specific Dunkin' stores

ALTER TABLE users ADD COLUMN IF NOT EXISTS store_id INTEGER DEFAULT 12345;

-- Add index for store_id queries
CREATE INDEX IF NOT EXISTS idx_users_store_id ON users(store_id);

-- Add comment
COMMENT ON COLUMN users.store_id IS 'Dunkin store ID this user belongs to. Default is 12345 for demo/development.';
