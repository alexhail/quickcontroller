-- UP
CREATE TABLE user_app_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    app_id VARCHAR(50) NOT NULL,
    has_access BOOLEAN NOT NULL DEFAULT false,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, app_id)
);

CREATE INDEX idx_user_app_permissions_user_id ON user_app_permissions(user_id);
CREATE INDEX idx_user_app_permissions_app_id ON user_app_permissions(app_id);

-- DOWN
DROP TABLE IF EXISTS user_app_permissions;
