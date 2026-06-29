-- =========================================================
-- Script de criação do banco de dados - Sistema de Loja e Pedidos
-- SGBD: PostgreSQL
-- =========================================================

DROP TABLE IF EXISTS itens_pedido CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- =========================================================
-- Tabela: clientes
-- Armazena Pessoa Física (tipo_pessoa='PF') e
--          Pessoa Jurídica (tipo_pessoa='PJ') na mesma tabela.
--
-- Campos por tipo:
--   PF  → nome, email, telefone, cpf
--   PJ  → nome (= razao_social), email, telefone, cnpj, nome_fantasia
-- =========================================================
CREATE TABLE clientes (
    id            SERIAL       PRIMARY KEY,
    nome          VARCHAR(200) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    telefone      VARCHAR(20),
    tipo_pessoa   CHAR(2)      NOT NULL DEFAULT 'PF'
                               CHECK (tipo_pessoa IN ('PF', 'PJ')),
    -- Pessoa Física
    cpf           VARCHAR(14)  UNIQUE,
    -- Pessoa Jurídica
    cnpj          VARCHAR(18)  UNIQUE,
    nome_fantasia VARCHAR(200),
    -- Restrição: PF deve ter CPF, PJ deve ter CNPJ
    CONSTRAINT chk_pf_tem_cpf  CHECK (tipo_pessoa <> 'PF' OR cpf  IS NOT NULL),
    CONSTRAINT chk_pj_tem_cnpj CHECK (tipo_pessoa <> 'PJ' OR cnpj IS NOT NULL)
);

-- =========================================================
-- Tabela: produtos
-- =========================================================
CREATE TABLE produtos (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(150)  NOT NULL,
    descricao   TEXT,
    preco       NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
    estoque     INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

-- =========================================================
-- Tabela: pedidos
-- =========================================================
CREATE TABLE pedidos (
    id            SERIAL PRIMARY KEY,
    cliente_id    INTEGER         NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    data_pedido   TIMESTAMP       NOT NULL DEFAULT NOW(),
    valor_total   NUMERIC(10,2)   NOT NULL DEFAULT 0 CHECK (valor_total >= 0),
    status        VARCHAR(20)     NOT NULL DEFAULT 'CONFIRMADO'
);

-- =========================================================
-- Tabela: itens_pedido
-- =========================================================
CREATE TABLE itens_pedido (
    id              SERIAL PRIMARY KEY,
    pedido_id       INTEGER         NOT NULL REFERENCES pedidos(id)   ON DELETE CASCADE,
    produto_id      INTEGER         NOT NULL REFERENCES produtos(id)  ON DELETE RESTRICT,
    quantidade      INTEGER         NOT NULL CHECK (quantidade > 0),
    valor_unitario  NUMERIC(10,2)   NOT NULL CHECK (valor_unitario >= 0)
);

-- =========================================================
-- Índices
-- =========================================================
CREATE INDEX idx_pedidos_cliente_id      ON pedidos(cliente_id);
CREATE INDEX idx_itens_pedido_pedido_id  ON itens_pedido(pedido_id);
CREATE INDEX idx_itens_pedido_produto_id ON itens_pedido(produto_id);

-- =========================================================
-- Dados de exemplo
-- =========================================================
INSERT INTO clientes (nome, email, telefone, tipo_pessoa, cpf) VALUES
    ('Ana Souza',  'ana.souza@email.com',  '92991234567', 'PF', '123.456.789-00');

INSERT INTO clientes (nome, email, telefone, tipo_pessoa, cnpj, nome_fantasia) VALUES
    ('Tech Distribuidora Ltda', 'contato@techdist.com.br', '92933334444',
     'PJ', '12.345.678/0001-99', 'TechDist');

INSERT INTO produtos (nome, descricao, preco, estoque) VALUES
    ('Teclado Mecânico',  'Teclado mecânico ABNT2 RGB',       249.90, 15),
    ('Mouse sem Fio',     'Mouse óptico sem fio 1600dpi',      89.90, 30),
    ('Monitor 24"',       'Monitor Full HD 24 polegadas',     799.00,  8),
    ('Headset Gamer',     'Headset com microfone destacável', 159.90,  0);
