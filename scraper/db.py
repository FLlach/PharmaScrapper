import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'backend_development'),
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

    # Ensure required columns exist on backend_development tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pharmacies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            base_domain VARCHAR(255),
            logo_url VARCHAR(255),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE pharmacies ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE;
        ALTER TABLE pharmacies ADD COLUMN IF NOT EXISTS base_domain VARCHAR(255);
        ALTER TABLE pharmacies ADD COLUMN IF NOT EXISTS logo_url VARCHAR(255);
        ALTER TABLE pharmacies ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE pharmacies ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            active_ingredient VARCHAR(255),
            dosage VARCHAR(255),
            presentation VARCHAR(255),
            normalized_name VARCHAR(255),
            normalized_active_ingredient VARCHAR(255),
            bioequivalent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS dosage VARCHAR(255);
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS presentation VARCHAR(255);
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS normalized_name VARCHAR(255);
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS normalized_active_ingredient VARCHAR(255);
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS bioequivalent BOOLEAN DEFAULT FALSE;
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE medicines ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS pharmacy_products (
            id SERIAL PRIMARY KEY,
            pharmacy_id INTEGER REFERENCES pharmacies(id),
            medicine_id INTEGER REFERENCES medicines(id),
            sku VARCHAR(100) NOT NULL,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(255),
            image_url VARCHAR(255),
            url TEXT,
            product_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS brand VARCHAR(255);
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS image_url VARCHAR(255);
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS url TEXT;
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS product_url TEXT;
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE pharmacy_products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS price_histories (
            id SERIAL PRIMARY KEY,
            pharmacy_product_id INTEGER REFERENCES pharmacy_products(id),
            price_regular INTEGER,
            price_offer INTEGER,
            in_stock BOOLEAN,
            captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ALTER TABLE price_histories ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE price_histories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    ''')

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
