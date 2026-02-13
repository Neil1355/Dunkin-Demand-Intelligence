# Database Schema & Management

Complete database documentation for Dunkin Demand Intelligence.

---

## Table of Contents

- [Schema Overview](#schema-overview)
- [Table Definitions](#table-definitions)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Backup & Restore](#backup--restore)
- [Query Examples](#query-examples)
- [Optimization Tips](#optimization-tips)

---

## Schema Overview

The database uses PostgreSQL with 7 main tables:

1. **users** - User accounts & authentication
2. **daily_sales** - Product sales records
3. **forecasts** - AI-generated sales predictions
4. **daily_waste** - Product waste/throwaway tracking
5. **password_reset_tokens** - Secure password reset
6. **products** - Product catalog
7. **audit_logs** - User action logging (optional)

---

## Table Definitions

### Users Table
Stores user account information.

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
```

**Columns:**
- `id`: Unique user identifier
- `name`: User's full name
- `email`: User's email (must be unique)
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update

---

### Daily Sales Table
Records individual product sales.

```sql
CREATE TABLE daily_sales (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  product_name VARCHAR(255) NOT NULL,
  quantity_sold INTEGER NOT NULL,
  revenue DECIMAL(10, 2),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_daily_sales_user_id ON daily_sales(user_id);
CREATE INDEX idx_daily_sales_date ON daily_sales(date);
CREATE INDEX idx_daily_sales_product ON daily_sales(product_name);
```

**Columns:**
- `id`: Record ID
- `user_id`: Which user recorded this
- `date`: Sales date (YYYY-MM-DD)
- `product_name`: Product sold
- `quantity_sold`: Units sold
- `revenue`: Total sales amount
- `notes`: Optional notes

---

### Forecasts Table
Stores AI-generated predictions.

```sql
CREATE TABLE forecasts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  forecast_date DATE NOT NULL,
  product_name VARCHAR(255) NOT NULL,
  predicted_demand INTEGER,
  confidence DECIMAL(4, 3),
  lower_bound INTEGER,
  upper_bound INTEGER,
  actual_demand INTEGER,
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_forecasts_user_id ON forecasts(user_id);
CREATE INDEX idx_forecasts_date ON forecasts(forecast_date);
CREATE INDEX idx_forecasts_status ON forecasts(status);
```

**Columns:**
- `id`: Record ID
- `user_id`: Which user generated forecast
- `forecast_date`: Predicted date
- `product_name`: Product being forecasted
- `predicted_demand`: AI prediction (units)
- `confidence`: Confidence score (0.0-1.0)
- `lower_bound`: Conservative estimate
- `upper_bound`: Optimistic estimate
- `actual_demand`: Actual sales (once recorded)
- `status`: "pending", "approved", "rejected"

---

### Daily Waste Table
Tracks product waste and spoilage.

```sql
CREATE TABLE daily_waste (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  product_name VARCHAR(255) NOT NULL,
  quantity_wasted INTEGER NOT NULL,
  reason VARCHAR(255),
  cost DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_daily_waste_user_id ON daily_waste(user_id);
CREATE INDEX idx_daily_waste_date ON daily_waste(date);
CREATE INDEX idx_daily_waste_reason ON daily_waste(reason);
```

**Columns:**
- `id`: Record ID
- `user_id`: Which user recorded waste
- `date`: Waste date
- `product_name`: Product wasted
- `quantity_wasted`: Units wasted
- `reason`: Why wasted (e.g., "End of day", "Damaged", "Expired")
- `cost`: Loss amount

---

### Password Reset Tokens Table
Secure password reset mechanism.

```sql
CREATE TABLE password_reset_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token TEXT NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  used_at TIMESTAMP DEFAULT NULL
);

-- Indexes
CREATE INDEX idx_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);
```

**Columns:**
- `id`: Token record ID
- `user_id`: Which user requested reset
- `token`: Cryptographically random token
- `expires_at`: When token expires (1 hour)
- `created_at`: Token generation time
- `used_at`: When token was used (NULL if unused)

---

### Products Table
Product catalog (optional for product lookup).

```sql
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  category VARCHAR(100),
  unit_cost DECIMAL(10, 2),
  unit_price DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_products_name ON products(name);
```

**Columns:**
- `id`: Product ID
- `name`: Product name (e.g., "Glazed Donut")
- `category`: Product type (e.g., "Donuts")
- `unit_cost`: Cost per unit
- `unit_price`: Selling price per unit

---

### Audit Logs Table (Optional)
Track user actions for compliance.

```sql
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(255) NOT NULL,
  details JSONB,
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

**Columns:**
- `id`: Log entry ID
- `user_id`: Which user performed action
- `action`: Action type (e.g., "LOGIN", "PASSWORD_RESET")
- `details`: Action details (JSON)
- `ip_address`: User's IP address
- `user_agent`: Browser/client info

---

## Relationships

```
┌──────────┐
│  users   │
└────┬─────┘
     │
     ├──────────┬─────────────┬──────────────┬──────────────┬────────────────┐
     │          │             │              │              │                │
     ▼          ▼             ▼              ▼              ▼                ▼
┌─────────────┐ ┌──────────────┐ ┌───────────┐ ┌──────────────┐ ┌─────────────────┐
│ daily_sales │ │ daily_waste  │ │ forecasts │ │ audit_logs   │ │ password_reset  │
│  (sales)    │ │   (waste)    │ │  (AI)     │ │  (logging)   │ │(authentication) │
└─────────────┘ └──────────────┘ └───────────┘ └──────────────┘ └─────────────────┘
```

All tables relate to `users` via `user_id` foreign key.

---

## Indexes

Created for performance optimization:

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);

-- Sales data queries
CREATE INDEX idx_daily_sales_user_id ON daily_sales(user_id);
CREATE INDEX idx_daily_sales_date ON daily_sales(date);
CREATE INDEX idx_daily_sales_product ON daily_sales(product_name);

-- Forecast queries
CREATE INDEX idx_forecasts_user_id ON forecasts(user_id);
CREATE INDEX idx_forecasts_date ON forecasts(forecast_date);
CREATE INDEX idx_forecasts_status ON forecasts(status);

-- Waste queries
CREATE INDEX idx_daily_waste_user_id ON daily_waste(user_id);
CREATE INDEX idx_daily_waste_date ON daily_waste(date);

-- Password reset
CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);

-- Audit logging
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

### View Existing Indexes
```sql
SELECT * FROM pg_indexes WHERE schemaname = 'public';
```

### Check Index Performance
```sql
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Backup & Restore

### Full Database Backup

```bash
# Binary backup (recommended)
pg_dump -Fc dunkin_demand > backup.dump

# SQL text backup
pg_dump dunkin_demand > backup.sql
```

### Backup Specific Table

```bash
pg_dump -t daily_sales dunkin_demand > sales_backup.dump
```

### Restore Full Backup

```bash
# From binary backup
pg_restore -d dunkin_demand backup.dump

# From SQL backup
psql dunkin_demand < backup.sql
```

### Restore Table

```bash
pg_restore -d dunkin_demand -t daily_sales sales_backup.dump
```

### Automated Backups

**Supabase:** Automatic daily backups (Settings → Backups)
**Railway:** Built-in backup service (check Settings → Backups)

---

## Query Examples

### User Analytics

```sql
-- Most active users (by sales records)
SELECT u.id, u.name, COUNT(*) as sales_count
FROM users u
JOIN daily_sales ds ON u.id = ds.user_id
GROUP BY u.id, u.name
ORDER BY sales_count DESC
LIMIT 10;
```

### Sales Trends

```sql
-- Total sales by date
SELECT date, SUM(revenue) as daily_revenue
FROM daily_sales
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date DESC;
```

### Forecast Accuracy

```sql
-- Compare predictions vs actual
SELECT 
  f.forecast_date,
  f.product_name,
  f.predicted_demand,
  f.actual_demand,
  ROUND(ABS(f.predicted_demand - f.actual_demand)::numeric / f.predicted_demand * 100, 2) as error_pct
FROM forecasts f
WHERE f.actual_demand IS NOT NULL
ORDER BY f.forecast_date DESC
LIMIT 20;
```

### Waste Analysis

```sql
-- Total waste by product
SELECT product_name, SUM(quantity_wasted) as total_wasted, SUM(cost) as total_cost
FROM daily_waste
WHERE date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY product_name
ORDER BY total_cost DESC;
```

### User Activity Audit

```sql
-- Recent user actions
SELECT user_id, action, details, created_at
FROM audit_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 50;
```

---

## Optimization Tips

### 1. Regular Maintenance

```sql
-- Vacuum and analyze (PostgreSQL optimization)
VACUUM ANALYZE;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. Archive Old Data

```sql
-- Archive sales older than 2 years
INSERT INTO daily_sales_archive
SELECT * FROM daily_sales
WHERE date < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM daily_sales
WHERE date < CURRENT_DATE - INTERVAL '2 years';
```

### 3. Query Performance

```sql
-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM daily_sales
WHERE date >= '2026-01-01' and user_id = 1;

-- Check slow queries
SELECT query, calls, mean_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;
```

### 4. Connection Pooling

Use PgBouncer for connection pooling:
```ini
# pgbouncer.ini
[databases]
dunkin_demand = host=localhost port=5432 dbname=dunkin_demand

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### 5. Replication & High Availability

For production, consider:
- **Supabase:** Built-in replicas included
- **AWS RDS:** Multi-AZ deployment
- **PostgreSQL Streaming Replication:** DIY option

---

## Common Tasks

### Add New Column

```sql
ALTER TABLE daily_sales
ADD COLUMN unit_price DECIMAL(10, 2);
```

### Rename Column

```sql
ALTER TABLE daily_sales
RENAME COLUMN revenue TO total_revenue;
```

### Change Column Type

```sql
ALTER TABLE daily_sales
ALTER COLUMN quantity_sold TYPE BIGINT;
```

### Create Composite Key

```sql
ALTER TABLE daily_sales
ADD CONSTRAINT unique_sale_per_day
UNIQUE (user_id, date, product_name);
```

### Check Constraint

```sql
ALTER TABLE daily_sales
ADD CONSTRAINT check_quantity_positive
CHECK (quantity_sold > 0);
```

---

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
psql --version

# Test connection
psql postgresql://user:password@localhost:5432/dunkin_demand

# Check listening port
netstat -an | grep 5432
```

### Disk Space Full

```sql
-- Check database size
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'dunkin_demand';

-- Remove old audit logs
DELETE FROM audit_logs
WHERE created_at < CURRENT_DATE - INTERVAL '6 months';

-- Vacuum to reclaim space
VACUUM FULL;
```

### Locks & Deadlocks

```sql
-- Find blocked queries
SELECT pid, usename, application_name, query
FROM pg_stat_activity
WHERE state = 'idle in transaction';

-- Kill blocking query
SELECT pg_terminate_backend(pid);
```

---

## Resources

- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)

---

**Last Updated:** February 13, 2026
