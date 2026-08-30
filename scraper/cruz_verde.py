import json
import argparse
import time
from datetime import datetime, timezone
import requests
from schema import PharmacyProduct, PharmacyProductBatch

def map_cruz_verde_product(raw_item):
    prices = raw_item.get("prices", {})
    price_regular = int(prices.get("price-list-cl", raw_item.get("mrp", 0)))
    price_offer = prices.get("price-sale-cl")
    if price_offer is not None:
        price_offer = int(price_offer)
    if price_offer == price_regular:
        price_offer = None

    image_url = raw_item.get("imageUrl")
    if not image_url and raw_item.get("images") and len(raw_item["images"]) > 0:
        image_url = raw_item["images"][0].get("link")

    product = PharmacyProduct(
        sku=str(raw_item.get("productId", "")),
        name=raw_item.get("productName") or raw_item.get("productTitle", ""),
        brand=raw_item.get("brand", "Desconocido") or raw_item.get("productBrand", "Desconocido"),
        bioequivalent=bool(raw_item.get("isBioequivalent", False)),
        price_regular=price_regular,
        price_offer=price_offer,
        unit_price_description=raw_item.get("pum"),
        currency="CLP",
        in_stock=raw_item.get("stock", 0) > 0,
        image_url=image_url,
        product_url=raw_item.get("pdpUrl", ""),
        category=raw_item.get("request_category_id")
    )
    return product

def scrape_cruz_verde(output_file="cruz_verde_products.json"):
    results = []
    unique_items = {}

    categories = [
        "medicamentos",
        "dermocosmetica",
        "cuidado-de-la-piel",
        "belleza",
        "higiene-y-cuidado-personal",
        "cuidado-capilar",
        "vitaminas-y-suplementos",
        "infantil-y-mama",
        "bienestar-sexual",
        "veterinaria",
    ]

    from playwright.sync_api import sync_playwright

    auth_headers = {}
    auth_cookies = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        def on_req(req):
            nonlocal auth_headers
            if "product-service/products/search" in req.url:
                auth_headers = req.headers
                auth_headers.pop("accept-encoding", None)

        page.on("request", on_req)
        page.goto("https://www.cruzverde.cl/medicamentos/", wait_until="networkidle")

        for cookie in context.cookies():
            auth_cookies[cookie["name"]] = cookie["value"]

        browser.close()

    print("Obtained valid headers and cookies via Playwright. Switching to requests for iteration...")

    for category in categories:
        print(f"\nScraping category: {category}")
        offset = 0
        limit = 50
        max_retries = 3

        while True:
            url = f"https://api.cruzverde.cl/product-service/products/search?limit={limit}&offset={offset}&refine[]=cgid={category}&isAndes=true&requestPage=CLP"

            success = False
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=auth_headers, cookies=auth_cookies, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        hits = data.get("hits", [])

                        if not hits:
                            print(f"No more items found at offset {offset}. Finishing category.")
                            success = True
                            break

                        print(f"Fetched {len(hits)} items (offset: {offset})")
                        for item in hits:
                            if "productId" in item:
                                unique_items[item["productId"]] = item

                        offset += limit
                        success = True
                        break
                    else:
                        print(f"Request failed with status {response.status_code}. Retrying ({attempt+1}/{max_retries})...")
                        time.sleep(2)
                except Exception as e:
                    print(f"Request error: {e}. Retrying ({attempt+1}/{max_retries})...")
                    time.sleep(2)

            if not success or not hits:
                break

            time.sleep(0.5)

    print(f"\nCaptured {len(unique_items)} unique products across all categories.")

    products = []
    for item in unique_items.values():
        try:
            parsed = map_cruz_verde_product(item)
            products.append(parsed)
        except Exception as e:
            print(f"Error parsing item {item.get('productId')}: {e}")

    batch = PharmacyProductBatch(
        scraped_at=datetime.now(timezone.utc),
        pharmacy_name="Cruz Verde",
        source_url="https://www.cruzverde.cl/",
        items_count=len(products),
        products=products
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Successfully mapped and saved {len(products)} products to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Cruz Verde full catalog.")
    parser.add_argument("--output", default="cruz_verde_products.json", help="Output JSON file name")
    args = parser.parse_args()

    scrape_cruz_verde(args.output)
