"""Repository responsável pelo acesso às tabelas `pedidos` e `itens_pedido`."""

from typing import List, Optional

from database.connection import obter_conexao
from models.pedido import Pedido
from models.item_pedido import ItemPedido
from repositories.produto_repository import ProdutoRepository


class PedidoRepository:
    """Encapsula todas as operações SQL relacionadas a pedidos e seus itens."""

    def __init__(self):
        self._produto_repo = ProdutoRepository()

    def salvar_pedido_completo(self, pedido: Pedido) -> Pedido:
        """
        Persiste o pedido, todos os seus itens e dá baixa no estoque dos
        produtos correspondentes em uma única transação atômica: ou tudo
        é gravado com sucesso, ou nada é alterado no banco (rollback).
        """
        sql_inserir_pedido = """
            INSERT INTO pedidos (cliente_id, data_pedido, valor_total, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        sql_inserir_item = """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, valor_unitario)
            VALUES (%s, %s, %s, %s)
        """

        conn = obter_conexao()
        try:
            with conn:  # commit automático ao sair do bloco sem erros, rollback em caso de exceção
                with conn.cursor() as cur:
                    cur.execute(
                        sql_inserir_pedido,
                        (pedido.cliente_id, pedido.data_pedido, pedido.valor_total, pedido.status),
                    )
                    pedido_id = cur.fetchone()[0]
                    pedido.id = pedido_id

                    for item in pedido.itens:
                        cur.execute(
                            sql_inserir_item,
                            (pedido_id, item.produto_id, item.quantidade, item.valor_unitario),
                        )

                        baixou_estoque = self._produto_repo.reduzir_estoque(
                            item.produto_id, item.quantidade, conn
                        )
                        if not baixou_estoque:
                            # Provoca rollback de toda a transação: estoque insuficiente
                            raise ValueError(
                                f"Estoque insuficiente para o produto #{item.produto_id} "
                                "no momento da confirmação do pedido."
                            )
            return pedido
        finally:
            conn.close()

    def buscar_por_id(self, pedido_id: int) -> Optional[Pedido]:
        sql_pedido = """
            SELECT p.id, p.cliente_id, p.data_pedido, p.status, c.nome
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id
            WHERE p.id = %s
        """
        sql_itens = """
            SELECT i.id, i.produto_id, i.quantidade, i.valor_unitario, pr.nome
            FROM itens_pedido i
            JOIN produtos pr ON pr.id = i.produto_id
            WHERE i.pedido_id = %s
            ORDER BY i.id
        """
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql_pedido, (pedido_id,))
                linha_pedido = cur.fetchone()
                if not linha_pedido:
                    return None

                cur.execute(sql_itens, (pedido_id,))
                linhas_itens = cur.fetchall()

            return self._mapear_pedido(linha_pedido, linhas_itens)
        finally:
            conn.close()

    def listar(self) -> List[Pedido]:
        sql = """
            SELECT p.id, p.cliente_id, p.data_pedido, p.status, c.nome
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id
            ORDER BY p.id DESC
        """
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                linhas = cur.fetchall()
        finally:
            conn.close()

        # Para cada pedido, busca seus itens (poderia ser otimizado com uma única
        # consulta agregada, mas a versão atual prioriza clareza didática).
        return [self.buscar_por_id(linha[0]) for linha in linhas]

    def atualizar_status(self, pedido_id: int, status: str) -> bool:
        sql = "UPDATE pedidos SET status = %s WHERE id = %s"
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (status, pedido_id))
                    return cur.rowcount > 0
        finally:
            conn.close()

    def cancelar_pedido_completo(self, pedido: Pedido) -> bool:
        """
        Cancela um pedido e devolve ao estoque a quantidade de cada item,
        também em uma única transação atômica.
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE pedidos SET status = %s WHERE id = %s",
                        (Pedido.STATUS_CANCELADO, pedido.id),
                    )
                    if cur.rowcount == 0:
                        return False

                for item in pedido.itens:
                    self._produto_repo.aumentar_estoque(item.produto_id, item.quantidade, conn)
            return True
        finally:
            conn.close()

    def total_vendido(self) -> float:
        """Soma o valor_total de todos os pedidos não cancelados."""
        sql = "SELECT COALESCE(SUM(valor_total), 0) FROM pedidos WHERE status != %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (Pedido.STATUS_CANCELADO,))
                return float(cur.fetchone()[0])
        finally:
            conn.close()

    @staticmethod
    def _mapear_pedido(linha_pedido, linhas_itens) -> Pedido:
        id_, cliente_id, data_pedido, status, cliente_nome = linha_pedido
        pedido = Pedido(
            cliente_id=cliente_id,
            id=id_,
            data_pedido=data_pedido,
            status=status,
            cliente_nome=cliente_nome,
        )
        for item_id, produto_id, quantidade, valor_unitario, produto_nome in linhas_itens:
            item = ItemPedido(
                produto_id=produto_id,
                quantidade=quantidade,
                valor_unitario=float(valor_unitario),
                id=item_id,
                produto_nome=produto_nome,
            )
            pedido.adicionar_item(item)
        return pedido
