"""
Modelo Funcionario: herda de Pessoa.

Esta classe não possui tabela própria no banco de dados (o enunciado do
projeto não define uma tabela `funcionarios`), mas é mantida na
hierarquia de modelos para demonstrar, de forma concreta, a herança e o
polimorfismo do método exibir_dados() ao lado de Cliente.
"""

from models.pessoa import Pessoa


class Funcionario(Pessoa):
    """Representa um funcionário da loja (atendente, vendedor, etc.)."""

    def __init__(self, nome: str, email: str, cargo: str, salario: float, id: int = None):
        super().__init__(nome, email)
        self.__id = id
        self.__cargo = cargo
        self.salario = salario  # passa pela validação do setter

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def cargo(self) -> str:
        return self.__cargo

    @cargo.setter
    def cargo(self, valor: str):
        self.__cargo = valor

    @property
    def salario(self) -> float:
        return self.__salario

    @salario.setter
    def salario(self, valor: float):
        if valor is not None and valor < 0:
            raise ValueError("O salário não pode ser negativo.")
        self.__salario = valor

    # ---------------------- Polimorfismo ----------------------
    def exibir_dados(self) -> str:
        return (
            f"Funcionário #{self.id} | Nome: {self.nome} | "
            f"Cargo: {self.cargo} | Salário: R$ {self.salario:.2f}"
        )

    def __str__(self) -> str:
        return self.exibir_dados()

    def __repr__(self) -> str:
        return f"Funcionario(id={self.id!r}, nome={self.nome!r}, cargo={self.cargo!r})"
