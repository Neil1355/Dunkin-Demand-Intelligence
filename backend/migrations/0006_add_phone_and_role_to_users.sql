-- Migration: Add phone number and role to users table
-- This allows collecting additional user information during signup

ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) DEFAULT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'employee';

-- Add comments
COMMENT ON COLUMN users.phone IS 'User phone number for contact purposes';
COMMENT ON COLUMN users.role IS 'User role: manager, assistant_manager, or employee';

-- Add index for role queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
