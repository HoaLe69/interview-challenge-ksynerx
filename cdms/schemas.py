from typing import List, Optional

from pydantic import BaseModel, field_validator


class Category(BaseModel):
    categoryCode: str
    categoryName: Optional[str] = None

class Product(BaseModel):
    productId: int
    sku: str
    partnerSKU: Optional[str] = None
    productName: str
    assetType: str = "Single"
    hasSerial: bool = False
    hasExpiration: bool = False
    color: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    isActive: bool = True
    units: List[str] = []
    categories: List[Category] = []

    @field_validator("*", mode="before")
    @classmethod
    def _clean_str(cls,v):
    # Normalize: trim whitespace, empty string -> None (so all 3 api hash the same)
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

