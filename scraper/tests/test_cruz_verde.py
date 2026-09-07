import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cruz_verde import map_cruz_verde_product
from schema import PharmacyProduct

def test_map_cruz_verde_product_happy_path():
    raw_item = {
        "productId": "12345",
        "productName": "Paracetamol 500mg",
        "brand": "Laboratorio Chile",
        "isBioequivalent": True,
        "prices": {
            "price-list-cl": 1500,
            "price-sale-cl": 1000
        },
        "pum": "100 por unidad",
        "stock": 10,
        "imageUrl": "https://example.com/image.jpg",
        "pdpUrl": "https://cruzverde.cl/paracetamol",
        "request_category_id": "medicamentos"
    }

    product = map_cruz_verde_product(raw_item)

    assert isinstance(product, PharmacyProduct)
    assert product.sku == "12345"
    assert product.name == "Paracetamol 500mg"
    assert product.brand == "Laboratorio Chile"
    assert product.bioequivalent is True
    assert product.price_regular == 1500
    assert product.price_offer == 1000
    assert product.unit_price_description == "100 por unidad"
    assert product.currency == "CLP"
    assert product.in_stock is True
    assert product.image_url == "https://example.com/image.jpg"
    assert product.product_url == "https://cruzverde.cl/paracetamol"
    assert product.category == "medicamentos"

def test_map_cruz_verde_product_same_price():
    raw_item = {
        "productId": "12345",
        "productName": "Paracetamol 500mg",
        "prices": {
            "price-list-cl": 1500,
            "price-sale-cl": 1500
        }
    }

    product = map_cruz_verde_product(raw_item)

    assert product.price_regular == 1500
    assert product.price_offer is None

def test_map_cruz_verde_product_no_offer_price():
    raw_item = {
        "productId": "12345",
        "productName": "Paracetamol 500mg",
        "prices": {
            "price-list-cl": 1500
        }
    }

    product = map_cruz_verde_product(raw_item)

    assert product.price_regular == 1500
    assert product.price_offer is None

def test_map_cruz_verde_product_image_fallback():
    raw_item = {
        "productId": "12345",
        "productName": "Paracetamol 500mg",
        "images": [
            {"link": "https://example.com/fallback.jpg"}
        ]
    }

    product = map_cruz_verde_product(raw_item)

    assert product.image_url == "https://example.com/fallback.jpg"

def test_map_cruz_verde_product_missing_fields_defaults():
    raw_item = {}

    product = map_cruz_verde_product(raw_item)

    assert product.sku == ""
    assert product.name == ""
    assert product.brand == "Desconocido"
    assert product.bioequivalent is False
    assert product.price_regular == 0
    assert product.price_offer is None
    assert product.unit_price_description is None
    assert product.currency == "CLP"
    assert product.in_stock is False
    assert product.image_url is None
    assert product.product_url == ""
    assert product.category is None
