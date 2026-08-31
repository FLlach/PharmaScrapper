# Especificación de Proyecto: Buscador y Comparador de Precios de Fármacos (Chile)

## 1. Contexto y Objetivos del Proyecto

El objetivo principal es construir una plataforma web integral que permita a los usuarios buscar, comparar y monitorear precios y disponibilidad de medicamentos y productos farmacéuticos a través de las principales cadenas de farmacias en Chile (ej. Farmacias Ahumada, Cruz Verde, Salcobrand, Redfarma, Dr. Simi, entre otras).

El proyecto se estructura en tres fases sucesivas:
1. **Fase 1: Motor de Web Scraping y Estandarización de Datos (JSON)**
2. **Fase 2: Backend y API RESTful (Ruby on Rails 8 & PostgreSQL)**
3. **Fase 3: Frontend y UI/UX (Svelte 5, SvelteKit & TypeScript)**

---

## 2. Stack Tecnológico y Herramientas

El proyecto se alinea estrictamente con el siguiente stack:

### 2.1 Backend & Base de Datos
- **Scraping:** Python
- **Framework:** Ruby on Rails 8
- **Lenguaje:** Ruby 3.x
- **Base de Datos:** PostgreSQL
- **Testing:** RSpec

### 2.2 Frontend & UI
- **Framework:** Svelte 5 + SvelteKit
- **Lenguaje:** TypeScript
- **UI / Componentes:** Storybook
- **E2E Testing:** Playwright

### 2.3 Infraestructura & Cloud
- **Hosting / Deploy:** Heroku / AWS
- **Servicios Auxiliares / Auth / Notificaciones:** Firebase

### 2.4 Asistencia y Calidad de Código
- **AI Tooling:** Claude Code, GitHub Copilot, CodeRabbit

---

## 3. Hoja de Ruta del Proyecto

```
┌─────────────────────────────────────────────────────────┐
│ Fase 1: Web Scraping & Normalización (JSON Estándar)    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ Fase 2: Backend API (Ruby on Rails 8 + PostgreSQL)      │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ Fase 3: Frontend & UI (SvelteKit + TypeScript + Tests)  │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Fase 1: Web Scraping & Formato de Datos

### 4.1 Requisitos del Scraper
- Capacidad de consultar o parsear catálogos y resultados de búsqueda de farmacias chilenas.
- Manejo de paginación, headers HTTP realistas, gestión de errores, reintentos y timeouts.
- Modularidad: cada farmacia debe contar con su extractor/adaptador independiente.

### 4.2 Esquema Estándar de Datos (JSON Schema)

Cada producto extraído debe normalizarse bajo el siguiente contrato JSON unificado para asegurar compatibilidad total con el backend en Rails:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PharmacyProductBatch",
  "type": "object",
  "required": ["scraped_at", "pharmacy_name", "items_count", "products"],
  "properties": {
    "scraped_at": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp ISO 8601 de la extracción (UTC)"
    },
    "pharmacy_name": {
      "type": "string",
      "enum": ["Cruz Verde", "Salcobrand", "Farmacias Ahumada", "Dr. Simi", "Redfarma", "Otra"]
    },
    "source_url": {
      "type": "string",
      "format": "uri"
    },
    "items_count": {
      "type": "integer"
    },
    "products": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "sku",
          "name",
          "brand",
          "price_regular",
          "in_stock",
          "product_url"
        ],
        "properties": {
          "sku": {
            "type": "string",
            "description": "Identificador único asignado por la farmacia"
          },
          "name": {
            "type": "string",
            "description": "Nombre comercial completo del fármaco/producto"
          },
          "active_ingredient": {
            "type": ["string", "null"],
            "description": "Principio activo (ej. Paracetamol, Ibuprofeno)"
          },
          "dosage": {
            "type": ["string", "null"],
            "description": "Dosis / Concentración (ej. 500 mg, 10 mg/ml)"
          },
          "presentation": {
            "type": ["string", "null"],
            "description": "Formato (ej. 20 Comprimidos, Jarabe 120ml)"
          },
          "brand": {
            "type": "string",
            "description": "Laboratorio o marca comercial"
          },
          "bioequivalent": {
            "type": "boolean",
            "description": "Indica si está marcado como bioequivalente / genérico"
          },
          "prescription_required": {
            "type": "boolean",
            "description": "Indica si requiere receta médica"
          },
          "price_regular": {
            "type": "integer",
            "description": "Precio normal en CLP (número entero)"
          },
          "price_offer": {
            "type": ["integer", "null"],
            "description": "Precio en oferta / suscripción en CLP si aplica"
          },
          "unit_price_description": {
            "type": ["string", "null"],
            "description": "Precio por unidad de medida (ej. $150 x Comprimido)"
          },
          "currency": {
            "type": "string",
            "default": "CLP"
          },
          "in_stock": {
            "type": "boolean"
          },
          "image_url": {
            "type": ["string", "null"],
            "format": "uri"
          },
          "product_url": {
            "type": "string",
            "format": "uri"
          },
          "category": {
            "type": ["string", "null"]
          }
        }
      }
    }
  }
}
```

### 4.3 Ejemplo de Documento JSON Generado

```json
{
  "scraped_at": "2026-08-29T17:30:00Z",
  "pharmacy_name": "Cruz Verde",
  "source_url": "https://www.cruzverde.cl/medicamentos/",
  "items_count": 2,
  "products": [
    {
      "sku": "CV-109283",
      "name": "Paracetamol 500 mg 20 Comprimidos",
      "active_ingredient": "Paracetamol",
      "dosage": "500 mg",
      "presentation": "20 Comprimidos",
      "brand": "Laboratorio Chile",
      "bioequivalent": true,
      "prescription_required": false,
      "price_regular": 1290,
      "price_offer": 990,
      "unit_price_description": "$49.5 por comprimido",
      "currency": "CLP",
      "in_stock": true,
      "image_url": "https://images.cruzverde.cl/products/109283.jpg",
      "product_url": "https://www.cruzverde.cl/paracetamol-500-mg-20-comprimidos/109283.html",
      "category": "Analgésicos y Antipiréticos"
    },
    {
      "sku": "CV-882310",
      "name": "Ibuprofeno 400 mg 10 Cápsulas Blandas",
      "active_ingredient": "Ibuprofeno",
      "dosage": "400 mg",
      "presentation": "10 Cápsulas Blandas",
      "brand": "Mintlab",
      "bioequivalent": true,
      "prescription_required": false,
      "price_regular": 2490,
      "price_offer": null,
      "unit_price_description": "$249 por cápsula",
      "currency": "CLP",
      "in_stock": true,
      "image_url": "https://images.cruzverde.cl/products/882310.jpg",
      "product_url": "https://www.cruzverde.cl/ibuprofeno-400-mg-10-capsulas/882310.html",
      "category": "Antiinflamatorios"
    }
  ]
}
```

---

## 5. Fase 2: Backend (Ruby on Rails 8 + PostgreSQL)

### 5.1 Modelado Relacional Sugerido
- **`Pharmacies`**: ID, nombre, dominio base, logo URL, activa.
- **`Medicines` (Entidad canónica):** Nombre genérico/común, principio activo, dosis estándar, bioequivalencia.
- **`PharmacyProducts` (Catálogo por tienda):** Pharmacy ID, Medicine ID (opcional / asociable), SKU, nombre según tienda, URL, imagen.
- **`PriceHistories`:** PharmacyProduct ID, precio normal, precio oferta, en stock, captured_at.

### 5.2 Tareas Clave del Backend
1. **Pipeline de Ingesta:** Endpoint o Rake Task (`rails import:prices`) para parsear y almacenar los JSON generados por el scraper.
2. **Algoritmo de Matching:** Comparación difusa (fuzzy search) y normalización de nombres para agrupar productos idénticos entre distintas farmacias bajo un mismo principio activo o medicamento canónico.
3. **Endpoints REST:**
   - `GET /api/v1/medicines?query=paracetamol`: Búsqueda de medicamentos con ordenamiento por menor precio.
   - `GET /api/v1/medicines/:id/comparison`: Comparativa detallada por farmacia y variaciones históricas de precio.
   - `GET /api/v1/pharmacies`: Lista de farmacias monitoreadas y estado de actualización.
4. **Testing:** Cobertura con RSpec para modelos, servicios de ingesta y endpoints de la API.

---

## 6. Fase 3: Frontend (Svelte 5, SvelteKit & TypeScript)

### 6.1 Vistas y Componentes Principales
- **Barra de Búsqueda Inteligente:** Input reactivo con debounce para buscar por nombre comercial o principio activo.
- **Grilla / Lista de Resultados:** Vista comparativa con tarjetas destacando:
  - Farmacia con el precio más bajo.
  - Indicador de stock.
  - Sello de bioequivalencia.
- **Ficha Comparativa de Producto:** Tabla desglosada por farmacia (precio normal, oferta, link directo a compra).
- **Componentes Aislados en Storybook:** Botones, badges de stock/bioequivalente, tarjetas de precios y tablas comparativas.
- **Pruebas End-to-End con Playwright:** Flujo crítico de búsqueda y comparación de precios.

---

## 7. Instrucciones para Jules (System Prompt & Directrices de Ejecución)

Al interactuar con el agente Jules:
1. **Comenzar estrictamente por la Fase 1:** Desarrollar los scripts de scraping modulares y validar que la salida cumpla 100% con el JSON Schema estipulado en la sección 4.2.
2. **Priorizar robustez en el scraping:** Implementar manejo de errores, reintentos y respeto por rate limits.
3. **Mantener tipado estricto en TypeScript** y convenciones estándar de **Rails 8 (MVC, Service Objects para la ingesta y RSpec para tests)**.
4. **No saltar a la UI sin antes haber completado y probado la ingesta y la API.**

## 8. Consideraciones de Arquitectura y Patrones de Diseño

- **Ingesta Desacoplada:** Los scrapers se ejecutan como jobs asíncronos mediante Solid Queue (Rails 8) programados periódicamente.
- **Motor de Búsqueda:** PostgreSQL con extensión `pg_trgm` e índices GIN sobre campos de texto para búsqueda difusa tolerante a errores tipográficos.
- **Normalización de Datos:** Separación de entidades canónicas (`Medicine`) y productos por tienda (`PharmacyProduct`) mediante un pipeline de deduplicación y matching.
- **Estrategia Frontend:** SvelteKit con SSR para rutas dinámicas de producto (SEO) y reactividad en cliente (Svelte 5 runes) para búsqueda y filtrado de precios en vivo.
- **Testing Pyramid:** 
  - Backend: Unit tests y request specs con RSpec.
  - Frontend: Component testing en Storybook y pruebas E2E críticas con Playwright.


# Repository Agent Rules

## Architectural Boundaries:
1. **Scraper Service (`/scraper`)**: Scripts de extracción y JSON schema. No debe tener dependencias con Rails ni Svelte.
2. **Backend API (`/backend`)**: Ruby on Rails 8 + PostgreSQL. Solo interactúa con `/scraper` mediante ingesta de archivos JSON.
3. **Frontend (`/frontend`)**: SvelteKit + TypeScript. No accede a BD directamente, solo consume la API REST.

## General Directives for Jules:
- Always restrict your file changes strictly to the module/directory specified in the task prompt.
- Never edit multiple architectural layers in a single task/PR.

## Links
www.cruzverde.cl
www.farmaciasahumada.cl
www.salcobrand.cl
www.drsimi.cl
www.ligafarmacia.cl