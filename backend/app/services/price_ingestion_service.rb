class PriceIngestionService
  def initialize(batch_json_data)
    @data = batch_json_data
  end

  def call
    # 1. Validar el JSON contra el esquema
    # 2. Encontrar o crear la Pharmacy
    # 3. Iterar sobre los productos:
    #    - Encontrar/Crear Medicine (Matching)
    #    - Encontrar/Crear PharmacyProduct
    #    - Crear PriceHistory si hubo cambio
  end
end
