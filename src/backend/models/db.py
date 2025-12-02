def seed_default_products():
    cursor = mysql.connection.cursor()

    # Run seed file
    with open('backend/models/seed_products.sql') as f:
        sql = f.read()
        cursor.execute(sql)
        mysql.connection.commit()
