-- Diagnostic queries to check data flow from pending waste approval to dashboard

-- 1. Check pending waste submissions and their items
SELECT 
    pws.id AS submission_id,
    pws.store_id,
    pws.submitter_name,
    pws.submission_date,
    pws.status,
    pws.reviewed_at,
    pwi.product_id,
    pwi.product_name,
    pwi.waste_quantity
FROM pending_waste_submissions pws
LEFT JOIN pending_waste_items pwi ON pwi.submission_id = pws.id
WHERE pws.store_id = 1  -- Replace with your store_id
ORDER BY pws.submitted_at DESC, pwi.product_name
LIMIT 50;

-- 2. Check what's in daily_throwaway (this is what dashboard reads)
SELECT 
    dt.id,
    dt.store_id,
    dt.product_id,
    p.product_name,
    dt.date,
    dt.waste,
    dt.produced,
    dt.source,
    dt.created_at
FROM daily_throwaway dt
JOIN products p ON p.product_id = dt.product_id
WHERE dt.store_id = 1  -- Replace with your store_id
  AND dt.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY dt.date DESC, p.product_name;

-- 3. Check if there's a uniqueness issue (duplicates)
SELECT 
    store_id,
    product_id,
    date,
    COUNT(*) as duplicate_count
FROM daily_throwaway
WHERE store_id = 1  -- Replace with your store_id
GROUP BY store_id, product_id, date
HAVING COUNT(*) > 1;

-- 4. Check most recent approval/edit activity
SELECT 
    pws.id,
    pws.store_id,
    pws.status,
    pws.submission_date,
    pws.reviewed_at,
    COUNT(pwi.id) as item_count
FROM pending_waste_submissions pws
LEFT JOIN pending_waste_items pwi ON pwi.submission_id = pws.id
WHERE pws.store_id = 1  -- Replace with your store_id
  AND pws.status IN ('approved', 'edited')
  AND pws.reviewed_at >= NOW() - INTERVAL '24 hours'
GROUP BY pws.id
ORDER BY pws.reviewed_at DESC;
