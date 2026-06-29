"""
Repository responsável pelo acesso à tabela `clientes`.

A tabela `clientes` armazena tanto Pessoa Física quanto Pessoa Jurídica
por meio da coluna discriminadora `tipo_pessoa` ('PF' ou 'PJ').
O método _mapear() retorna a subclasse correta com base nessa coluna,
de modo que a camada de Services e UI sempre recebe um objeto tipado
(PessoaFisica ou PessoaJuridica) e pode usar isinstance() para
distingui-los quando necessário.

Colunas utilizadas:
    id, nome, email, telefone, tipo_pessoa   — comuns a PF e PJ
    cpf                                      — exclusivo de PF
    cnpj, nome_fantasia                      — exclusivos de PJ
"""

from typing import List, Optional, Union

from database.connection import obter_conexao
from models.pessoa_fisica import PessoaFisica
from models.pessoa_juridica import PessoaJuridica

Cliente = Union[PessoaFisica, PessoaJuridica]   # alias de tipo para legibilidade

_COLUNAS = "id, nome, email, telefone, tipo_pessoa, cpf, cnpj, nome_fantasia"


class ClienteRepository:
    """Encapsula todas as operações SQL relacionadas a clientes."""

    # ------------------------------------------------------------------ INSERT
    def inserir(self, cliente: Cliente) -> Cliente:
        sql = f"""
            INSERT INTO clientes
                (nome, email, telefone, tipo_pessoa, cpf, cnpj, nome_fantasia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, _valores_para_insert(cliente))
                    cliente.id = cur.fetchone()[0]
            return cliente
        finally:
            conn.close()

    # ------------------------------------------------------------------ SELECT
    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        sql = f"SELECT {_COLUNAS} FROM clientes WHERE id = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (cliente_id,))
                linha = cur.fetchone()
                return _mapear(linha) if linha else None
        finally:
            conn.close()

    def buscar_por_email(self, email: str) -> Optional[Cliente]:
        sql = f"SELECT {_COLUNAS} FROM clientes WHERE email = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (email.strip().lower(),))
                linha = cur.fetchone()
                return _mapear(linha) if linha else None
        finally:
            conn.close()

    def buscar_por_cpf(self, cpf: str) -> Optional[PessoaFisica]:
        sql = f"SELECT {_COLUNAS} FROM clientes WHERE cpf = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (cpf.strip(),))
                linha = cur.fetchone()
                return _mapear(linha) if linha else None
        finally:
            conn.close()

    def buscar_por_cnpj(self, cnpj: str) -> Optional[PessoaJuridica]:
        sql = f"SELECT {_COLUNAS} FROM clientes WHERE cnpj = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (cnpj.strip(),))
                linha = cur.fetchone()
                return _mapear(linha) if linha else None
        finally:
            conn.close()

    def listar(self) -> List[Cliente]:
        sql = f"SELECT {_COLUNAS} FROM clientes ORDER BY id"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [_mapear(linha) for linha in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------ UPDATE
    def atualizar(self, cliente: Cliente) -> bool:
        sql = """
            UPDATE clientes
            SET nome = %s, email = %s, telefone = %s, cpf = %s,
                cnpj = %s, nome_fantasia = %s
            WHERE id = %s
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, _valores_para_update(cliente))
                    return cur.rowcount > 0
        finally:
            conn.close()

    # ------------------------------------------------------------------ DELETE
    def excluir(self, cliente_id: int) -> bool:
        sql = "DELETE FROM clientes WHERE id = %s"
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (cliente_id,))
                    return cur.rowcount > 0
        finally:
            conn.close()


# ---------------------------------------------------------------- helpers privados

def _valores_para_insert(cliente: Cliente) -> tuple:
    """Monta a tupla de valores para o INSERT respeitando o tipo de pessoa."""
    if isinstance(cliente, PessoaFisica):
        return (
            cliente.nome, cliente.email, cliente.telefone,
            "PF", cliente.cpf, None, None,
        )
    # PessoaJuridica
    return (
        cliente.razao_social, cliente.email, cliente.telefone,
        "PJ", None, cliente.cnpj, cliente.nome_fantasia,
    )


def _valores_para_update(cliente: Cliente) -> tuple:
    """Monta a tupla de valores para o UPDATE (mesmos campos, mais o id no final)."""
    if isinstance(cliente, PessoaFisica):
        return (
            cliente.nome, cliente.email, cliente.telefone,
            cliente.cpf, None, None,
            cliente.id,
        )
    return (
        cliente.razao_social, cliente.email, cliente.telefone,
        None, cliente.cnpj, cliente.nome_fantasia,
        cliente.id,
    )


def _mapear(linha) -> Cliente:
    """
    Converte uma linha do banco em PessoaFisica ou PessoaJuridica
    com base no discriminador tipo_pessoa — polimorfismo no mapeamento O/R.
    """
    id_, nome, email, telefone, tipo_pessoa, cpf, cnpj, nome_fantasia = linha

    if tipo_pessoa == "PF":
        return PessoaFisica(
            nome=nome, email=email, cpf=cpf or "",
            telefone=telefone, id=id_,
        )
    # PJ
    return PessoaJuridica(
        razao_social=nome, email=email, cnpj=cnpj or "",
        nome_fantasia=nome_fantasia, telefone=telefone, id=id_,
    )
