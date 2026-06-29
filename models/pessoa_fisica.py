"""
Modelo PessoaFisica: cliente pessoa física.

Herda de Pessoa e adiciona os atributos específicos de uma pessoa física:
CPF e telefone. Implementa exibir_dados() (polimorfismo) e encapsula
todos os atributos com atributos privados e @property.

Persistência: tabela `clientes` com tipo_pessoa = 'PF'.
"""

from models.pessoa import Pessoa

TIPO_PESSOA = "PF"


class PessoaFisica(Pessoa):
    """Representa um cliente pessoa física da loja."""

    def __init__(
        self,
        nome: str,
        email: str,
        cpf: str,
        telefone: str = None,
        id: int = None,
    ):
        super().__init__(nome, email)   # reutiliza validação de nome e email de Pessoa
        self.__id = id
        self.cpf = cpf                  # passa pela validação do setter
        self.__telefone = telefone

    # ---------------------- Encapsulamento ----------------------
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor: int):
        self.__id = valor

    @property
    def tipo_pessoa(self) -> str:
        return TIPO_PESSOA

    @property
    def cpf(self) -> str:
        return self.__cpf

    @cpf.setter
    def cpf(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("O CPF não pode ser vazio.")
        self.__cpf = valor.strip()

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
            f"[PF] Cliente #{self.id} | Nome: {self.nome} | "
            f"CPF: {self.cpf} | E-mail: {self.email} | Telefone: {telefone}"
        )

    def __str__(self) -> str:
        return self.exibir_dados()

    def __repr__(self) -> str:
        return (
            f"PessoaFisica(id={self.id!r}, nome={self.nome!r}, "
            f"cpf={self.cpf!r}, email={self.email!r})"
        )
