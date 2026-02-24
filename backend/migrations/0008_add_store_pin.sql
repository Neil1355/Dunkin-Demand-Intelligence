-- Migration: Add store PIN for QR code waste submissions
-- Purpose: Allow stores to set a 4-digit PIN for validating employee submissions

-- Add store_pin column to stores table
ALTER TABLE stores 
ADD COLUMN IF NOT EXISTS store_pin VARCHAR(4);

-- Add index for PIN lookups
CREATE INDEX IF NOT EXISTS idx_stores_pin ON stores(store_pin) WHERE store_pin IS NOT NULL;

-- Add comment
COMMENT ON COLUMN stores.store_pin IS '4-digit PIN for employee waste submissions via QR code (optional, enhances security)';

-- Note: Managers can set this PIN in their store settings
-- If NULL, submissions will still work but without PIN validation
