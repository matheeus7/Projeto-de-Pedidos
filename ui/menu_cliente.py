"""Submenu de gerenciamento de Clientes."""

from services.cliente_service import ClienteService
from ui.helpers import ler_texto, ler_inteiro, pausar, exibir_titulo, tratar_erro


def menu_clientes(service: ClienteService):
    while True:
        exibir_titulo("MENU CLIENTES")
        print("1 - Cadastrar cliente")
        print("2 - Listar clientes")
        print("3 - Buscar cliente por ID")
        print("4 - Atualizar cliente")
        print("5 - Excluir cliente")
        print("0 - Voltar")

        opcao = ler_texto("\nEscolha uma opção: ")

        try:
            if opcao == "1":
                _cadastrar(service)
            elif opcao == "2":
                _listar(service)
            elif opcao == "3":
                _buscar(service)
            elif opcao == "4":
                _atualizar(service)
            elif opcao == "5":
                _excluir(service)
            elif opcao == "0":
                return
            else:
                print(">> Opção inválida.")
        except Exception as erro:
            tratar_erro(erro)
            pausar()


def _cadastrar(service: ClienteService):
    exibir_titulo("CADASTRAR CLIENTE")
    nome = ler_texto("Nome: ")
    email = ler_texto("E-mail: ")
    telefone = ler_texto("Telefone (opcional): ", obrigatorio=False)

    cliente = service.cadastrar(nome, email, telefone or None)
    print(f"\n>> Cliente cadastrado com sucesso! {cliente}")
    pausar()


def _listar(service: ClienteService):
    exibir_titulo("LISTA DE CLIENTES")
    clientes = service.listar()
    if not clientes:
        print("Nenhum cliente cadastrado.")
    for cliente in clientes:
        print(cliente)
    pausar()


def _buscar(service: ClienteService):
    exibir_titulo("BUSCAR CLIENTE POR ID")
    cliente_id = ler_inteiro("ID do cliente: ")
    cliente = service.buscar_por_id(cliente_id)
    print(f"\n{cliente}")
    pausar()


def _atualizar(service: ClienteService):
    exibir_titulo("ATUALIZAR CLIENTE")
    cliente_id = ler_inteiro("ID do cliente: ")
    cliente_atual = service.buscar_por_id(cliente_id)
    print(f"Dados atuais: {cliente_atual}")

    nome = ler_texto(f"Novo nome [{cliente_atual.nome}]: ", obrigatorio=False) or cliente_atual.nome
    email = ler_texto(f"Novo e-mail [{cliente_atual.email}]: ", obrigatorio=False) or cliente_atual.email
    telefone = ler_texto(
        f"Novo telefone [{cliente_atual.telefone or '-'}]: ", obrigatorio=False
    ) or cliente_atual.telefone

    cliente = service.atualizar(cliente_id, nome, email, telefone)
    print(f"\n>> Cliente atualizado com sucesso! {cliente}")
    pausar()


def _excluir(service: ClienteService):
    exibir_titulo("EXCLUIR CLIENTE")
    cliente_id = ler_inteiro("ID do cliente: ")
    cliente = service.buscar_por_id(cliente_id)
    confirmacao = ler_texto(f"Confirma a exclusão de '{cliente.nome}'? (s/n): ").lower()
    if confirmacao == "s":
        service.excluir(cliente_id)
        print(">> Cliente excluído com sucesso!")
    else:
        print(">> Operação cancelada.")
    pausar()
