# Change Data Management Service Prototype

A service that stores **only new or changed** product data coming from three sources, with effectively-once
semantics under failures and spike load.

## Problem statement

- Emulate a Vietful-like inventory service (Products API).
- CDMS ingests product data via three mechanisms:
  1. Scheduled polling of the inventory service
  2. Webhook callbacks
  3. Excel file upload over REST
- Only new/changed data is persisted: no old data, no duplicates.
- Must survive failures of CDMS, Vietful, the database and the host machine.
- Containerized (Docker Compose), single machine.

## Tech stack

FastAPI, PostgreSQL, Docker Compose, Python 3.12

## Project structure

interview-challenge-ksynerx/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── vietful_mock/             # service giả lập Vietful
│   └── app/
├── cdms/                     # service chính
│   ├── main.py
│   └── migrations/           # Alembic
├── tools/                    # faker client, chaos script, load test
├── tests/
└── docs/
