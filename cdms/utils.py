import json
import re

from app.schemas import Product


# Header (lower-cased, punctuation removed) -> VietFul field name
COLUMNS = {
    "productid": "productId", "sku": "sku", "partnersku": "partnerSKU",
    "productname": "productName", "assettype": "assetType", "hasserial": "hasSerial",
    "hasexpiration": "hasExpiration", "color": "color", "size": "size",
    "description": "description", "isactive": "isActive", "units": "units",
    "categories": "categories",
}

def get_key(header) -> str:
    return re.sub(r"[^a-z0-9]", "", str(header).lower())


def parse_row(row: dict) -> Product:
    data = {k : v for k, v in row.items() if k in COLUMNS.values() and v not in (None, "")} 
    if "units" in data:
        u = data["units"]
        data["units"] = json.load(u) if u.startswith("[") else [s.strip() for s in u.split(",")]
    if "categories" in data:
        data["categories"] = json.loads(data["categories"])
    return Product(**data)
