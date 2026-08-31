# PharmaScrapper

PharmaScrapper es una plataforma de comparación de precios de medicamentos. El proyecto está dividido en tres componentes principales: Backend, Frontend y Scraper. A continuación se detallan las instrucciones para configurar y ejecutar la aplicación completa.

## Requisitos Previos

Asegúrate de tener instalados los siguientes componentes en tu sistema:
- **Ruby** (v3+ recomendado, revisa `backend/.ruby-version` si está disponible)
- **Node.js** y **npm** (para el frontend SvelteKit)
- **Python** (v3.8+)
- **PostgreSQL** (en ejecución y con credenciales configuradas)

## Pasos de Ejecución

### 1. Configuración y Ejecución del Backend (Ruby on Rails)

El backend expone la API y gestiona la base de datos PostgreSQL.

1. Navega al directorio del backend:
   ```bash
   cd backend
   ```
2. Instala las dependencias de Ruby:
   ```bash
   bundle install
   ```
3. Configura la base de datos (creación, migraciones y datos semilla):
   ```bash
   # Asegúrate de configurar las variables de entorno para PostgreSQL si es necesario (DB_NAME, DB_USER, DB_PASSWORD)
   bin/rails db:prepare
   ```
4. Inicia el servidor de desarrollo (por defecto en `http://localhost:3000`):
   ```bash
   bin/rails server
   ```

### 2. Configuración y Ejecución del Frontend (SvelteKit)

El frontend proporciona la interfaz de usuario web.

1. En una nueva terminal, navega al directorio del frontend:
   ```bash
   cd frontend
   ```
2. Instala las dependencias de Node:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo (por defecto en `http://localhost:5173`):
   ```bash
   npm run dev
   ```

### 3. Configuración y Ejecución del Scraper (Python)

El scraper se encarga de extraer los datos de las farmacias e insertarlos en el backend. Asegúrate de que el **Backend esté en ejecución** antes de ingerir los datos, ya que el scraper se comunica con su API.

1. En una nueva terminal, navega al directorio del scraper:
   ```bash
   cd scraper
   ```
2. Crea un entorno virtual e instálalo:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias y los navegadores necesarios para Playwright:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. Ejecuta el pipeline completo (ejecutará todos los scrapers e iniciará la ingesta de datos):
   ```bash
   ./pipeline.sh
   ```
   *Nota: El script activará el entorno virtual y ejecutará las herramientas necesarias de forma automatizada.*

---
**Flujo Típico de Desarrollo:**
1. Levantar el Backend (`bin/rails server`).
2. Levantar el Frontend (`npm run dev`).
3. (Opcional o por tarea cron) Ejecutar el Scraper (`./pipeline.sh`) para poblar la base de datos con precios actualizados.
