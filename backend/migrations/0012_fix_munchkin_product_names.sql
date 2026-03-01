-- Migration: Fix corrupted munchkin product names
-- Purpose: Clean up the messed up munchkin names and keep only the three correct ones

-- Delete the corrupted/unwanted munchkin products
DELETE FROM products 
WHERE product_type = 'munchkin' 
  AND product_name IN (
    'Chocolate Munchkin',
    'Munchkins',
    'Old Fashioned Munch',
    'Wicked Munchkin'
  );

-- Update existing munchkin product names to correct versions
UPDATE products 
SET product_name = 'Glazed Munchkins'
WHERE product_type = 'munchkin' 
  AND (product_name = 'Glazed Munchkin');

UPDATE products 
SET product_name = 'Chocolate Glazed Munchkins'
WHERE product_type = 'munchkin' 
  AND (product_name = 'Chocolate Glazed Munchkin');

UPDATE products 
SET product_name = 'Glazed Old Fashioned Munchkins'
WHERE product_type = 'munchkin' 
  AND (product_name = 'Old Fashioned Munchkin');

-- Insert the three correct munchkins if they don't already exist
INSERT INTO products (product_name, product_type, is_active) VALUES
('Glazed Munchkins', 'munchkin', true),
('Chocolate Glazed Munchkins', 'munchkin', true),
('Glazed Old Fashioned Munchkins', 'munchkin', true)
ON CONFLICT (product_name) DO NOTHING;
