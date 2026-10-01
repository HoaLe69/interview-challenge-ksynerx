# Testing

## Manual Test

1. **Idempotent qua webhook**: gửi cùng một payload hai lần. Lần 1 `changed=1`, lần 2 `changed=0`.

2. **Excel**: upload `samples/products.csv`. Lần 1 `inserted=2, skipped=1`. Lần 2 `unchanged=2`.

3. **Polling**: đặt `POLL_INTERVAL_SECONDS=10`, xem `docker compose logs -f cdms`.

4. **Health khi DB sập**: `docker compose stop db` thì `/health` trả 503, `docker compose start db` thì tự hồi phục.

## Spike test

- Do hạn chế về mặt thời gian nên chưa thể thực hiện test bằng script với số lượng data lớn.

## Data test

- Sample CSV data: `/tests/sample.csv`

- Sample JSON data for `/api/v1/product/webhook`:

```json
[
  {
    "productId": 1,
    "sku": "SKU-001",
    "partnerSku": "P-1",
    "productName": "Kem",
    "color": "Red",
    "size": "XXL",
    "isActive": true,
    "units": ["Pcs", "Box"],
    "categories": [
      {
        "categoryCode": "CAT_METAL",
        "categoryName": "Raw Materials"
      }
    ]
  },
  {
    "productId": 2,
    "sku": "SKU-002",
    "partnerSku": "P-2",
    "productName": "Dong",
    "color": "Blue",
    "size": "M",
    "isActive": true,
    "units": ["Pcs"],
    "categories": []
  }
]
```
