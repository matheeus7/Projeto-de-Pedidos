"""Service responsável pelas regras de negócio relacionadas a pedidos."""

from typing import List, Dict

from models.pedido import Pedido
from models.item_pedido import ItemPedido
from repositories.pedido_repository import PedidoRepository
from repositories.produto_repository import ProdutoRepository
from repositories.cliente_repository import ClienteRepository
from exceptions.exceptions import (
    EntidadeNaoEncontradaError,
    PedidoSemItensError,
    QuantidadeInvalidaError,
    EstoqueInsuficienteError,
    PedidoJaCanceladoError,
)


class PedidoService:
    """Concentra as regras de negócio do módulo de pedidos."""

    def __init__(
        self,
        pedido_repository: PedidoRepository = None,
        produto_repository: ProdutoRepository = None,
        cliente_repository: ClienteRepository = None,
    ):
        self._pedido_repo = pedido_repository or PedidoRepository()
        self._produto_repo = produto_repository or ProdutoRepository()
        self._cliente_repo = cliente_repository or ClienteRepository()

    def criar_pedido(self, cliente_id: int, itens: List[Dict]) -> Pedido:
        """
        Cria um pedido novo.

        `itens` deve ser uma lista de dicionários no formato:
            [{"produto_id": 1, "quantidade": 2}, ...]

        Regras aplicadas (ver exceptions.exceptions para cada uma):
            - cliente deve existir
            - pedido não pode ser criado sem itens
            - quantidade de cada item deve ser > 0
            - produto de cada item deve existir
            - estoque do produto deve ser suficiente para a quantidade pedida
            - o valor total é calculado automaticamente
            - o estoque dos produtos é reduzido automaticamente ao confirmar
        """
        cliente = self._cliente_repo.buscar_por_id(cliente_id)
        if not cliente:
            raise EntidadeNaoEncontradaError(f"Cliente #{cliente_id} não encontrado.")

        if not itens:
            raise PedidoSemItensError("Não é possível criar um pedido sem itens.")

        pedido = Pedido(cliente_id=cliente_id, cliente_nome=cliente.nome)

        for item_info in itens:
            produto_id = item_info["produto_id"]
            quantidade = item_info["quantidade"]

            if quantidade is None or quantidade <= 0:
                raise QuantidadeInvalidaError(
                    f"A quantidade do produto #{produto_id} deve ser maior que zero."
                )

            produto = self._produto_repo.buscar_por_id(produto_id)
            if not produto:
                raise EntidadeNaoEncontradaError(f"Produto #{produto_id} não encontrado.")

            if not produto.possui_estoque_suficiente(quantidade):
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para o produto '{produto.nome}'. "
                    f"Disponível: {produto.estoque}, solicitado: {quantidade}."
                )

            item = ItemPedido(
                produto_id=produto.id,
                quantidade=quantidade,
                valor_unitario=produto.preco,
                produto_nome=produto.nome,
            )
            pedido.adicionar_item(item)

        return self._pedido_repo.salvar_pedido_completo(pedido)

    def listar_pedidos(self) -> List[Pedido]:
        return self._pedido_repo.listar()

    def buscar_pedido(self, pedido_id: int) -> Pedido:
        pedido = self._pedido_repo.buscar_por_id(pedido_id)
        if not pedido:
            raise EntidadeNaoEncontradaError(f"Pedido #{pedido_id} não encontrado.")
        return pedido

    def cancelar_pedido(self, pedido_id: int) -> Pedido:
        """Cancela um pedido e devolve os itens ao estoque automaticamente."""
        pedido = self.buscar_pedido(pedido_id)
        if pedido.esta_cancelado:
            raise PedidoJaCanceladoError(f"O pedido #{pedido_id} já está cancelado.")

        self._pedido_repo.cancelar_pedido_completo(pedido)
        pedido.status = Pedido.STATUS_CANCELADO
        return pedido

    def total_vendido(self) -> float:
        return self._pedido_repo.total_vendido()
