"""Service responsável pelas regras de negócio relacionadas a produtos."""

from typing import List

from models.produto import Produto
from repositories.produto_repository import ProdutoRepository
from exceptions.exceptions import (
    EntidadeNaoEncontradaError,
    PrecoInvalidoError,
    EstoqueInvalidoError,
    ProdutoComPedidosError,
)


class ProdutoService:
    """Concentra as regras de negócio do módulo de produtos."""

    LIMITE_ESTOQUE_BAIXO_PADRAO = 5

    def __init__(self, produto_repository: ProdutoRepository = None):
        self._repo = produto_repository or ProdutoRepository()

    def cadastrar(self, nome: str, descricao: str, preco: float, estoque: int) -> Produto:
        self._validar_preco(preco)
        self._validar_estoque(estoque)
        produto = Produto(nome=nome, descricao=descricao, preco=preco, estoque=estoque)
        return self._repo.inserir(produto)

    def listar(self) -> List[Produto]:
        return self._repo.listar()

    def buscar_por_id(self, produto_id: int) -> Produto:
        produto = self._repo.buscar_por_id(produto_id)
        if not produto:
            raise EntidadeNaoEncontradaError(f"Produto #{produto_id} não encontrado.")
        return produto

    def atualizar(
        self, produto_id: int, nome: str, descricao: str, preco: float, estoque: int
    ) -> Produto:
        produto = self.buscar_por_id(produto_id)
        self._validar_preco(preco)
        self._validar_estoque(estoque)

        produto.nome = nome
        produto.descricao = descricao
        produto.preco = preco
        produto.estoque = estoque
        self._repo.atualizar(produto)
        return produto

    def excluir(self, produto_id: int) -> None:
        self.buscar_por_id(produto_id)  # garante que existe
        if self._repo.possui_pedidos(produto_id):
            raise ProdutoComPedidosError(
                f"O produto #{produto_id} não pode ser excluído pois já está "
                "associado a um ou mais pedidos."
            )
        self._repo.excluir(produto_id)

    def listar_estoque_baixo(self, limite: int = LIMITE_ESTOQUE_BAIXO_PADRAO) -> List[Produto]:
        return self._repo.listar_estoque_baixo(limite)

    @staticmethod
    def _validar_preco(preco: float):
        if preco is None or preco < 0:
            raise PrecoInvalidoError("O preço do produto não pode ser negativo.")

    @staticmethod
    def _validar_estoque(estoque: int):
        if estoque is None or estoque < 0:
            raise EstoqueInvalidoError("O estoque do produto não pode ser negativo.")
