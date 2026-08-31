# Anotaciones y Correcciones del Proyecto

Este documento registra observaciones, mejores prácticas y correcciones detectadas durante el desarrollo para evitar errores recurrentes y optimizar la arquitectura.

## 1. Fase 1: Web Scraping
- **APIs Ocultas vs HTML Parsing:** Las farmacias chilenas modernas (Cruz Verde, Salcobrand, Ahumada) suelen utilizar plataformas de e-commerce como VTEX o motores de búsqueda como Algolia. En lugar de parsear HTML con BeautifulSoup o Nokogiri, es mucho más robusto, rápido y estable interceptar las peticiones a las APIs internas que devuelven JSON directamente.
- **Identificador Único (EAN):** Aunque el JSON schema define un `sku`, siempre que sea posible se debe extraer el código de barras (EAN/UPC) de los productos. Esto facilitará enormemente la Fase 2 (Matching), ya que el nombre puede variar entre farmacias, pero el EAN es universal para el mismo producto físico.
- **Tipos de Datos:** El esquema requiere que `price_regular` y `price_offer` sean números enteros (CLP no tiene decimales en uso práctico, pero a veces las APIs retornan floats como `1590.0`). Asegurarse de coercionar siempre los valores extraídos a enteros (ej. `.to_i`) para no fallar la validación.

## 2. Fase 2: Backend
- **Idempotencia en la Ingesta:** El servicio `PriceIngestionService` debe ser completamente idempotente. Al correr múltiples veces el mismo batch de scraping, no debe duplicar `PharmacyProduct`, sino actualizar los precios y crear nuevos `PriceHistory` solo si el precio cambió.
- **Matching y Deduplicación:** Se recomienda que la entidad `Medicine` se nutra primariamente del Instituto de Salud Pública (ISP) de Chile si es posible (nombres de registros sanitarios), y usar las técnicas de búsqueda difusa solo como fallback secundario o en el frontend.

## 3. Fase 3: Frontend
- **Manejo de Estado (Runes):** En Svelte 5 se deben usar *runes* (`$state`, `$derived`, `$props`, `$effect`) en lugar de los métodos reactivos de Svelte 4 para garantizar el máximo rendimiento de actualización de la UI.
- **Scraper Best Practices**: Do not commit scraped data `.json` files or scratchpad `.py` scripts used during development. Always remove them before submitting a patch.
- **Playwright Native Methods**: Prefer Playwright's native locator actions (e.g., `page.locator().click()`) over injecting javascript `page.evaluate(() => element.click())` for more reliable and deterministic automation.
Backend (Rails 8 API): Initialize core functionality, integrate authentication (native + Google OAuth), configure PostgreSQL schemas, and implement the Medicines and Pharmacies REST APIs with Rswag documentation. N+1 queries were resolved using Ruby's `max_by`, and OmniAuth was correctly routed within the `/api/v1/auth` namespace to enable GET and POST requests.
