"""Modelo ItemPedido: persistido na tabela `itens_pedido`."""


class ItemPedido:
    """Representa um item (linha) dentro de um pedido."""

    def __init__(
        self,
        produto_id: int,
        quantidade: int,
        valor_unitario: float,
        id: int = None,
        produto_nome: str = None,
    ):
        self.__id = id
        self.__produto_id = produto_id
        self.quantidade = quantidade            # passa pelo setter
        self.valor_unitario = valor_unitario     # passa pelo setter
        self.produto_nome = produto_nome

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def produto_id(self) -> int:
        return self.__produto_id

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @quantidade.setter
    def quantidade(self, valor: int):
        if valor is None or valor <= 0:
            raise ValueError("A quantidade do item deve ser maior que zero.")
        self.__quantidade = int(valor)

    @property
    def valor_unitario(self) -> float:
        return self.__valor_unitario

    @valor_unitario.setter
    def valor_unitario(self, valor: float):
        if valor is None or valor < 0:
            raise ValueError("O valor unitário não pode ser negativo.")
        self.__valor_unitario = float(valor)

    # ---------------------- Comportamentos do domínio ----------------------
    @property
    def subtotal(self) -> float:
        return round(self.__quantidade * self.__valor_unitario, 2)

    def __str__(self) -> str:
        nome = self.produto_nome or f"Produto #{self.produto_id}"
        return (
            f"{self.quantidade}x {nome} | Unitário: R$ {self.valor_unitario:.2f} | "
            f"Subtotal: R$ {self.subtotal:.2f}"
        )

    def __repr__(self) -> str:
        return (
            f"ItemPedido(produto_id={self.produto_id!r}, "
            f"quantidade={self.quantidade!r}, valor_unitario={self.valor_unitario!r})"
        )
