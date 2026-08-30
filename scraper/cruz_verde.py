import json
import argparse
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        def handle_response(response):
            if "product-service/products/search" in response.url and response.status == 200:
                try:
                    data = response.json()
                    if "hits" in data:
                        results.extend(data["hits"])
                except Exception:
                    pass

        page.on("response", handle_response)
        print("Navigating to Cruz Verde to trigger API calls...")
        page.goto("https://www.cruzverde.cl/medicamentos/", wait_until="networkidle")

        # Scroll down to ensure we trigger any initial loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2000)

        browser.close()

    # Deduplicate items by productId
    unique_items = {}
    for item in results:
        if "productId" in item:
            unique_items[item["productId"]] = item

    print(f"Captured {len(unique_items)} unique products.")

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
        source_url="https://www.cruzverde.cl/medicamentos/",
        items_count=len(products),
        products=products
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Successfully mapped and saved {len(products)} products to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Cruz Verde products.")
    parser.add_argument("--output", default="cruz_verde_products.json", help="Output JSON file name")
    args = parser.parse_args()

    scrape_cruz_verde(args.output)
