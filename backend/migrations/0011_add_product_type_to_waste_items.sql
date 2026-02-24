-- Migration: Add product_type column to pending_waste_items
-- Purpose: Store product category for both DB and custom products

ALTER TABLE pending_waste_items
ADD COLUMN product_type VARCHAR(50) DEFAULT 'other';

COMMENT ON COLUMN pending_waste_items.product_type IS 'Product type/category: donut, munchkin, bagel, bakery, muffin, or other';
