-- Adiciona colunas UUID às tabelas de notificações e dispositivos
ALTER TABLE IF EXISTS notifications_device
  ADD COLUMN IF NOT EXISTS dvc_uuid uuid;

ALTER TABLE IF EXISTS notifications_notification
  ADD COLUMN IF NOT EXISTS ntf_uuid uuid;

-- Preencher com UUIDs recém-gerados para linhas existentes
UPDATE notifications_device SET dvc_uuid = gen_random_uuid() WHERE dvc_uuid IS NULL;
UPDATE notifications_notification SET ntf_uuid = gen_random_uuid() WHERE ntf_uuid IS NULL;

-- Tornar NOT NULL e adicionar UNIQUE
ALTER TABLE notifications_device ALTER COLUMN dvc_uuid SET NOT NULL;
ALTER TABLE notifications_notification ALTER COLUMN ntf_uuid SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS notifications_device_dvc_uuid_idx ON notifications_device (dvc_uuid);
CREATE UNIQUE INDEX IF NOT EXISTS notifications_notification_ntf_uuid_idx ON notifications_notification (ntf_uuid);

-- Ajustar nomes das colunas no banco se desejar (opcional):
-- ALTER TABLE notifications_device RENAME COLUMN dvc_uuid TO uuid;
-- ALTER TABLE notifications_notification RENAME COLUMN ntf_uuid TO uuid;
