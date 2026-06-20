"""Service responsável pelas regras de negócio relacionadas a clientes."""

import re
from typing import List

from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository
from exceptions.exceptions import EmailDuplicadoError, EntidadeNaoEncontradaError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClienteService:
    """Concentra as regras de negócio do módulo de clientes."""

    def __init__(self, cliente_repository: ClienteRepository = None):
        self._repo = cliente_repository or ClienteRepository()

    def cadastrar(self, nome: str, email: str, telefone: str = None) -> Cliente:
        self._validar_email(email)
        if self._repo.buscar_por_email(email):
            raise EmailDuplicadoError(f"Já existe um cliente cadastrado com o e-mail '{email}'.")

        cliente = Cliente(nome=nome, email=email, telefone=telefone)
        return self._repo.inserir(cliente)

    def listar(self) -> List[Cliente]:
        return self._repo.listar()

    def buscar_por_id(self, cliente_id: int) -> Cliente:
        cliente = self._repo.buscar_por_id(cliente_id)
        if not cliente:
            raise EntidadeNaoEncontradaError(f"Cliente #{cliente_id} não encontrado.")
        return cliente

    def atualizar(self, cliente_id: int, nome: str, email: str, telefone: str = None) -> Cliente:
        cliente = self.buscar_por_id(cliente_id)

        self._validar_email(email)
        cliente_com_mesmo_email = self._repo.buscar_por_email(email)
        if cliente_com_mesmo_email and cliente_com_mesmo_email.id != cliente_id:
            raise EmailDuplicadoError(f"Já existe um cliente cadastrado com o e-mail '{email}'.")

        cliente.nome = nome
        cliente.email = email
        cliente.telefone = telefone
        self._repo.atualizar(cliente)
        return cliente

    def excluir(self, cliente_id: int) -> None:
        self.buscar_por_id(cliente_id)  # garante que existe (lança exceção caso contrário)
        self._repo.excluir(cliente_id)

    @staticmethod
    def _validar_email(email: str):
        if not email or not EMAIL_REGEX.match(email.strip()):
            raise ValueError(f"E-mail inválido: '{email}'.")
