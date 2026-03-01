-- Migration: Add unique constraint to daily_throwaway
-- Purpose: Prevent duplicate entries for same store/product/date combination

-- Add unique constraint on (store_id, product_id, date) to enable ON CONFLICT
ALTER TABLE daily_throwaway 
ADD CONSTRAINT daily_throwaway_store_product_date_unique 
UNIQUE (store_id, product_id, date);
