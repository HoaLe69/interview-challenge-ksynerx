import json 
import logging
import urllib.request

import time
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import ValidationError

from app.core import upsert_products
from app.config import POLL_INTERVAL_SECONDS, VIETFUL_URL
from app.schemas import Product

log = logging.getLogger("poller")
scheduler = BackgroundScheduler()


def poll_once(): 
    print("Run schedule Job")
    try:
        with urllib.request.urlopen(VIETFUL_URL, timeout=10) as resp:
            raw = json.load(resp)
        products = []
        for item in raw:
            try:
                products.append(Product(**item))
            except ValidationError as e:
                log.warning("Skip invalid item: %s", e.errors()[0])
        result = upsert_products(products)

        log.info("poll done: %s", {k: v for k, v in result.items() if k != "errors"})
    except Exception:
    #VietFul or DB down: log and wait for the next tick, never crash the scheduler
        log.exception("poll failed")

def start_scheduler():
    scheduler.add_job(poll_once, "interval", seconds=POLL_INTERVAL_SECONDS, max_instances=1, coalesce=True)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown(wait=False)
