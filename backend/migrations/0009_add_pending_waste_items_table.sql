-- Migration: Add pending waste items table for product-level tracking
-- Purpose: Store individual product waste entries from QR code submissions

-- Create pending_waste_items table (product-level detail)
CREATE TABLE IF NOT EXISTS pending_waste_items (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES pending_waste_submissions(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    waste_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add index for faster lookups
CREATE INDEX idx_pending_waste_items_submission ON pending_waste_items(submission_id);
CREATE INDEX idx_pending_waste_items_product ON pending_waste_items(product_id);

-- Add comment
COMMENT ON TABLE pending_waste_items IS 'Stores individual product waste quantities for each pending submission';

-- Update pending_waste_submissions to remove simple count columns (they'll be calculated from items)
-- Note: We'll keep the existing columns for backward compatibility but won't use them
COMMENT ON COLUMN pending_waste_submissions.donut_count IS 'DEPRECATED: Use pending_waste_items table instead';
COMMENT ON COLUMN pending_waste_submissions.munchkin_count IS 'DEPRECATED: Use pending_waste_items table instead';
COMMENT ON COLUMN pending_waste_submissions.other_count IS 'DEPRECATED: Use pending_waste_items table instead';
