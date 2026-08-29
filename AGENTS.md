# Repository Agent Rules

## Architectural Boundaries:
1. **Scraper Service (`/scraper`)**: Scripts de extracción y JSON schema. No debe tener dependencias con Rails ni Svelte.
2. **Backend API (`/backend`)**: Ruby on Rails 8 + PostgreSQL. Solo interactúa con `/scraper` mediante ingesta de archivos JSON.
3. **Frontend (`/frontend`)**: SvelteKit + TypeScript. No accede a BD directamente, solo consume la API REST.

## General Directives for Jules:
- Always restrict your file changes strictly to the module/directory specified in the task prompt.
- Never edit multiple architectural layers in a single task/PR.