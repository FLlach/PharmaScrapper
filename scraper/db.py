import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'pharma_scraper'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Contr4sen4'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pharmacies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            active_ingredient VARCHAR(255),
            presentation VARCHAR(255),
            normalized_name VARCHAR(255) NOT NULL,
            normalized_active_ingredient VARCHAR(255),
            UNIQUE (normalized_name, normalized_active_ingredient, presentation)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS pharmacy_products (
            id SERIAL PRIMARY KEY,
            pharmacy_id INTEGER REFERENCES pharmacies(id),
            medicine_id INTEGER REFERENCES medicines(id),
            sku VARCHAR(100) NOT NULL,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(255),
            product_url TEXT,
            UNIQUE (pharmacy_id, sku)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS price_histories (
            id SERIAL PRIMARY KEY,
            pharmacy_product_id INTEGER REFERENCES pharmacy_products(id),
            price_regular INTEGER,
            price_offer INTEGER,
            in_stock BOOLEAN,
            captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
