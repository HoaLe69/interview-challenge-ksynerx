import random
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from faker import Faker

fake = Faker()

class CategoryModel(BaseModel):
    categoryCode: str = Field(..., example="CAT_METAL")
    categoryName: str = Field(..., example="Raw Materials")

class VietFulProduct(BaseModel):
    productId: int = Field(..., example=123)
    sku: str = Field(..., example="SKU-001-RED-XXL")
    partnerSKU: str = Field(..., example="PARTNER-SKU-99")
    productName: str = Field(..., example="Kẽm")
    assetType: str = Field("Single", example="Single")
    hasSerial: bool = Field(False, example=True)
    hasExpiration: bool = Field(False, example=True)
    color: Optional[str] = Field(None, example="Red")
    size: Optional[str] = Field(None, example="XXL")
    description: Optional[str] = Field(None, example="Cutting edge product description")
    isActive: bool = Field(True, example=True)
    units: List[str] = Field(default_factory=lambda: ["Pcs"], example=["Pcs", "Box"])
    categories: List[CategoryModel] = Field(default_factory=list)

router = APIRouter(prefix="/api/v1", tags=["VietFul Mock Inventory Service"])

# In-memory storage for mock catalog
MOCK_CATALOG: dict[str, VietFulProduct] = {}

# Predefined categories for realistic mock generation
SAMPLE_CATEGORIES = [
    CategoryModel(categoryCode="CAT_METAL", categoryName="Raw Materials"),
    CategoryModel(categoryCode="CAT_ELEC", categoryName="Electronics"),
    CategoryModel(categoryCode="CAT_APPAREL", categoryName="Apparel & Garments"),
    CategoryModel(categoryCode="CAT_PLASTIC", categoryName="Plastics & Polymers")
]

def generate_fake_product(product_id: int, sku_override: Optional[str] = None) -> VietFulProduct:
    """Helper to construct a realistic VietFul product using Faker."""
    color = fake.color_name()
    size = random.choice(["S", "M", "L", "XL", "XXL"])
    sku = sku_override or f"SKU-{product_id:03d}-{color.upper()[:3]}-{size}"
    
    return VietFulProduct(
        productId=product_id,
        sku=sku,
        partnerSKU=f"PARTNER-SKU-{fake.random_int(min=10, max=99)}",
        productName=fake.word().capitalize(),
        assetType=random.choice(["Single", "Bundle", "Assembly"]),
        hasSerial=fake.boolean(chance_of_getting_true=30),
        hasExpiration=fake.boolean(chance_of_getting_true=20),
        color=color,
        size=size,
        description=fake.sentence(nb_words=10),
        isActive=True,
        units=random.choice([["Pcs"], ["Pcs", "Box"], ["Kg", "Ton"]]),
        categories=random.sample(SAMPLE_CATEGORIES, k=random.randint(1, 2))
    )

def init_mock_catalog(count: int = 15):
    """Seed the in-memory catalog if empty."""
    if not MOCK_CATALOG:
        for i in range(1, count + 1):
            prod = generate_fake_product(i)
            MOCK_CATALOG[prod.sku] = prod

@router.get("/product", response_model=List[VietFulProduct])
def get_vietful_products(
    limit: int = Query(default=10, ge=1, le=100, description="Number of products to retrieve"),
    perturb: bool = Query(default=False, description="Simulate data changes in existing products for testing CDC")
):
    """
    Mock endpoint simulating VietFul Inventory API GET /api/v1/product.
    Supports optional perturbation to test CDC deduplication & change detection.
    """
    init_mock_catalog()
    products = list(MOCK_CATALOG.values())[:limit]

    if perturb and products:
        # Randomly mutate one product to simulate an updated record in VietFul
        target = random.choice(products)
        target.productName = f"{target.productName} (Updated)"
        target.description = f"Updated at {fake.date_time_this_month().isoformat()}"
        MOCK_CATALOG[target.sku] = target
    return products

@router.get("/product/{sku}", response_model=VietFulProduct)
def get_vietful_product_by_sku(sku: str):
    """
    Mock endpoint simulating VietFul Inventory API GET /api/v1/product/{sku}.
    """
    init_mock_catalog()
    
    if sku in MOCK_CATALOG:
        return MOCK_CATALOG[sku]
    
    raise HTTPException(status_code=404, detail=f"Product with SKU '{sku}' not found in VietFul Inventory")
