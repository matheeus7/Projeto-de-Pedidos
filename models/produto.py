"""Modelo Produto: persistido na tabela `produtos`."""


class Produto:
    """Representa um produto comercializado pela loja."""

    def __init__(self, nome: str, descricao: str, preco: float, estoque: int, id: int = None):
        self.__id = id
        self.nome = nome
        self.__descricao = descricao
        self.preco = preco        # passa pelo setter (valida preço >= 0)
        self.estoque = estoque    # passa pelo setter (valida estoque >= 0)

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("O nome do produto não pode ser vazio.")
        self.__nome = valor.strip()

    @property
    def descricao(self) -> str:
        return self.__descricao

    @descricao.setter
    def descricao(self, valor: str):
        self.__descricao = valor

    @property
    def preco(self) -> float:
        return self.__preco

    @preco.setter
    def preco(self, valor: float):
        if valor is None or valor < 0:
            raise ValueError("O preço do produto não pode ser negativo.")
        self.__preco = float(valor)

    @property
    def estoque(self) -> int:
        return self.__estoque

    @estoque.setter
    def estoque(self, valor: int):
        if valor is None or valor < 0:
            raise ValueError("O estoque do produto não pode ser negativo.")
        self.__estoque = int(valor)

    # ---------------------- Comportamentos do domínio ----------------------
    def possui_estoque_suficiente(self, quantidade: int) -> bool:
        return quantidade <= self.__estoque

    def reduzir_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a reduzir deve ser maior que zero.")
        if not self.possui_estoque_suficiente(quantidade):
            raise ValueError("Estoque insuficiente para a operação.")
        self.__estoque -= quantidade

    def aumentar_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a adicionar deve ser maior que zero.")
        self.__estoque += quantidade

    def __str__(self) -> str:
        return (
            f"Produto #{self.id} | {self.nome} | R$ {self.preco:.2f} | "
            f"Estoque: {self.estoque}"
        )

    def __repr__(self) -> str:
        return f"Produto(id={self.id!r}, nome={self.nome!r}, preco={self.preco!r})"
