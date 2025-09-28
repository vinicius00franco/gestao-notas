-- SQL de criação para app parceiros
CREATE TABLE IF NOT EXISTS parceiros_parceiro (
    id serial PRIMARY KEY,
    nome varchar(255) NOT NULL,
    cnpj varchar(18) NOT NULL UNIQUE,
    tipo varchar(10) NOT NULL
);
