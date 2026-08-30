import json
import argparse
import time
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from schema import PharmacyProduct, PharmacyProductBatch

def clean_price(price_str):
    if not price_str:
        return 0
    # Remove $ and dots, convert to int
    cleaned = ''.join(c for c in price_str if c.isdigit())
    return int(cleaned) if cleaned else 0

def extract_products_from_page(page):
    return page.evaluate('''() => {
        const items = [];
        document.querySelectorAll('h2.p-nombre-med').forEach(titleEl => {
            const linkEl = titleEl.closest('a');
            const url = linkEl ? linkEl.href : '';
            const name = titleEl.innerText;

            const container = titleEl.closest('.col-xl-4, .product-wrap, div[class*="col-xl"]') || titleEl.parentElement.parentElement;
            if (!container) return;

            const activeIngredientEl = container.querySelector('.p-laboratorio');
            const activeIngredient = activeIngredientEl ? activeIngredientEl.innerText : '';

            const priceEl = container.querySelector('.p-precio-producto');
            const price = priceEl ? priceEl.innerText : '';

            const imgEl = container.querySelector('img');
            const imageUrl = imgEl ? imgEl.src : '';

            let prescription = false;
            if (container.innerText.includes('Receta Medica')) prescription = true;

            items.push({name, activeIngredient, price, url, imageUrl, prescription});
        });
        return items;
    }''')

def map_ligafarmacia_product(raw_item):
    price_regular = clean_price(raw_item.get("price"))

    # Try to extract sku from URL if possible
    # https://ligafarmacia.cl/product/003180030-ac-valproico-200-mg
    sku = ""
    url = raw_item.get("url", "")
    if "product/" in url:
        part = url.split("product/")[-1]
        sku = part.split("-")[0] if "-" in part else part

    if not sku:
        sku = raw_item.get("name", "").strip()

    name = raw_item.get("name", "").strip()
    presentation = None

    # Extract presentation from name, e.g. "Ac. Valproico 200 Mg (30 Comprimidos)"
    match = re.search(r'\((.*?)\)$', name)
    if match:
        presentation = match.group(1).title()
        # Remove the presentation part from the name
        name = name[:match.start()].strip()

    active_ingredient = raw_item.get("activeIngredient", "").strip()
    # capitalize words properly
    active_ingredient = active_ingredient.title() if active_ingredient else None

    # Liga farmacia is mostly generics and epilepsy meds, bioequivalent not explicitly marked usually, default to False
    product = PharmacyProduct(
        sku=sku,
        name=name.title(),
        brand="Liga Chilena de la Epilepsia", # The pharmacy acts as the brand for their imports often or doesn't show it easily
        active_ingredient=active_ingredient,
        presentation=presentation,
        bioequivalent=False,
        prescription_required=raw_item.get("prescription", False),
        price_regular=price_regular,
        price_offer=None,
        currency="CLP",
        in_stock=True, # Listed items are usually in stock
        image_url=raw_item.get("imageUrl") or None,
        product_url=url,
    )
    return product

def scrape_ligafarmacia(output_file="ligafarmacia_products.json", max_pages=None):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        print("Navigating to Liga Farmacia...")
        try:
            page.goto("https://www.ligafarmacia.cl/medicamentos", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Error navigating: {e}")
            browser.close()
            return

        # Get total pages
        total_pages = page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a.page-link'));
            let maxPage = 1;
            links.forEach(l => {
                const num = parseInt(l.innerText.trim(), 10);
                if (!isNaN(num) && num > maxPage) {
                    maxPage = num;
                }
            });
            return maxPage;
        }''')

        print(f"Found {total_pages} pages to scrape.")

        if max_pages and max_pages < total_pages:
            total_pages = max_pages

        for current_page in range(1, total_pages + 1):
            print(f"Scraping page {current_page}/{total_pages}...")

            # Extract products
            page_products = extract_products_from_page(page)
            results.extend(page_products)

            if current_page < total_pages:
                # Go to next page
                next_page_num = current_page + 1
                try:
                    # Native playwright click for better reliability
                    loc = page.locator(f"a.page-link:has-text('{next_page_num}')").first
                    if loc:
                        loc.click()
                        page.wait_for_timeout(3000) # Small timeout to allow DOM to start updating, site is SPA-ish
                except Exception as e:
                    print(f"Error navigating to page {next_page_num}: {e}")
                    break

        browser.close()

    # Deduplicate items by URL or name
    unique_items = {}
    for item in results:
        key = item.get("url") or item.get("name")
        if key:
            unique_items[key] = item

    print(f"Captured {len(unique_items)} unique products.")

    products = []
    for item in unique_items.values():
        try:
            parsed = map_ligafarmacia_product(item)
            if parsed.price_regular > 0:
                products.append(parsed)
        except Exception as e:
            print(f"Error parsing item {item.get('name')}: {e}")

    batch = PharmacyProductBatch(
        scraped_at=datetime.now(timezone.utc),
        pharmacy_name="Otra", # Liga Farmacia is not in the explicit enum, so "Otra"
        source_url="https://www.ligafarmacia.cl/medicamentos",
        items_count=len(products),
        products=products
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(batch.model_dump_json(indent=2))

    print(f"Successfully mapped and saved {len(products)} products to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Liga Farmacia products.")
    parser.add_argument("--output", default="ligafarmacia_products.json", help="Output JSON file name")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum number of pages to scrape")
    args = parser.parse_args()

    scrape_ligafarmacia(args.output, args.max_pages)
