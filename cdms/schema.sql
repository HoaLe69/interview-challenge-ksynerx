CREATE TABLE IF NOT EXISTS products (
    product_id      BIGINT PRIMARY KEY,
    sku             VARCHAR(100) NOT NULL UNIQUE,
    partner_sku     VARCHAR(100),
    product_name    VARCHAR(255) NOT NULL,
    asset_type      VARCHAR(50) DEFAULT 'Single',
    has_serial      BOOLEAN DEFAULT FALSE,
    has_expiration  BOOLEAN DEFAULT FALSE,
    color           VARCHAR(50),
    size            VARCHAR(50),
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    units           JSONB DEFAULT '[]'::jsonb,
    categories      JSONB DEFAULT '[]'::jsonb,
    payload_hash    CHAR(64) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- UNIQUE(sku) already creates an index, so no extra index is needed.
