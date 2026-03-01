-- Add unique constraint on product_name
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'products_product_name_key'
    ) THEN
        ALTER TABLE products ADD CONSTRAINT products_product_name_key UNIQUE (product_name);
    END IF;
END $$;

-- Insert All Products
INSERT INTO products (product_name, product_type, is_active) VALUES
-- Bagels
('Cinnamon Raisin', 'bagel', true),
('Everything', 'bagel', true),
('Multigrain', 'bagel', true),
('Plain', 'bagel', true),
('Sesame', 'bagel', true),
-- Bakery
('Bagels', 'bakery', true),
('Cheddar Twist', 'bakery', true),
('Coffee Roll', 'bakery', true),
('Fancies', 'bakery', true),
('Muffins', 'bakery', true),
('Plain Croissants', 'bakery', true),
-- Donuts
('Apple Crumb', 'donut', true),
('Blueberry Glazed', 'donut', true),
('Boston Kreme', 'donut', true),
('Choc Frosted', 'donut', true),
('Choc Frosted Sprinkles', 'donut', true),
('Choc Glazed', 'donut', true),
('Chocolate Frosted', 'donut', true),
('Chocolate Frosted with Sprinkles', 'donut', true),
('Donuts', 'donut', true),
('Double Choc Glazed', 'donut', true),
('Double Chocolate', 'donut', true),
('French Cruller', 'donut', true),
('Glazed', 'donut', true),
('Glazed Chocolate', 'donut', true),
('Jelly', 'donut', true),
('Kreme Delight', 'donut', true),
('Old Fashioned', 'donut', true),
('Straw Frosted Sprinkle', 'donut', true),
('Strawberry Frosted with Sprinkles', 'donut', true),
('Van Frosted Sprinkles', 'donut', true),
('Vanilla Frosted with Sprinkles', 'donut', true),
-- Muffins
('Blueberry', 'muffin', true),
('Chocolate Chip', 'muffin', true),
('Coffee Cake', 'muffin', true),
('Corn', 'muffin', true),
-- Munchkins
('Glazed Munchkins', 'munchkin', true),
('Chocolate Glazed Munchkins', 'munchkin', true),
('Glazed Old Fashioned Munchkins', 'munchkin', true),
-- Other
('Golden Chocolate', 'other', true),
('Holiday Lights', 'other', true),
('Holiday Munchkins', 'other', true),
('Holiday Spinkle Munch', 'other', true),
('Holiday Sprinkle Munc', 'other', true),
('Holiday Tree', 'other', true),
('Salted Dark Choc Mun', 'other', true),
('Salted Dark Choc Munc', 'other', true),
('Sugared', 'other', true),
('Winter Snowman', 'other', true)
ON CONFLICT (product_name) DO NOTHING;

-- Verify
SELECT COUNT(*) as total_products, product_type, COUNT(*) as count 
FROM products 
GROUP BY product_type 
ORDER BY product_type;
