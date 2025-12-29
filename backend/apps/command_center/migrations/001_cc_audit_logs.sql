-- UP
CREATE TABLE cc_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cc_audit_logs_user_id ON cc_audit_logs(user_id);
CREATE INDEX idx_cc_audit_logs_action ON cc_audit_logs(action);
CREATE INDEX idx_cc_audit_logs_created_at ON cc_audit_logs(created_at DESC);

-- DOWN
DROP TABLE IF EXISTS cc_audit_logs;
