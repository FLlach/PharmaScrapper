from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class PharmacyProduct(BaseModel):
    sku: str = Field(description="Identificador único asignado por la farmacia")
    name: str = Field(description="Nombre comercial completo del fármaco/producto")
    active_ingredient: Optional[str] = Field(default=None, description="Principio activo")
    dosage: Optional[str] = Field(default=None, description="Dosis / Concentración")
    presentation: Optional[str] = Field(default=None, description="Formato")
    brand: str = Field(description="Laboratorio o marca comercial")
    bioequivalent: bool = Field(description="Indica si está marcado como bioequivalente / genérico")
    prescription_required: bool = Field(default=False, description="Indica si requiere receta médica")
    price_regular: int = Field(description="Precio normal en CLP (número entero)")
    price_offer: Optional[int] = Field(default=None, description="Precio en oferta / suscripción en CLP si aplica")
    unit_price_description: Optional[str] = Field(default=None, description="Precio por unidad de medida")
    currency: str = Field(default="CLP")
    in_stock: bool
    image_url: Optional[str] = None
    product_url: str
    category: Optional[str] = None

class PharmacyProductBatch(BaseModel):
    scraped_at: datetime = Field(description="Timestamp ISO 8601 de la extracción (UTC)")
    pharmacy_name: str
    source_url: str
    items_count: int
    products: List[PharmacyProduct]
