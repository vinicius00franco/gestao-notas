-- SQL de criação para app processamento
CREATE TABLE IF NOT EXISTS processamento_jobprocessamento (
    id serial PRIMARY KEY,
    arquivo_original varchar(255) NOT NULL,
    meu_cnpj varchar(18) NOT NULL,
    status varchar(12) NOT NULL DEFAULT 'PENDENTE',
    dt_criacao timestamptz NOT NULL DEFAULT now(),
    dt_conclusao timestamptz NULL,
    mensagem_erro text NULL
);
