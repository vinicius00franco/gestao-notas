-- SQL de criação para app financeiro
CREATE TABLE IF NOT EXISTS financeiro_lancamentofinanceiro (
    id serial PRIMARY KEY,
    nota_fiscal_id integer NOT NULL UNIQUE,
    descricao varchar(255) NOT NULL,
    valor numeric(10,2) NOT NULL,
    tipo varchar(10) NOT NULL,
    status varchar(10) NOT NULL DEFAULT 'PENDENTE',
    data_vencimento date NOT NULL,
    data_pagamento date NULL,
    CONSTRAINT fk_nota_fiscal FOREIGN KEY (nota_fiscal_id) REFERENCES notas_notafiscal(id) ON DELETE CASCADE
);
