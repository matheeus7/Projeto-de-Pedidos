"""Submenu de gerenciamento de Pedidos."""

from services.pedido_service import PedidoService
from ui.helpers import ler_texto, ler_inteiro, pausar, exibir_titulo, tratar_erro


def menu_pedidos(service: PedidoService):
    while True:
        exibir_titulo("MENU PEDIDOS")
        print("1 - Criar novo pedido")
        print("2 - Listar pedidos")
        print("3 - Consultar pedido por ID")
        print("4 - Cancelar pedido")
        print("0 - Voltar")

        opcao = ler_texto("\nEscolha uma opção: ")

        try:
            if opcao == "1":
                _criar_pedido(service)
            elif opcao == "2":
                _listar(service)
            elif opcao == "3":
                _consultar(service)
            elif opcao == "4":
                _cancelar(service)
            elif opcao == "0":
                return
            else:
                print(">> Opção inválida.")
        except Exception as erro:
            tratar_erro(erro)
            pausar()


def _criar_pedido(service: PedidoService):
    exibir_titulo("NOVO PEDIDO")
    cliente_id = ler_inteiro("ID do cliente: ")

    itens = []
    print("\nAdicione os itens do pedido (digite 0 no ID do produto para finalizar):")
    while True:
        produto_id = ler_inteiro(f"\nItem {len(itens) + 1} - ID do produto (0 para finalizar): ")
        if produto_id == 0:
            break
        quantidade = ler_inteiro("Quantidade: ")
        itens.append({"produto_id": produto_id, "quantidade": quantidade})

    pedido = service.criar_pedido(cliente_id, itens)
    print(f"\n>> Pedido criado com sucesso!\n{pedido}")
    for item in pedido.itens:
        print(f"   - {item}")
    pausar()


def _listar(service: PedidoService):
    exibir_titulo("LISTA DE PEDIDOS")
    pedidos = service.listar_pedidos()
    if not pedidos:
        print("Nenhum pedido registrado.")
    for pedido in pedidos:
        print(pedido)
    pausar()


def _consultar(service: PedidoService):
    exibir_titulo("CONSULTAR PEDIDO")
    pedido_id = ler_inteiro("ID do pedido: ")
    pedido = service.buscar_pedido(pedido_id)
    print(f"\n{pedido}")
    print("Itens:")
    for item in pedido.itens:
        print(f"   - {item}")
    pausar()


def _cancelar(service: PedidoService):
    exibir_titulo("CANCELAR PEDIDO")
    pedido_id = ler_inteiro("ID do pedido: ")
    pedido = service.buscar_pedido(pedido_id)
    confirmacao = ler_texto(
        f"Confirma o cancelamento do pedido #{pedido.id} (total R$ {pedido.valor_total:.2f})? (s/n): "
    ).lower()
    if confirmacao == "s":
        service.cancelar_pedido(pedido_id)
        print(">> Pedido cancelado com sucesso! O estoque dos itens foi restaurado.")
    else:
        print(">> Operação cancelada.")
    pausar()
