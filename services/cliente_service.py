"""
Service responsável pelas regras de negócio relacionadas a clientes.

Expõe métodos distintos para Pessoa Física e Pessoa Jurídica:
    cadastrar_pf / atualizar_pf
    cadastrar_pj / atualizar_pj

As regras de negócio aplicadas são:
    - E-mail único entre todos os clientes (PF e PJ)
    - CPF único entre todas as Pessoas Físicas
    - CNPJ único entre todas as Pessoas Jurídicas
    - Validação de formato de e-mail
    - CPF e CNPJ não podem ser vazios
"""

import re
from typing import List, Union

from models.pessoa_fisica import PessoaFisica
from models.pessoa_juridica import PessoaJuridica
from repositories.cliente_repository import ClienteRepository
from exceptions.exceptions import (
    EmailDuplicadoError,
    DocumentoDuplicadoError,
    EntidadeNaoEncontradaError,
)

Cliente = Union[PessoaFisica, PessoaJuridica]

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClienteService:
    """Concentra as regras de negócio do módulo de clientes."""

    def __init__(self, cliente_repository: ClienteRepository = None):
        self._repo = cliente_repository or ClienteRepository()

    # --------------------------------------------------------- Pessoa Física
    def cadastrar_pf(
        self, nome: str, email: str, cpf: str, telefone: str = None
    ) -> PessoaFisica:
        self._validar_email(email)
        self._verificar_email_unico(email)
        self._verificar_cpf_unico(cpf)

        pf = PessoaFisica(nome=nome, email=email, cpf=cpf, telefone=telefone)
        return self._repo.inserir(pf)

    def atualizar_pf(
        self, cliente_id: int, nome: str, email: str, cpf: str, telefone: str = None
    ) -> PessoaFisica:
        cliente = self._buscar_como(cliente_id, PessoaFisica)

        self._validar_email(email)
        self._verificar_email_unico(email, excluir_id=cliente_id)
        self._verificar_cpf_unico(cpf, excluir_id=cliente_id)

        cliente.nome = nome
        cliente.email = email
        cliente.cpf = cpf
        cliente.telefone = telefone
        self._repo.atualizar(cliente)
        return cliente

    # --------------------------------------------------------- Pessoa Jurídica
    def cadastrar_pj(
        self,
        razao_social: str,
        email: str,
        cnpj: str,
        nome_fantasia: str = None,
        telefone: str = None,
    ) -> PessoaJuridica:
        self._validar_email(email)
        self._verificar_email_unico(email)
        self._verificar_cnpj_unico(cnpj)

        pj = PessoaJuridica(
            razao_social=razao_social, email=email, cnpj=cnpj,
            nome_fantasia=nome_fantasia, telefone=telefone,
        )
        return self._repo.inserir(pj)

    def atualizar_pj(
        self,
        cliente_id: int,
        razao_social: str,
        email: str,
        cnpj: str,
        nome_fantasia: str = None,
        telefone: str = None,
    ) -> PessoaJuridica:
        cliente = self._buscar_como(cliente_id, PessoaJuridica)

        self._validar_email(email)
        self._verificar_email_unico(email, excluir_id=cliente_id)
        self._verificar_cnpj_unico(cnpj, excluir_id=cliente_id)

        cliente.razao_social = razao_social
        cliente.email = email
        cliente.cnpj = cnpj
        cliente.nome_fantasia = nome_fantasia
        cliente.telefone = telefone
        self._repo.atualizar(cliente)
        return cliente

    # --------------------------------------------------------- Comuns a PF e PJ
    def listar(self) -> List[Cliente]:
        return self._repo.listar()

    def buscar_por_id(self, cliente_id: int) -> Cliente:
        cliente = self._repo.buscar_por_id(cliente_id)
        if not cliente:
            raise EntidadeNaoEncontradaError(f"Cliente #{cliente_id} não encontrado.")
        return cliente

    def excluir(self, cliente_id: int) -> None:
        self.buscar_por_id(cliente_id)   # garante que existe
        self._repo.excluir(cliente_id)

    # --------------------------------------------------------- Helpers privados
    def _buscar_como(self, cliente_id: int, tipo_esperado: type) -> Cliente:
        """Busca o cliente e garante que é do tipo esperado (PF ou PJ)."""
        cliente = self.buscar_por_id(cliente_id)
        if not isinstance(cliente, tipo_esperado):
            tipo_real = "Pessoa Física" if isinstance(cliente, PessoaFisica) else "Pessoa Jurídica"
            tipo_exp = "Pessoa Física" if tipo_esperado is PessoaFisica else "Pessoa Jurídica"
            raise ValueError(
                f"O cliente #{cliente_id} é {tipo_real}, não {tipo_exp}. "
                "O tipo de pessoa não pode ser alterado após o cadastro."
            )
        return cliente

    def _verificar_email_unico(self, email: str, excluir_id: int = None):
        existente = self._repo.buscar_por_email(email)
        if existente and existente.id != excluir_id:
            raise EmailDuplicadoError(
                f"Já existe um cliente cadastrado com o e-mail '{email}'."
            )

    def _verificar_cpf_unico(self, cpf: str, excluir_id: int = None):
        existente = self._repo.buscar_por_cpf(cpf)
        if existente and existente.id != excluir_id:
            raise DocumentoDuplicadoError(
                f"Já existe um cliente cadastrado com o CPF '{cpf}'."
            )

    def _verificar_cnpj_unico(self, cnpj: str, excluir_id: int = None):
        existente = self._repo.buscar_por_cnpj(cnpj)
        if existente and existente.id != excluir_id:
            raise DocumentoDuplicadoError(
                f"Já existe um cliente cadastrado com o CNPJ '{cnpj}'."
            )

    @staticmethod
    def _validar_email(email: str):
        if not email or not EMAIL_REGEX.match(email.strip()):
            raise ValueError(f"E-mail inválido: '{email}'.")
