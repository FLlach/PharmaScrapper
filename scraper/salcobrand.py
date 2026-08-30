import json
import argparse
import time
import requests
from datetime import datetime, timezone
from schema import PharmacyProduct, PharmacyProductBatch

def map_salcobrand_product(raw_item):
    # Parse prices
    price_regular = int(raw_item.get("normal_price", 0))
    price_offer = None

    if raw_item.get("direct_discount"):
        try:
            price_offer = int(float(raw_item.get("direct_discount")))
        except ValueError:
            pass

    if not price_offer and raw_item.get("ribbon_info") and raw_item["ribbon_info"].get("price"):
        price_str = raw_item["ribbon_info"]["price"]
        # Convert string like "$1.004" to integer 1004
        price_str = price_str.replace("$", "").replace(".", "").strip()
        try:
            price_offer = int(price_str)
        except ValueError:
            pass

    if price_offer == price_regular:
        price_offer = None

    bioequivalent = False
    if raw_item.get("bioequivalent_filter"):
        bioequivalent = bool(raw_item["bioequivalent_filter"].get("has_bioequivalent", False))

    category = None
    if raw_item.get("product_categories") and "lvl1" in raw_item["product_categories"]:
        cats = raw_item["product_categories"]["lvl1"]
        if cats and len(cats) > 0:
            category = cats[0]

    product_url = ""
    if raw_item.get("slug"):
        product_url = f"https://salcobrand.cl/t/medicamentos/{raw_item['slug']}"

    product = PharmacyProduct(
        sku=str(raw_item.get("sku", "")),
        name=raw_item.get("name", ""),
        brand=raw_item.get("brand", "Desconocido"),
        bioequivalent=bioequivalent,
        prescription_required=bool(raw_item.get("needs_recipe", False)),
        price_regular=price_regular,
        price_offer=price_offer,
        unit_price_description=raw_item.get("options_text"),
        currency="CLP",
        in_stock=bool(raw_item.get("has_stock", False)),
        image_url=raw_item.get("catalog_image_url"),
        product_url=product_url,
        category=category
    )
    return product

def scrape_salcobrand(output_file="salcobrand_products.json"):
    url = "https://gm3rp06hjg-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.3)%3B%20Browser%20(lite)&x-algolia-api-key=0259fe250b3be4b1326eb85e47aa7d81&x-algolia-application-id=GM3RP06HJG"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://salcobrand.cl",
        "Referer": "https://salcobrand.cl/"
    }

    current_time = int(time.time())
    hits_per_page = 1000
    page = 0
    total_pages = 1

    all_hits = []

    while page < total_pages:
        print(f"Fetching page {page} of {total_pages}...")
        payload = {
            "requests": [
                {
                    "indexName": "sb_variant_production",
                    "params": f"facetFilters=%5B%5B%22product_categories.lvl0%3AMedicamentos%22%5D%5D&filters=(timestamp_available_on%20%3C%20{current_time})&hitsPerPage={hits_per_page}&page={page}"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            hits = result.get("hits", [])
            all_hits.extend(hits)

            total_pages = result.get("nbPages", 1)

        page += 1
        time.sleep(1) # Be polite

    print(f"Captured {len(all_hits)} products from Algolia.")

    # Deduplicate by sku
    unique_items = {}
    for item in all_hits:
        if "sku" in item:
            unique_items[item["sku"]] = item

    products = []
    for item in unique_items.values():
        try:
            parsed = map_salcobrand_product(item)
            products.append(parsed)
        except Exception as e:
            print(f"Error parsing item {item.get('sku')}: {e}")

    batch = PharmacyProductBatch(
        scraped_at=datetime.now(timezone.utc),
        pharmacy_name="Salcobrand",
        source_url="https://salcobrand.cl/t/medicamentos",
        items_count=len(products),
        products=products
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Successfully mapped and saved {len(products)} products to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Salcobrand products.")
    parser.add_argument("--output", default="salcobrand_products.json", help="Output JSON file name")
    args = parser.parse_args()

    scrape_salcobrand(args.output)
