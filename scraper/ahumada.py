import requests
import json
import argparse
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from schema import PharmacyProduct, PharmacyProductBatch

def fetch_ahumada_page(start: int, sz: int = 1000):
    url = f"https://www.farmaciasahumada.cl/on/demandware.store/Sites-ahumada-cl-Site/default/Search-UpdateGrid?cgid=medicamentos&start={start}&sz={sz}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_price(text):
    if not text:
        return None
    val = re.sub(r'[^\d]', '', text)
    if not val:
        return None
    return int(val)

def clean_text(text):
    if not text:
        return None
    return " ".join(text.split())

def parse_product_tile(tile):
    pid = tile.get('data-pid')
    if not pid:
        return None

    img_tag = tile.select_one('.image-container img.tile-image')
    name = img_tag.get('title', '').strip(', ') if img_tag else None
    image_url = img_tag.get('src') if img_tag else None

    brand_elem = tile.select_one('.product-tile-brand')
    brand = clean_text(brand_elem.text) if brand_elem else "Desconocido"
    if not brand:
        brand = "Desconocido"

    url_elem = tile.select_one('.image-container a')
    url = url_elem.get('href') if url_elem else None
    if url and url.startswith('/'):
        url = 'https://www.farmaciasahumada.cl' + url
    elif not url:
        url = 'https://www.farmaciasahumada.cl'

    bio_badge = tile.select_one('.bioequivalent-badge')
    bioequivalent = bio_badge is not None

    rx_badge = tile.select_one('.sellcondition-badge')
    rx = rx_badge is not None

    price_elem = tile.select_one('.sales')
    price_val = None
    if price_elem:
        price_val_container = price_elem.select_one('.promotion-badge-container')
        if price_val_container:
            # We want the text content, strip out tags
            text_nodes = price_val_container.find_all(string=True, recursive=False)
            price_str = "".join(text_nodes).strip()
            price_val = parse_price(price_str)
        else:
            value_span = price_elem.select_one('.value')
            if value_span:
                val_content = value_span.get('content')
                price_val = parse_price(val_content) if val_content else parse_price(value_span.text.strip())

    old_price_elem = tile.select_one('.strike-through .value')
    old_price_val = None
    if old_price_elem:
        val_content = old_price_elem.get('content')
        old_price_val = parse_price(val_content) if val_content else parse_price(old_price_elem.text.strip())

    unit_price_elem = tile.select_one('.preccio-fracionado')
    unit_price_val = clean_text(unit_price_elem.text) if unit_price_elem else None

    # Logic for offer and regular price
    offer = None
    regular = 0
    if price_val and old_price_val:
        # price_val is offer, old_price_val is regular
        offer = price_val
        regular = old_price_val
    elif price_val and not old_price_val:
        regular = price_val
    elif not price_val and old_price_val:
        regular = old_price_val

    # Prevent issue with free products / no price
    if regular == 0 and offer is None:
        return None

    # Handle if they are the same
    if offer == regular:
        offer = None

    return PharmacyProduct(
        sku=str(pid),
        name=name or f"Producto {pid}",
        brand=brand,
        bioequivalent=bioequivalent,
        prescription_required=rx,
        price_regular=regular,
        price_offer=offer,
        unit_price_description=unit_price_val,
        currency="CLP",
        in_stock=True, # Displayed in the catalog implies stock
        image_url=image_url,
        product_url=url,
        category="Medicamentos"
    )

def scrape_ahumada(output_file="ahumada_products.json"):
    print("Iniciando scraper para Farmacias Ahumada...")
    all_products = {}

    start = 0
    sz = 1000

    while True:
        print(f"Obteniendo productos desde el offset {start}...")
        html = fetch_ahumada_page(start, sz)
        soup = BeautifulSoup(html, 'html.parser')
        tiles = soup.select('.product-tile')

        if not tiles:
            print("No se encontraron más productos.")
            break

        print(f"Encontrados {len(tiles)} productos en esta página.")

        for tile in tiles:
            try:
                product = parse_product_tile(tile)
                if product:
                    all_products[product.sku] = product
            except Exception as e:
                print(f"Error parseando producto: {e}")

        if len(tiles) < sz:
            # Last page
            break

        start += sz

    products_list = list(all_products.values())
    print(f"Total de productos únicos capturados: {len(products_list)}")

    batch = PharmacyProductBatch(
        scraped_at=datetime.now(timezone.utc),
        pharmacy_name="Farmacias Ahumada",
        source_url="https://www.farmaciasahumada.cl/medicamentos.html",
        items_count=len(products_list),
        products=products_list
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Se han guardado exitosamente {len(products_list)} productos en {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Farmacias Ahumada products.")
    parser.add_argument("--output", default="ahumada_products.json", help="Output JSON file name")
    args = parser.parse_args()

    scrape_ahumada(args.output)
