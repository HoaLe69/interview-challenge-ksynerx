import hashlib
import json
from typing import List

from sqlalchemy import text

from app.db import engine
from app.schemas import Product


UPSERT_SQL = text("""
    INSERT INTO products (
        product_id, sku, partner_sku, product_name, asset_type, has_serial,
        has_expiration, color, size, description, is_active, units, categories,
        payload_hash, updated_at
    ) VALUES (
        :product_id, :sku, :partner_sku, :product_name, :asset_type, :has_serial,
        :has_expiration, :color, :size, :description, :is_active,
        CAST(:units AS JSONB), CAST(:categories AS JSONB), :payload_hash, CURRENT_TIMESTAMP
    )
    ON CONFLICT (sku) DO UPDATE SET
        partner_sku = EXCLUDED.partner_sku,
        product_name = EXCLUDED.product_name,
        asset_type = EXCLUDED.asset_type,
        has_serial = EXCLUDED.has_serial,
        has_expiration = EXCLUDED.has_expiration,
        color = EXCLUDED.color,
        size = EXCLUDED.size,
        description = EXCLUDED.description,
        is_active = EXCLUDED.is_active,
        units = EXCLUDED.units,
        categories = EXCLUDED.categories,
        payload_hash = EXCLUDED.payload_hash,
        updated_at = CURRENT_TIMESTAMP
    WHERE products.payload_hash IS DISTINCT FROM EXCLUDED.payload_hash
    RETURNING (xmax = 0) AS inserted
""")


def compute_hash(p : Product) -> str:
    """SHA-256 over canonical JSON of every business field ( productId exclueded). """
    data = p.model_dump(exclude={"productId"})
    data["units"] = sorted(data["units"])
    data["categories"] = sorted(data["categories"], key=lambda c: c["categoryCode"])
    raw = json.dumps(data, sort_keys=True, separators=(",",":"), ensure_ascii=False)

    return hashlib.sha256(raw.encode("utf=8")).hexdigest()


def _params(p : Product) -> dict:
    return {
        "product_id": p.productId,
        "sku": p.sku,
        "partner_sku": p.partnerSKU,
        "product_name": p.productName,
        "asset_type": p.assetType,
        "has_serial": p.hasSerial,
        "has_expiration": p.hasExpiration,
        "color": p.color,
        "size": p.size,
        "description": p.description,
        "is_active": p.isActive,
        "units": json.dumps(p.units),
        "categories": json.dumps([c.model_dump() for c in p.categories]),
        "payload_hash": compute_hash(p),
    }


def upsert_products(products: List[Product]) -> dict:
    """Single entry point for all 3 channels. One transaction, one savepoint per row."""
    unique = {p.sku: p for p in products}  # same SKU twice in a batch: last one wins
    result = {"received": len(products), "inserted": 0, "updated": 0,
              "unchanged": 0, "errors": []}
 
    with engine.begin() as conn:
        for sku in sorted(unique):  # fixed order across workers -> fewer deadlocks
            try:
                with conn.begin_nested():  # a bad row doesn't abort the others
                    row = conn.execute(UPSERT_SQL, _params(unique[sku])).first()
            except Exception as e:
                result["errors"].append({"sku": sku, "error": type(e).__name__})
                continue
            if row is None:
                result["unchanged"] += 1
            elif row.inserted:
                result["inserted"] += 1
            else:
                result["updated"] += 1
 
    result["changed"] = result["inserted"] + result["updated"]
    return result
