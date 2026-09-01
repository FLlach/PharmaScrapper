# Fase 2: Backend & API RESTful (Ruby on Rails 8 & PostgreSQL)

## Objetivo
Implementar la API que recibirá, almacenará y servirá los datos de medicamentos al frontend.

## Tareas Clave
- **Modelos:** `Pharmacy`, `Medicine`, `PharmacyProduct`, `PriceHistory`.
- **Servicios:** Lógica de negocio para la ingesta de JSON (`PriceIngestionService`) y normalización (matching).
- **Controladores:** Endpoints RESTful en `app/controllers/api/v1`.
- **Tareas (Tasks):** `lib/tasks/` para programar la ingesta asíncrona.
- **Tests:** Cobertura con RSpec en `spec/`.
- **Documentación API:** Swagger/OpenAPI mediante `rswag`.

## Instrucciones de Ejecución en Windows

Si estás ejecutando o desarrollando este proyecto en **Windows**, asegúrate de seguir los siguientes pasos:

### 1. Requisitos Previos en Windows
- **Ruby:** Descarga e instala la última versión de [RubyInstaller for Windows](https://rubyinstaller.org/).
  - Al finalizar la instalación, marca la opción para ejecutar `ridk install` e instalar los componentes de **MSYS2** base (necesarios para compilar gemas nativas como `pg`).
- **PostgreSQL:** Instala [PostgreSQL para Windows](https://www.postgresql.org/download/windows/) y asegúrate de que el servicio esté ejecutándose en el puerto 5432.
- **Git:** Instalado y configurado en tu entorno.

### 2. Preparación del Entorno
Clona el proyecto, abre tu terminal (se recomienda PowerShell o Windows Terminal) e ingresa al directorio del backend:

```powershell
cd ruta\al\proyecto\backend
```

Si encuentras problemas al instalar la gema de base de datos (`pg`), asegúrate de que los binarios de PostgreSQL estén en tu variable de entorno PATH, o provéelos mediante Bundler:
```powershell
bundle config build.pg --with-pg-dir="C:\Program Files\PostgreSQL\<version>"
```

Instala las dependencias del proyecto:
```powershell
bundle install
```

### 3. Configuración de Base de Datos y Credenciales
La aplicación necesita ciertas credenciales de desarrollo. Si tienes variables de entorno configuradas localmente para Google OAuth (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`), asegúrate de cargarlas (puedes usar un archivo `.env` mediante la gema dotenv si la instalas posteriormente).

Para inicializar la base de datos de Rails, corre:
```powershell
bin\rails db:create
bin\rails db:migrate
```

### 4. Levantar el Servidor y la Documentación
Inicia el servidor backend en modo API:
```powershell
bin\rails server
```

El servidor estará escuchando en `http://localhost:3000`.

**Para ver la documentación OpenAPI interactiva (Swagger UI):**
Abre en tu navegador `http://localhost:3000/api-docs` para interactuar con los endpoints de la API (Medicines y Pharmacies).

## Instrucciones Generales
- Mantener convención de nombres y estructura estándar de Rails.
- Priorizar la deduplicación de medicamentos en el servicio de ingesta.
- Los endpoints deben ser eficientes, apoyándose en índices en la DB para búsquedas.
