-- SQL de criação para app notas
CREATE TABLE IF NOT EXISTS notas_notafiscal (
    id serial PRIMARY KEY,
    job_origem_id integer NOT NULL,
    parceiro_id integer NOT NULL,
    numero varchar(100) NOT NULL,
    data_emissao date NOT NULL,
    valor_total numeric(10,2) NOT NULL,
    CONSTRAINT fk_job_origem FOREIGN KEY (job_origem_id) REFERENCES processamento_jobprocessamento(id) ON DELETE PROTECT,
    CONSTRAINT fk_parceiro FOREIGN KEY (parceiro_id) REFERENCES parceiros_parceiro(id) ON DELETE CASCADE
);
