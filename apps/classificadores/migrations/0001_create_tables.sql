-- SQL de criação para tabela de classificadores
CREATE TABLE IF NOT EXISTS geral_classificadores (
    id serial PRIMARY KEY,
    tipo varchar(50) NOT NULL,
    codigo varchar(50) NOT NULL,
    descricao varchar(255) NOT NULL,
    CONSTRAINT uq_tipo_codigo UNIQUE (tipo, codigo)
);
