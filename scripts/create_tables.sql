-- =========================================================
-- Script de criação do banco de dados - Sistema de Loja e Pedidos
-- SGBD: PostgreSQL
-- =========================================================
-- Execute este script já conectado ao banco de dados desejado
-- (ex: loja_db). Veja o README.md para instruções de criação
-- do banco antes de rodar este script.
-- =========================================================

-- Remoção segura (útil em reexecuções durante o desenvolvimento)
DROP TABLE IF EXISTS itens_pedido CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- =========================================================
-- Tabela: clientes
-- =========================================================
CREATE TABLE clientes (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(150)        NOT NULL,
    email     VARCHAR(150)        NOT NULL UNIQUE,
    telefone  VARCHAR(20)
);

-- =========================================================
-- Tabela: produtos
-- =========================================================
CREATE TABLE produtos (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(150)    NOT NULL,
    descricao   TEXT,
    preco       NUMERIC(10,2)   NOT NULL CHECK (preco >= 0),
    estoque     INTEGER         NOT NULL DEFAULT 0 CHECK (estoque >= 0)
);

-- =========================================================
-- Tabela: pedidos
-- Observação: a coluna "status" foi incluída além do solicitado
-- no enunciado original para viabilizar a regra de negócio de
-- cancelamento de pedidos (ver README.md, seção "Decisões de
-- projeto"). Valores possíveis: CONFIRMADO, CANCELADO.
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
    pedido_id       INTEGER         NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id      INTEGER         NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade      INTEGER         NOT NULL CHECK (quantidade > 0),
    valor_unitario  NUMERIC(10,2)   NOT NULL CHECK (valor_unitario >= 0)
);

-- =========================================================
-- Índices para otimizar consultas frequentes
-- =========================================================
CREATE INDEX idx_pedidos_cliente_id      ON pedidos(cliente_id);
CREATE INDEX idx_itens_pedido_pedido_id  ON itens_pedido(pedido_id);
CREATE INDEX idx_itens_pedido_produto_id ON itens_pedido(produto_id);

-- =========================================================
-- Dados de exemplo (opcionais) - facilita testes e apresentação
-- =========================================================
INSERT INTO clientes (nome, email, telefone) VALUES
    ('Ana Souza',   'ana.souza@email.com',   '92991234567'),
    ('Bruno Lima',  'bruno.lima@email.com',  '92998765432');

INSERT INTO produtos (nome, descricao, preco, estoque) VALUES
    ('Teclado Mecânico',  'Teclado mecânico ABNT2 RGB',        249.90, 15),
    ('Mouse sem Fio',     'Mouse óptico sem fio 1600dpi',       89.90, 30),
    ('Monitor 24"',       'Monitor Full HD 24 polegadas',      799.00, 8),
    ('Headset Gamer',     'Headset com microfone destacável',  159.90, 0);
