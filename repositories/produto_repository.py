"""Repository responsável pelo acesso à tabela `produtos`."""

from typing import List, Optional

from database.connection import obter_conexao
from models.produto import Produto


class ProdutoRepository:
    """Encapsula todas as operações SQL relacionadas a produtos."""

    def inserir(self, produto: Produto) -> Produto:
        sql = """
            INSERT INTO produtos (nome, descricao, preco, estoque)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql, (produto.nome, produto.descricao, produto.preco, produto.estoque)
                    )
                    produto.id = cur.fetchone()[0]
            return produto
        finally:
            conn.close()

    def buscar_por_id(self, produto_id: int, conn=None) -> Optional[Produto]:
        sql = "SELECT id, nome, descricao, preco, estoque FROM produtos WHERE id = %s"
        conexao_propria = conn is None
        conexao = conn or obter_conexao()
        try:
            with conexao.cursor() as cur:
                cur.execute(sql, (produto_id,))
                linha = cur.fetchone()
                return self._mapear(linha) if linha else None
        finally:
            if conexao_propria:
                conexao.close()

    def listar(self) -> List[Produto]:
        sql = "SELECT id, nome, descricao, preco, estoque FROM produtos ORDER BY id"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [self._mapear(linha) for linha in cur.fetchall()]
        finally:
            conn.close()

    def listar_estoque_baixo(self, limite: int = 10) -> List[Produto]:
        sql = """
            SELECT id, nome, descricao, preco, estoque
            FROM produtos
            WHERE estoque <= %s
            ORDER BY estoque ASC, nome
        """
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (limite,))
                return [self._mapear(linha) for linha in cur.fetchall()]
        finally:
            conn.close()

    def atualizar(self, produto: Produto) -> bool:
        sql = """
            UPDATE produtos
            SET nome = %s, descricao = %s, preco = %s, estoque = %s
            WHERE id = %s
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql,
                        (produto.nome, produto.descricao, produto.preco, produto.estoque, produto.id),
                    )
                    return cur.rowcount > 0
        finally:
            conn.close()

    def excluir(self, produto_id: int) -> bool:
        sql = "DELETE FROM produtos WHERE id = %s"
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (produto_id,))
                    return cur.rowcount > 0
        finally:
            conn.close()

    def possui_pedidos(self, produto_id: int) -> bool:
        """Verifica se o produto já está referenciado em algum item de pedido."""
        sql = "SELECT 1 FROM itens_pedido WHERE produto_id = %s LIMIT 1"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (produto_id,))
                return cur.fetchone() is not None
        finally:
            conn.close()

    def reduzir_estoque(self, produto_id: int, quantidade: int, conn) -> bool:
        """
        Reduz o estoque de forma segura dentro de uma transação existente.
        A cláusula WHERE estoque >= %s evita estoque negativo mesmo em
        cenários de concorrência (outro processo alterando o estoque ao
        mesmo tempo).
        """
        sql = """
            UPDATE produtos
            SET estoque = estoque - %s
            WHERE id = %s AND estoque >= %s
        """
        with conn.cursor() as cur:
            cur.execute(sql, (quantidade, produto_id, quantidade))
            return cur.rowcount > 0

    def aumentar_estoque(self, produto_id: int, quantidade: int, conn) -> bool:
        """Devolve quantidade ao estoque (usado no cancelamento de pedidos)."""
        sql = "UPDATE produtos SET estoque = estoque + %s WHERE id = %s"
        with conn.cursor() as cur:
            cur.execute(sql, (quantidade, produto_id))
            return cur.rowcount > 0

    @staticmethod
    def _mapear(linha) -> Produto:
        id_, nome, descricao, preco, estoque = linha
        return Produto(nome=nome, descricao=descricao, preco=float(preco), estoque=estoque, id=id_)
