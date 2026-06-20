"""Modelo Pedido: persistido na tabela `pedidos`, agrega ItemPedido."""

from datetime import datetime
from typing import List, Optional

from models.item_pedido import ItemPedido


class Pedido:
    """Representa um pedido feito por um cliente, composto por itens."""

    STATUS_CONFIRMADO = "CONFIRMADO"
    STATUS_CANCELADO = "CANCELADO"

    def __init__(
        self,
        cliente_id: int,
        id: int = None,
        data_pedido: Optional[datetime] = None,
        itens: Optional[List[ItemPedido]] = None,
        status: str = STATUS_CONFIRMADO,
        cliente_nome: str = None,
    ):
        self.__id = id
        self.__cliente_id = cliente_id
        self.cliente_nome = cliente_nome
        self.__data_pedido = data_pedido or datetime.now()
        self.__itens: List[ItemPedido] = list(itens) if itens else []
        self.__status = status

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def cliente_id(self) -> int:
        return self.__cliente_id

    @property
    def data_pedido(self) -> datetime:
        return self.__data_pedido

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, valor: str):
        self.__status = valor

    @property
    def itens(self) -> List[ItemPedido]:
        # Retorna uma cópia para não permitir alteração direta da lista interna
        return list(self.__itens)

    # ---------------------- Comportamentos do domínio ----------------------
    def adicionar_item(self, item: ItemPedido):
        if not isinstance(item, ItemPedido):
            raise TypeError("Apenas instâncias de ItemPedido podem ser adicionadas.")
        self.__itens.append(item)

    @property
    def valor_total(self) -> float:
        return round(sum(item.subtotal for item in self.__itens), 2)

    @property
    def esta_cancelado(self) -> bool:
        return self.__status == Pedido.STATUS_CANCELADO

    def __str__(self) -> str:
        data_formatada = self.data_pedido.strftime("%d/%m/%Y %H:%M")
        cliente = self.cliente_nome or f"Cliente #{self.cliente_id}"
        return (
            f"Pedido #{self.id} | {cliente} | Data: {data_formatada} | "
            f"Itens: {len(self.__itens)} | Total: R$ {self.valor_total:.2f} | "
            f"Status: {self.status}"
        )

    def __repr__(self) -> str:
        return f"Pedido(id={self.id!r}, cliente_id={self.cliente_id!r}, status={self.status!r})"
