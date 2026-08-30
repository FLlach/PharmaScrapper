import json
import argparse
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from schema import PharmacyProduct, PharmacyProductBatch

def map_dr_simi_product(raw_item):
    """Map a raw VTEX product JSON to the standard PharmacyProduct schema."""

    sku = str(raw_item.get("productId", ""))
    name = raw_item.get("productTitle") or raw_item.get("productName", "")
    brand = raw_item.get("brand", "Desconocido")

    # Extract properties
    properties = raw_item.get("allSpecifications", [])
    bioequivalent = False
    if "Tipo de Producto" in properties and raw_item.get("Tipo de Producto"):
        if any("BIOEQUIVALENTE" in str(val).upper() for val in raw_item["Tipo de Producto"]):
            bioequivalent = True

    active_ingredient = None
    if "Principio Activo" in properties and raw_item.get("Principio Activo"):
        active_ingredient = ", ".join(raw_item["Principio Activo"])

    prescription_required = False
    if "Condición de Venta" in properties and raw_item.get("Condición de Venta"):
        if any("RECETA" in str(val).upper() for val in raw_item["Condición de Venta"]):
            prescription_required = True

    presentation = None
    if "Forma farmacéutica" in properties and raw_item.get("Forma farmacéutica"):
        presentation = ", ".join(raw_item["Forma farmacéutica"])

    unit_price_desc = None
    if "Precio unitario" in properties and raw_item.get("Precio unitario"):
        unit_price_desc = ", ".join(raw_item["Precio unitario"])

    # Extract price and stock from first SKU / Item
    items = raw_item.get("items", [])
    price_regular = 0
    price_offer = None
    in_stock = False
    image_url = None

    if items:
        first_item = items[0]
        sellers = first_item.get("sellers", [])

        if sellers:
            offer = sellers[0].get("commertialOffer", {})
            price_regular = int(offer.get("ListPrice", 0))
            price_offer = int(offer.get("Price", 0))
            if price_offer == price_regular:
                price_offer = None

            stock = offer.get("AvailableQuantity", 0)
            in_stock = stock > 0

        images = first_item.get("images", [])
        if images:
            image_url = images[0].get("imageUrl")

    # Sometimes products might not have a proper link, fallback to base URL if missing
    product_url = raw_item.get("link", "")
    if not product_url and "linkText" in raw_item:
        product_url = f"https://www.drsimi.cl/{raw_item['linkText']}/p"

    category = None
    categories = raw_item.get("categories", [])
    if categories:
        category = categories[0].strip("/")

    product = PharmacyProduct(
        sku=sku,
        name=name,
        active_ingredient=active_ingredient,
        presentation=presentation,
        brand=brand,
        bioequivalent=bioequivalent,
        prescription_required=prescription_required,
        price_regular=price_regular,
        price_offer=price_offer,
        unit_price_description=unit_price_desc,
        currency="CLP",
        in_stock=in_stock,
        image_url=image_url,
        product_url=product_url,
        category=category
    )
    return product

def scrape_dr_simi(output_file="dr_simi_products.json", max_pages=None):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # We can scrape via pagination using the VTEX search API
        page_size = 50
        start_idx = 0
        page_num = 1

        while True:
            if max_pages and page_num > max_pages:
                break

            end_idx = start_idx + page_size - 1
            url = f"https://www.drsimi.cl/api/catalog_system/pub/products/search/medicamentos?_from={start_idx}&_to={end_idx}"
            print(f"Fetching page {page_num} (items {start_idx}-{end_idx})...")

            try:
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(2000) # Give it some time to load

                body = page.evaluate("document.body.innerText")
                data = json.loads(body)

                if not data or not isinstance(data, list) or len(data) == 0:
                    print("No more products found or invalid response.")
                    break

                results.extend(data)
                print(f"Added {len(data)} products. Total collected: {len(results)}")

                if len(data) < page_size:
                    # Last page
                    break

                start_idx += page_size
                page_num += 1

                # Small delay to respect rate limits
                time.sleep(1)

            except Exception as e:
                print(f"Error on page {page_num}: {e}")
                break

        browser.close()

    print(f"Finished scraping. Deduplicating {len(results)} raw items...")

    unique_items = {}
    for item in results:
        if "productId" in item:
            unique_items[item["productId"]] = item

    print(f"Captured {len(unique_items)} unique products.")

    products = []
    for item in unique_items.values():
        try:
            parsed = map_dr_simi_product(item)
            products.append(parsed)
        except Exception as e:
            print(f"Error parsing item {item.get('productId')}: {e}")

    batch = PharmacyProductBatch(
        scraped_at=datetime.now(timezone.utc),
        pharmacy_name="Dr. Simi",
        source_url="https://www.drsimi.cl/medicamentos",
        items_count=len(products),
        products=products
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Successfully mapped and saved {len(products)} products to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Dr. Simi products.")
    parser.add_argument("--output", default="dr_simi_products.json", help="Output JSON file name")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum number of pages to scrape (for testing)")
    args = parser.parse_args()

    scrape_dr_simi(args.output, args.max_pages)
