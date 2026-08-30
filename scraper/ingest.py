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

MATCH_THRESHOLD = 85

def normalize_text(text):
    if not text:
        return ""
    # Remove accents/diacritics
    text = unidecode(text)
    # Convert to lowercase
    text = text.lower()
    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_or_create_pharmacy(conn, pharmacy_name):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id FROM pharmacies WHERE name = %s", (pharmacy_name,))
        res = cur.fetchone()
        if res:
            return res['id']

        cur.execute("INSERT INTO pharmacies (name) VALUES (%s) RETURNING id", (pharmacy_name,))
        return cur.fetchone()['id']

def load_medicines_cache(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, normalized_name, normalized_active_ingredient, presentation
            FROM medicines
        """)
        return cur.fetchall()

def find_medicine_match(medicines_cache, norm_name, norm_active_ingredient, presentation):
    if not medicines_cache:
        return None

    # Try exact match first
    for med in medicines_cache:
        if med['normalized_name'] == norm_name and \
           med['normalized_active_ingredient'] == norm_active_ingredient and \
           med['presentation'] == presentation:
            return med['id']

    # Try fuzzy matching
    best_match = None
    highest_score = 0

    for med in medicines_cache:
        # We match primarily on name and active ingredient
        score_name = fuzz.token_sort_ratio(norm_name, med['normalized_name'])

        score_ai = 100
        if norm_active_ingredient and med['normalized_active_ingredient']:
            score_ai = fuzz.token_sort_ratio(norm_active_ingredient, med['normalized_active_ingredient'])
        elif norm_active_ingredient or med['normalized_active_ingredient']:
            score_ai = 50 # Partial mismatch

        # Calculate a weighted score
        total_score = (score_name * 0.7) + (score_ai * 0.3)

        if total_score > highest_score:
            highest_score = total_score
            best_match = med['id']

    if highest_score >= MATCH_THRESHOLD:
        return best_match

    return None

def get_or_create_medicine(conn, medicines_cache, product):
    norm_name = normalize_text(product['name'])
    norm_active_ingredient = normalize_text(product.get('active_ingredient', ''))
    presentation = product.get('presentation', '')

    med_id = find_medicine_match(medicines_cache, norm_name, norm_active_ingredient, presentation)
    if med_id:
        return med_id

    # Create new
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            cur.execute("""
                INSERT INTO medicines (name, active_ingredient, presentation, normalized_name, normalized_active_ingredient)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, normalized_name, normalized_active_ingredient, presentation
            """, (
                product['name'],
                product.get('active_ingredient', ''),
                presentation,
                norm_name,
                norm_active_ingredient
            ))
            new_med = cur.fetchone()
            medicines_cache.append(new_med)
            return new_med['id']
        except psycopg2.IntegrityError:
            conn.rollback()
            # If concurrent insert happened, fetch it
            cur.execute("""
                SELECT id, normalized_name, normalized_active_ingredient, presentation
                FROM medicines
                WHERE normalized_name = %s AND normalized_active_ingredient = %s AND presentation = %s
            """, (norm_name, norm_active_ingredient, presentation))
            res = cur.fetchone()
            if res:
                medicines_cache.append(res)
                return res['id']
            return None

def get_or_create_pharmacy_product(conn, pharmacy_id, medicine_id, product):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id FROM pharmacy_products
            WHERE pharmacy_id = %s AND sku = %s
        """, (pharmacy_id, product['sku']))
        res = cur.fetchone()

        if res:
            return res['id']

        cur.execute("""
            INSERT INTO pharmacy_products (pharmacy_id, medicine_id, sku, name, brand, product_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            pharmacy_id,
            medicine_id,
            product['sku'],
            product['name'],
            product.get('brand', ''),
            product['product_url']
        ))
        return cur.fetchone()['id']

def process_price_history(conn, pharmacy_product_id, product, scraped_at):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get most recent price history
        cur.execute("""
            SELECT price_regular, price_offer, in_stock
            FROM price_histories
            WHERE pharmacy_product_id = %s
            ORDER BY captured_at DESC
            LIMIT 1
        """, (pharmacy_product_id,))
        latest = cur.fetchone()

        # If it changed or it's the first one, insert
        if not latest or \
           latest['price_regular'] != product['price_regular'] or \
           latest['price_offer'] != product.get('price_offer') or \
           latest['in_stock'] != product['in_stock']:

           cur.execute("""
               INSERT INTO price_histories (pharmacy_product_id, price_regular, price_offer, in_stock, captured_at)
               VALUES (%s, %s, %s, %s, %s)
           """, (
               pharmacy_product_id,
               product['price_regular'],
               product.get('price_offer'),
               product['in_stock'],
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
            med_id = get_or_create_medicine(conn, medicines_cache, prod)
            pp_id = get_or_create_pharmacy_product(conn, pharmacy_id, med_id, prod)
            process_price_history(conn, pp_id, prod, scraped_at)

            if (i+1) % 100 == 0:
                print(f"Processed {i+1}/{len(products)}...")
                conn.commit()

        conn.commit()
        print("Batch processing complete.")
    except Exception as e:
        conn.rollback()
        print(f"Error processing batch: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # Find all json files in scraper dir ending with _products.json
    for f in os.listdir('.'):
        if f.endswith('_products.json'):
            process_batch(f)
