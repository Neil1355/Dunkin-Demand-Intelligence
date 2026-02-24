-- Migration: Seed default products for all stores
-- Purpose: Add standard donut, munchkin, and other items

-- Clear existing products (optional - comment out if you want to keep existing)
-- DELETE FROM products;

-- Insert Donuts
INSERT INTO products (product_name, product_type, is_active) VALUES
('Chocolate Frosted with Sprinkles', 'donut', true),
('Strawberry Frosted with Sprinkles', 'donut', true),
('Vanilla Frosted with Sprinkles', 'donut', true),
('Boston Kreme', 'donut', true),
('Kreme Delight', 'donut', true),
('French Cruller', 'donut', true),
('Glazed', 'donut', true),
('Old Fashioned', 'donut', true),
('Glazed Chocolate', 'donut', true),
('Double Chocolate', 'donut', true),
('Chocolate Frosted', 'donut', true),
('Apple Crumb', 'donut', true)
ON CONFLICT (product_name) DO NOTHING;

-- Insert Munchkins
INSERT INTO products (product_name, product_type, is_active) VALUES
('Glazed Munchkin', 'munchkin', true),
('Chocolate Glazed Munchkin', 'munchkin', true),
('Old Fashioned Munchkin', 'munchkin', true)
ON CONFLICT (product_name) DO NOTHING;

-- Insert Other
INSERT INTO products (product_name, product_type, is_active) VALUES
('Coffee Roll', 'other', true)
ON CONFLICT (product_name) DO NOTHING;

-- Add unique constraint on product_name if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'products_product_name_key'
    ) THEN
        ALTER TABLE products ADD CONSTRAINT products_product_name_key UNIQUE (product_name);
    END IF;
END $$;
