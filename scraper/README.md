# Fase 1: Web Scraping & Normalización

## Objetivo
Desarrollar scrapers modulares por farmacia que extraigan datos y los normalicen según el esquema JSON definido.

## Estructura
- `schemas/`: Contiene el esquema JSON (`PharmacyProductBatch.json`) para validación.
- `adapters/`: Contendrá los scrapers específicos por farmacia (ej. `cruz_verde.rb`, `salcobrand.rb` o el lenguaje de preferencia para esta fase).
- `templates/`: Plantillas base para facilitar la creación de nuevos scrapers.
- `output/`: Directorio donde se guardarán temporalmente los JSON generados.

## Consideraciones
- Manejar paginación y headers HTTP realistas.
- Implementar gestión de errores, reintentos y timeouts.
- Asegurar que el JSON generado pase la validación contra `schemas/PharmacyProductBatch.json`.
