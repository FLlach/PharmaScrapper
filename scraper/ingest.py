import json
import re
import os
from datetime import datetime
from unidecode import unidecode
from thefuzz import fuzz
from thefuzz import process
import psycopg2
from psycopg2.extras import RealDictCursor
from db import get_connection

MATCH_THRESHOLD = 92

def sanitize_price(val):
    if val is None:
        return None
    try:
        num = int(val)
        if num < 0 or num > 2147483647:
            return None
        return num
    except (ValueError, TypeError):
        return None

def normalize_text(text):
    if not text:
        return ""
    text = unidecode(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_or_create_pharmacy(conn, pharmacy_name):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id FROM pharmacies WHERE name = %s LIMIT 1", (pharmacy_name,))
        res = cur.fetchone()
        if res:
            return res['id']

        cur.execute("""
            INSERT INTO pharmacies (name, active, created_at, updated_at)
            VALUES (%s, true, NOW(), NOW())
            RETURNING id
        """, (pharmacy_name,))
        pharm_id = cur.fetchone()['id']
        conn.commit()
        return pharm_id

def load_medicines_cache(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, active_ingredient, presentation, normalized_name, normalized_active_ingredient
            FROM medicines
        """)
        return cur.fetchall()

def find_medicine_match(medicines_cache, norm_name, norm_active_ingredient, presentation):
    if not medicines_cache:
        return None

    for med in medicines_cache:
        m_norm_name = med.get('normalized_name') or normalize_text(med.get('name', ''))
        m_norm_ai = med.get('normalized_active_ingredient') or normalize_text(med.get('active_ingredient', ''))
        m_pres = med.get('presentation', '') or ''

        if m_norm_name == norm_name and m_norm_ai == norm_active_ingredient and m_pres == presentation:
            return med['id']

    best_match = None
    highest_score = 0

    for med in medicines_cache:
        m_norm_name = med.get('normalized_name') or normalize_text(med.get('name', ''))
        m_norm_ai = med.get('normalized_active_ingredient') or normalize_text(med.get('active_ingredient', ''))

        score_name = fuzz.token_sort_ratio(norm_name, m_norm_name)

        score_ai = 100
        if norm_active_ingredient and m_norm_ai:
            score_ai = fuzz.token_sort_ratio(norm_active_ingredient, m_norm_ai)
        elif norm_active_ingredient or m_norm_ai:
            score_ai = 50

        total_score = (score_name * 0.7) + (score_ai * 0.3)

        if total_score > highest_score:
            highest_score = total_score
            best_match = med['id']

    if highest_score >= MATCH_THRESHOLD:
        return best_match

    return None

def get_or_create_medicine(conn, medicines_cache, product):
    prod_name = (product.get('name') or '').strip()
    if not prod_name:
        return None

    norm_name = normalize_text(prod_name)
    norm_active_ingredient = normalize_text(product.get('active_ingredient', ''))
    presentation = product.get('presentation', '') or ''
    dosage = product.get('dosage')
    bioequivalent = bool(product.get('bioequivalent'))

    med_id = find_medicine_match(medicines_cache, norm_name, norm_active_ingredient, presentation)
    if med_id:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM medicines WHERE id = %s LIMIT 1", (med_id,))
            if cur.fetchone():
                return med_id
        medicines_cache[:] = [m for m in medicines_cache if m['id'] != med_id]

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, active_ingredient, presentation, normalized_name, normalized_active_ingredient
            FROM medicines
            WHERE name = %s
            LIMIT 1
        """, (prod_name,))
        existing = cur.fetchone()
        if existing:
            medicines_cache.append(existing)
            return existing['id']

        cur.execute("""
            INSERT INTO medicines (
                name, active_ingredient, dosage, presentation,
                normalized_name, normalized_active_ingredient, bioequivalent,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id, name, active_ingredient, presentation, normalized_name, normalized_active_ingredient
        """, (
            prod_name,
            product.get('active_ingredient', ''),
            dosage,
            presentation,
            norm_name,
            norm_active_ingredient,
            bioequivalent
        ))
        new_med = cur.fetchone()
        medicines_cache.append(new_med)
        return new_med['id']

def get_or_create_pharmacy_product(conn, pharmacy_id, pharmacy_name, medicine_id, product):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id FROM pharmacies WHERE id = %s LIMIT 1", (pharmacy_id,))
        if not cur.fetchone():
            pharmacy_id = get_or_create_pharmacy(conn, pharmacy_name)

        prod_url = product.get('product_url') or product.get('url') or ''
        image_url = product.get('image_url')
        sku = str(product['sku'])

        cur.execute("""
            SELECT id FROM pharmacy_products
            WHERE pharmacy_id = %s AND sku = %s
            LIMIT 1
        """, (pharmacy_id, sku))
        res = cur.fetchone()

        if res:
            cur.execute("""
                UPDATE pharmacy_products
                SET medicine_id = COALESCE(medicine_id, %s),
                    updated_at = NOW()
                WHERE id = %s
            """, (medicine_id, res['id']))
            return res['id']

        cur.execute("""
            INSERT INTO pharmacy_products (
                pharmacy_id, medicine_id, sku, name, brand,
                product_url, url, image_url, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            pharmacy_id,
            medicine_id,
            sku,
            product['name'],
            product.get('brand', ''),
            prod_url,
            prod_url,
            image_url
        ))
        return cur.fetchone()['id']

def process_price_history(conn, pharmacy_product_id, product, scraped_at):
    reg_price = sanitize_price(product.get('price_regular'))
    off_price = sanitize_price(product.get('price_offer'))
    in_stock = bool(product.get('in_stock', True))

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT price_regular, price_offer, in_stock
            FROM price_histories
            WHERE pharmacy_product_id = %s
            ORDER BY captured_at DESC
            LIMIT 1
        """, (pharmacy_product_id,))
        latest = cur.fetchone()

        if not latest or \
           latest['price_regular'] != reg_price or \
           latest['price_offer'] != off_price or \
           latest['in_stock'] != in_stock:

           cur.execute("""
               INSERT INTO price_histories (
                   pharmacy_product_id, price_regular, price_offer,
                   in_stock, captured_at, created_at, updated_at
               )
               VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
           """, (
               pharmacy_product_id,
               reg_price,
               off_price,
               in_stock,
               scraped_at
           ))

def process_batch(filepath):
    print(f"Processing batch: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pharmacy_name = data['pharmacy_name']
    scraped_at = data['scraped_at']
    products = data['products']

    print(f"Found {len(products)} products from {pharmacy_name}")

    conn = get_connection()
    try:
        pharmacy_id = get_or_create_pharmacy(conn, pharmacy_name)
        medicines_cache = load_medicines_cache(conn)

        for i, prod in enumerate(products):
            with conn.cursor() as sp_cur:
                sp_cur.execute("SAVEPOINT item_sp;")
            try:
                med_id = get_or_create_medicine(conn, medicines_cache, prod)
                if med_id:
                    pp_id = get_or_create_pharmacy_product(conn, pharmacy_id, pharmacy_name, med_id, prod)
                    process_price_history(conn, pp_id, prod, scraped_at)
                with conn.cursor() as sp_cur:
                    sp_cur.execute("RELEASE SAVEPOINT item_sp;")

                if (i+1) % 100 == 0:
                    print(f"Processed {i+1}/{len(products)}...")
                    conn.commit()
            except Exception as item_err:
                with conn.cursor() as sp_cur:
                    sp_cur.execute("ROLLBACK TO SAVEPOINT item_sp;")
                print(f"Warning: skipped product {prod.get('sku')} due to error: {item_err}")

        conn.commit()
        print(f"Batch processing complete for {filepath}.")
    except Exception as e:
        conn.rollback()
        print(f"Error processing batch {filepath}: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    from db import init_db
    init_db()

    for f in os.listdir('.'):
        if f.endswith('_products.json'):
            process_batch(f)
