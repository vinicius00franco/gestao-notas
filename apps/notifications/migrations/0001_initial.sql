-- Create notifications_device table
CREATE TABLE notifications_device (
    dvc_id BIGSERIAL PRIMARY KEY,
    dvc_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES auth_user(id) ON DELETE CASCADE,
    empresa_id BIGINT REFERENCES cadastro_empresas(emp_id) ON DELETE CASCADE,
    token VARCHAR(512) NOT NULL UNIQUE,
    platform VARCHAR(16),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create notifications_notification table
CREATE TABLE notifications_notification (
    ntf_id BIGSERIAL PRIMARY KEY,
    ntf_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    delivered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE
);