-- UP
CREATE TYPE connection_status AS ENUM ('online', 'offline', 'connecting', 'error');

CREATE TABLE master_controllers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    connection_status connection_status NOT NULL DEFAULT 'offline',
    last_seen TIMESTAMPTZ,
    last_error TEXT,
    ha_version VARCHAR(50),
    discovered_via VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, url)
);

CREATE INDEX idx_master_controllers_user_id ON master_controllers(user_id);

-- DOWN
DROP TABLE IF EXISTS master_controllers;
DROP TYPE IF EXISTS connection_status;
