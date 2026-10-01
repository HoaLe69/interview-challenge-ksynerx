from fastapi import FastAPI, Response, status
from contextlib import asynccontextmanager
from app.db import init_db, check_db
from typing import Union, List
from pydantic import ValidationError

from app.cdc import upsert_products
from app.schemas import Product

from app.utils import key, parse_row, COLUMNS


import io

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check(response: Response):
    ok = check_db()
    response.status_code = 200 if ok else 503
    return {"status": "healthy" if ok else "unhealthy"}



@app.post("/api/v1/webhook/product", status_code=202)
def webhook_product(payload: Union[Product, List[Product]]):
    products = payload if isinstance(payload, list) else [payload]

    result = upsert_products(products)

    return { 
        "status" : "accepted", 
        "count" : len(products), 
        "changed" : result["changed"],
        "errors" : result["errors"]
    }
