-- SQL de criação para app empresa
CREATE TABLE IF NOT EXISTS empresa_minhaempresa (
    id serial PRIMARY KEY,
    nome varchar(255) NOT NULL DEFAULT 'Minha Empresa',
    cnpj varchar(18) NOT NULL UNIQUE
);
