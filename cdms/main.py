from fastapi import FastAPI, Response, File, HTTPException, UploadFile, status
from contextlib import asynccontextmanager
from app.db import init_db, check_db
from typing import Union, List
from pydantic import ValidationError

from app.cdc import upsert_products
from app.schemas import Product

from app.utils import get_key, parse_row, COLUMNS
import pandas as pd

from app.poller import start_scheduler, stop_scheduler


import io

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()

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

@app.post("/api/v1/products/upload-excel")
def upload_excel(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    content = io.BytesIO(file.file.read())

    try:
        if name.endswith(".xlsx"):
            df = pd.read_excel(content, dtype=str)
        elif name.endswith(".csv"):
            df = pd.read_csv(content, dtype=str)
        else:
            raise HTTPException(400, "Only .xlsx or .csv files are supported")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Cannot parse file: {type(e).__name__}: {e}")

    df = df.rename(columns=lambda c: COLUMNS.get(get_key(c), c))
    rows = df.astype(object).where(df.notna(), None).to_dict("records")


    products, errors = [],[]

    for i, row in enumerate(rows, start=2):
        try:
            products.append(parse_row(row));
        except (ValidationError, ValueError) as e:
            msg = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            errors.append({"row": i, "error" : msg})

    result = upsert_products(products);

    return {
        "total" : len(rows),
        "processed" : len(products),
        "skipped" : len(errors),
        "inserted" : result["inserted"],
        "updated" : result["updated"],
        "unchanged" : result["unchanged"],
        "changes" : result["changed"],
        "errors" : errors + result["errors"]
    }

