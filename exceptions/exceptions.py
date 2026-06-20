"""
Exceções customizadas do domínio da aplicação.

Cada exceção representa a violação de uma regra de negócio específica
e é lançada exclusivamente pela camada de Services, permitindo que a
camada de UI trate cada caso com uma mensagem clara para o usuário.
"""


class RegraDeNegocioError(Exception):
    """Classe base para todas as exceções de regras de negócio do sistema."""
    pass


class EntidadeNaoEncontradaError(RegraDeNegocioError):
    """Lançada quando um registro buscado por id não existe no banco."""
    pass


class EmailDuplicadoError(RegraDeNegocioError):
    """Lançada ao tentar cadastrar/atualizar um cliente com e-mail já existente."""
    pass


class PrecoInvalidoError(RegraDeNegocioError):
    """Lançada quando um produto recebe um preço negativo."""
    pass


class EstoqueInvalidoError(RegraDeNegocioError):
    """Lançada quando um produto recebe uma quantidade de estoque negativa."""
    pass


class EstoqueInsuficienteError(RegraDeNegocioError):
    """Lançada quando a quantidade solicitada excede o estoque disponível."""
    pass


class QuantidadeInvalidaError(RegraDeNegocioError):
    """Lançada quando a quantidade de um item de pedido é menor ou igual a zero."""
    pass


class PedidoSemItensError(RegraDeNegocioError):
    """Lançada ao tentar criar um pedido sem nenhum item."""
    pass


class ProdutoComPedidosError(RegraDeNegocioError):
    """Lançada ao tentar excluir um produto que já está associado a pedidos."""
    pass


class PedidoJaCanceladoError(RegraDeNegocioError):
    """Lançada ao tentar cancelar um pedido que já está cancelado."""
    pass
