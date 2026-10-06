import os
import requests

BASE_URL = os.getenv("OFF_BASE_URL", "https://world.openfoodfacts.org")
HEADERS = {"User-Agent": "InventoryAdmin/1.0 (katelyn.chemjor@moringaschool.com)"}
TIMEOUT = 10
FIELDS = "code,product_name,brands,ingredients_text,nutriscore_grade,nova_group"


class OFFError(Exception):
    pass


class ProductNotFound(OFFError):
    pass


def _normalize(product, barcode=None):
    return {
        "barcode": product.get("code") or barcode,
        "name": product.get("product_name") or "Unknown product",
        "brand": (product.get("brands") or "").split(",")[0].strip(),
        "ingredients": product.get("ingredients_text", ""),
        "nutriscore": product.get("nutriscore_grade"),
        "nova_group": product.get("nova_group"),
    }


def fetch_by_barcode(barcode):
    url = f"{BASE_URL}/api/v3.6/product/{barcode}.json"
    r = requests.get(url, params={"fields": FIELDS}, headers=HEADERS, timeout=TIMEOUT)
    if r.status_code == 404:
        raise ProductNotFound(f"No product with barcode {barcode}")
    r.raise_for_status()
    product = r.json().get("product")
    if not product:
        raise ProductNotFound(f"No product with barcode {barcode}")
    return _normalize(product, barcode)


def search_by_name(name, limit=5):
    # API v3 has no search endpoint; the legacy search endpoint still works.
    # It is limited to 10 requests/min/IP, so don't call it in a loop.
    params = {
        "search_terms": name, "search_simple": 1, "action": "process",
        "json": 1, "page_size": limit, "fields": FIELDS,
    }
    r = requests.get(f"{BASE_URL}/cgi/search.pl", params=params,
                     headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return [_normalize(p) for p in r.json().get("products", [])]