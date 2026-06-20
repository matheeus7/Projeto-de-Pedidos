"""Repository responsável pelo acesso à tabela `clientes`."""

from typing import List, Optional

from database.connection import obter_conexao
from models.cliente import Cliente


class ClienteRepository:
    """Encapsula todas as operações SQL relacionadas a clientes."""

    def inserir(self, cliente: Cliente) -> Cliente:
        sql = """
            INSERT INTO clientes (nome, email, telefone)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (cliente.nome, cliente.email, cliente.telefone))
                    cliente.id = cur.fetchone()[0]
            return cliente
        finally:
            conn.close()

    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        sql = "SELECT id, nome, email, telefone FROM clientes WHERE id = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (cliente_id,))
                linha = cur.fetchone()
                return self._mapear(linha) if linha else None
        finally:
            conn.close()

    def buscar_por_email(self, email: str) -> Optional[Cliente]:
        sql = "SELECT id, nome, email, telefone FROM clientes WHERE email = %s"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (email.strip().lower(),))
                linha = cur.fetchone()
                return self._mapear(linha) if linha else None
        finally:
            conn.close()

    def listar(self) -> List[Cliente]:
        sql = "SELECT id, nome, email, telefone FROM clientes ORDER BY id"
        conn = obter_conexao()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [self._mapear(linha) for linha in cur.fetchall()]
        finally:
            conn.close()

    def atualizar(self, cliente: Cliente) -> bool:
        sql = """
            UPDATE clientes
            SET nome = %s, email = %s, telefone = %s
            WHERE id = %s
        """
        conn = obter_conexao()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (cliente.nome, cliente.email, cliente.telefone, cliente.id))
                    return cur.rowcount > 0
        finally:
            conn.close()

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

    @staticmethod
    def _mapear(linha) -> Cliente:
        id_, nome, email, telefone = linha
        return Cliente(nome=nome, email=email, telefone=telefone, id=id_)
