"""
Modelo PessoaJuridica: cliente pessoa jurídica.

Herda de Pessoa e adiciona os atributos específicos de uma pessoa
jurídica: CNPJ, razão social (armazenada em `nome`, herdado de Pessoa)
e nome fantasia. Implementa exibir_dados() (polimorfismo) e encapsula
todos os atributos com atributos privados e @property.

Persistência: tabela `clientes` com tipo_pessoa = 'PJ'.

Convenção de mapeamento:
    Pessoa.nome  ↔  PessoaJuridica.razao_social   (coluna `nome` do banco)
    PessoaJuridica.nome_fantasia                   (coluna `nome_fantasia`)
    PessoaJuridica.cnpj                            (coluna `cnpj`)
"""

from models.pessoa import Pessoa

TIPO_PESSOA = "PJ"


class PessoaJuridica(Pessoa):
    """Representa um cliente pessoa jurídica da loja."""

    def __init__(
        self,
        razao_social: str,
        email: str,
        cnpj: str,
        nome_fantasia: str = None,
        telefone: str = None,
        id: int = None,
    ):
        # `razao_social` é passada como `nome` para Pessoa — uso explícito de super()
        super().__init__(razao_social, email)
        self.__id = id
        self.cnpj = cnpj                        # passa pela validação do setter
        self.__nome_fantasia = nome_fantasia
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
    def razao_social(self) -> str:
        """Delega para Pessoa.nome — a razão social é o nome legal da empresa."""
        return self.nome

    @razao_social.setter
    def razao_social(self, valor: str):
        self.nome = valor   # aciona a validação e o setter de Pessoa

    @property
    def cnpj(self) -> str:
        return self.__cnpj

    @cnpj.setter
    def cnpj(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("O CNPJ não pode ser vazio.")
        self.__cnpj = valor.strip()

    @property
    def nome_fantasia(self) -> str:
        return self.__nome_fantasia

    @nome_fantasia.setter
    def nome_fantasia(self, valor: str):
        self.__nome_fantasia = valor

    @property
    def telefone(self) -> str:
        return self.__telefone

    @telefone.setter
    def telefone(self, valor: str):
        self.__telefone = valor

    # ---------------------- Polimorfismo ----------------------
    def exibir_dados(self) -> str:
        fantasia = self.nome_fantasia or "não informado"
        telefone = self.telefone or "não informado"
        return (
            f"[PJ] Cliente #{self.id} | Razão Social: {self.razao_social} | "
            f"Nome Fantasia: {fantasia} | CNPJ: {self.cnpj} | "
            f"E-mail: {self.email} | Telefone: {telefone}"
        )

    def __str__(self) -> str:
        return self.exibir_dados()

    def __repr__(self) -> str:
        return (
            f"PessoaJuridica(id={self.id!r}, razao_social={self.razao_social!r}, "
            f"cnpj={self.cnpj!r}, email={self.email!r})"
        )
