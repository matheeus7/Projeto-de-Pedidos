"""Modelo Cliente: herda de Pessoa e é persistido na tabela `clientes`."""

from models.pessoa import Pessoa


class Cliente(Pessoa):
    """Representa um cliente da loja."""

    def __init__(self, nome: str, email: str, telefone: str = None, id: int = None):
        super().__init__(nome, email)
        self.__id = id
        self.__telefone = telefone

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def telefone(self) -> str:
        return self.__telefone

    @telefone.setter
    def telefone(self, valor: str):
        self.__telefone = valor

    # ---------------------- Polimorfismo ----------------------
    def exibir_dados(self) -> str:
        telefone = self.telefone or "não informado"
        return (
            f"Cliente #{self.id} | Nome: {self.nome} | "
            f"E-mail: {self.email} | Telefone: {telefone}"
        )

    def __str__(self) -> str:
        return self.exibir_dados()

    def __repr__(self) -> str:
        return f"Cliente(id={self.id!r}, nome={self.nome!r}, email={self.email!r})"
