# Fase 2: Backend & API RESTful (Ruby on Rails 8 & PostgreSQL)

## Objetivo
Implementar la API que recibirá, almacenará y servirá los datos de medicamentos al frontend.

## Tareas Clave
- **Modelos:** `Pharmacy`, `Medicine`, `PharmacyProduct`, `PriceHistory`.
- **Servicios:** Lógica de negocio para la ingesta de JSON (`PriceIngestionService`) y normalización (matching).
- **Controladores:** Endpoints RESTful en `app/controllers/api/v1`.
- **Tareas (Tasks):** `lib/tasks/` para programar la ingesta asíncrona.
- **Tests:** Cobertura con RSpec en `spec/`.

## Instrucciones
- Mantener convención de nombres y estructura estándar de Rails.
- Priorizar la deduplicación de medicamentos en el servicio de ingesta.
- Los endpoints deben ser eficientes, apoyándose en índices en la DB para búsquedas.
