"""Submenu de Relatórios."""

from services.produto_service import ProdutoService
from services.pedido_service import PedidoService
from ui.helpers import ler_texto, ler_inteiro, pausar, exibir_titulo, tratar_erro


def menu_relatorios(produto_service: ProdutoService, pedido_service: PedidoService):
    while True:
        exibir_titulo("MENU RELATÓRIOS")
        print("1 - Produtos cadastrados")
        print("2 - Produtos com estoque baixo")
        print("3 - Pedidos realizados")
        print("4 - Total vendido")
        print("0 - Voltar")

        opcao = ler_texto("\nEscolha uma opção: ")

        try:
            if opcao == "1":
                _produtos_cadastrados(produto_service)
            elif opcao == "2":
                _estoque_baixo(produto_service)
            elif opcao == "3":
                _pedidos_realizados(pedido_service)
            elif opcao == "4":
                _total_vendido(pedido_service)
            elif opcao == "0":
                return
            else:
                print(">> Opção inválida.")
        except Exception as erro:
            tratar_erro(erro)
            pausar()


def _produtos_cadastrados(service: ProdutoService):
    exibir_titulo("RELATÓRIO - PRODUTOS CADASTRADOS")
    produtos = service.listar()
    if not produtos:
        print("Nenhum produto cadastrado.")
    for produto in produtos:
        print(produto)
    print(f"\nTotal de produtos: {len(produtos)}")
    pausar()


def _estoque_baixo(service: ProdutoService):
    exibir_titulo("RELATÓRIO - PRODUTOS COM ESTOQUE BAIXO")
    limite_str = ler_texto(
        f"Limite de estoque (padrão {ProdutoService.LIMITE_ESTOQUE_BAIXO_PADRAO}): ",
        obrigatorio=False,
    )
    limite = int(limite_str) if limite_str else ProdutoService.LIMITE_ESTOQUE_BAIXO_PADRAO

    produtos = service.listar_estoque_baixo(limite)
    if not produtos:
        print(f"Nenhum produto com estoque <= {limite}.")
    for produto in produtos:
        print(produto)
    pausar()


def _pedidos_realizados(service: PedidoService):
    exibir_titulo("RELATÓRIO - PEDIDOS REALIZADOS")
    pedidos = service.listar_pedidos()
    if not pedidos:
        print("Nenhum pedido registrado.")
    for pedido in pedidos:
        print(pedido)
    print(f"\nTotal de pedidos: {len(pedidos)}")
    pausar()


def _total_vendido(service: PedidoService):
    exibir_titulo("RELATÓRIO - TOTAL VENDIDO")
    total = service.total_vendido()
    print(f"Total vendido (pedidos confirmados, excluindo cancelados): R$ {total:.2f}")
    pausar()
