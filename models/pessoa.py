"""
Classe abstrata Pessoa.

Define o contrato comum que toda "pessoa" do sistema deve cumprir
(Cliente e Funcionario), demonstrando o uso de classe abstrata,
encapsulamento e o ponto de extensão para o polimorfismo do método
exibir_dados().
"""

from abc import ABC, abstractmethod


class Pessoa(ABC):
    """Classe abstrata que representa uma pessoa genérica no sistema."""

    def __init__(self, nome: str, email: str = None):
        self._validar_nome(nome)
        self.__nome = nome.strip()
        self.__email = email.strip().lower() if email else None

    # ---------------------- Encapsulamento via properties ----------------------
    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, novo_nome: str):
        self._validar_nome(novo_nome)
        self.__nome = novo_nome.strip()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, novo_email: str):
        self.__email = novo_email.strip().lower() if novo_email else None

    @staticmethod
    def _validar_nome(nome: str):
        if not nome or not str(nome).strip():
            raise ValueError("O nome não pode ser vazio.")

    # ---------------------- Método abstrato (polimorfismo) ----------------------
    @abstractmethod
    def exibir_dados(self) -> str:
        """Cada subclasse deve definir como seus dados são exibidos."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.exibir_dados()
