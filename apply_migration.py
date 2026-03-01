#!/usr/bin/env python3
"""
Script to apply the munchkin product name fix migration
"""
import sys
sys.path.insert(0, 'backend')

from models.db import get_connection, return_connection

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Read and execute the migration
    with open('backend/migrations/0012_fix_munchkin_product_names.sql', 'r') as f:
        migration_sql = f.read()
    
    # Execute the migration
    cur.execute(migration_sql)
    conn.commit()
    
    # Verify the changes
    cur.execute("""
        SELECT product_id, product_name, product_type 
        FROM products 
        WHERE product_type = 'munchkin' 
        ORDER BY product_name
    """)
    
    print("✅ Migration applied successfully!")
    print("\nUpdated munchkin products:")
    print("-" * 60)
    for row in cur.fetchall():
        if isinstance(row, dict):
            print(f"ID: {row['product_id']}, Name: {row['product_name']}")
        else:
            print(f"ID: {row[0]}, Name: {row[1]}")
    
    cur.close()
    return_connection(conn)
    
except Exception as e:
    print(f"❌ Error applying migration: {e}")
    sys.exit(1)
