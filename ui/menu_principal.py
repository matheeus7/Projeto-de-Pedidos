"""Menu principal do sistema de Loja e Pedidos."""

from services.cliente_service import ClienteService
from services.produto_service import ProdutoService
from services.pedido_service import PedidoService

from ui.menu_cliente import menu_clientes
from ui.menu_produto import menu_produtos
from ui.menu_pedido import menu_pedidos
from ui.menu_relatorios import menu_relatorios
from ui.helpers import ler_texto, exibir_titulo, tratar_erro


def iniciar_menu_principal():
    cliente_service = ClienteService()
    produto_service = ProdutoService()
    pedido_service = PedidoService()

    while True:
        exibir_titulo("SISTEMA DE LOJA E PEDIDOS")
        print("1 - Clientes")
        print("2 - Produtos")
        print("3 - Pedidos")
        print("4 - Relatórios")
        print("0 - Sair")

        try:
            opcao = ler_texto("\nEscolha uma opção: ")

            if opcao == "1":
                menu_clientes(cliente_service)
            elif opcao == "2":
                menu_produtos(produto_service)
            elif opcao == "3":
                menu_pedidos(pedido_service)
            elif opcao == "4":
                menu_relatorios(produto_service, pedido_service)
            elif opcao == "0":
                print("\nEncerrando o sistema. Até logo!")
                break
            else:
                print(">> Opção inválida.")
        except ConnectionError as erro:
            tratar_erro(erro)
            print("\nEncerrando o sistema.")
            break
        except KeyboardInterrupt:
            print("\n\nEncerrando o sistema. Até logo!")
            break
        except Exception as erro:
            tratar_erro(erro)
