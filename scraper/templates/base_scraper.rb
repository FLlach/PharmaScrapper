# Template base para un adaptador de scraping
# Este es un esqueleto en Ruby, pero puede adaptarse al lenguaje definido para los scrapers.

class BaseScraper
  def initialize
    # Configuración de headers, timeouts, etc.
  end

  def fetch_catalog
    # Lógica para obtener el catálogo o realizar búsquedas
    raise NotImplementedError
  end

  def parse_product(html_or_json_node)
    # Lógica para extraer los campos del producto
    # Debe retornar un hash que cumpla con el esquema JSON
    raise NotImplementedError
  end

  def run
    # Flujo principal:
    # 1. fetch_catalog
    # 2. iterar sobre productos y parse_product
    # 3. construir y retornar (o guardar) el objeto PharmacyProductBatch
    raise NotImplementedError
  end
end
