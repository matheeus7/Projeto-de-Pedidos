"""
Submenu de gerenciamento de Clientes.

Distingue Pessoa Física (CPF) de Pessoa Jurídica (CNPJ) no cadastro
e na atualização. A listagem e exclusão são comuns a ambos os tipos.
"""

from models.pessoa_fisica import PessoaFisica
from models.pessoa_juridica import PessoaJuridica
from services.cliente_service import ClienteService
from ui.helpers import ler_texto, ler_inteiro, pausar, exibir_titulo, tratar_erro


def menu_clientes(service: ClienteService):
    while True:
        exibir_titulo("MENU CLIENTES")
        print("1 - Cadastrar cliente (PF ou PJ)")
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


# ------------------------------------------------------------------ cadastrar
def _cadastrar(service: ClienteService):
    exibir_titulo("CADASTRAR CLIENTE")
    print("Tipo de pessoa:")
    print("  1 - Pessoa Física  (CPF)")
    print("  2 - Pessoa Jurídica (CNPJ)")
    tipo = ler_texto("Escolha (1 ou 2): ")

    if tipo == "1":
        _cadastrar_pf(service)
    elif tipo == "2":
        _cadastrar_pj(service)
    else:
        print(">> Tipo inválido. Operação cancelada.")


def _cadastrar_pf(service: ClienteService):
    print("\n-- Pessoa Física --")
    nome = ler_texto("Nome completo: ")
    cpf = ler_texto("CPF: ")
    email = ler_texto("E-mail: ")
    telefone = ler_texto("Telefone (opcional): ", obrigatorio=False)

    cliente = service.cadastrar_pf(nome, email, cpf, telefone or None)
    print(f"\n>> Cliente cadastrado com sucesso!\n   {cliente}")
    pausar()


def _cadastrar_pj(service: ClienteService):
    print("\n-- Pessoa Jurídica --")
    razao_social = ler_texto("Razão social: ")
    cnpj = ler_texto("CNPJ: ")
    nome_fantasia = ler_texto("Nome fantasia (opcional): ", obrigatorio=False)
    email = ler_texto("E-mail: ")
    telefone = ler_texto("Telefone (opcional): ", obrigatorio=False)

    cliente = service.cadastrar_pj(
        razao_social, email, cnpj, nome_fantasia or None, telefone or None
    )
    print(f"\n>> Cliente cadastrado com sucesso!\n   {cliente}")
    pausar()


# ------------------------------------------------------------------ listar / buscar
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


# ------------------------------------------------------------------ atualizar
def _atualizar(service: ClienteService):
    exibir_titulo("ATUALIZAR CLIENTE")
    cliente_id = ler_inteiro("ID do cliente: ")
    atual = service.buscar_por_id(cliente_id)
    print(f"\nDados atuais:\n  {atual}\n")

    if isinstance(atual, PessoaFisica):
        _atualizar_pf(service, cliente_id, atual)
    else:
        _atualizar_pj(service, cliente_id, atual)


def _atualizar_pf(service: ClienteService, cliente_id: int, atual: PessoaFisica):
    print("-- Editando Pessoa Física --")
    nome = ler_texto(f"Nome [{atual.nome}]: ", obrigatorio=False) or atual.nome
    cpf = ler_texto(f"CPF [{atual.cpf}]: ", obrigatorio=False) or atual.cpf
    email = ler_texto(f"E-mail [{atual.email}]: ", obrigatorio=False) or atual.email
    telefone = (
        ler_texto(f"Telefone [{atual.telefone or '-'}]: ", obrigatorio=False)
        or atual.telefone
    )

    cliente = service.atualizar_pf(cliente_id, nome, email, cpf, telefone)
    print(f"\n>> Cliente atualizado com sucesso!\n   {cliente}")
    pausar()


def _atualizar_pj(service: ClienteService, cliente_id: int, atual: PessoaJuridica):
    print("-- Editando Pessoa Jurídica --")
    razao = (
        ler_texto(f"Razão social [{atual.razao_social}]: ", obrigatorio=False)
        or atual.razao_social
    )
    cnpj = ler_texto(f"CNPJ [{atual.cnpj}]: ", obrigatorio=False) or atual.cnpj
    fantasia = (
        ler_texto(f"Nome fantasia [{atual.nome_fantasia or '-'}]: ", obrigatorio=False)
        or atual.nome_fantasia
    )
    email = ler_texto(f"E-mail [{atual.email}]: ", obrigatorio=False) or atual.email
    telefone = (
        ler_texto(f"Telefone [{atual.telefone or '-'}]: ", obrigatorio=False)
        or atual.telefone
    )

    cliente = service.atualizar_pj(cliente_id, razao, email, cnpj, fantasia, telefone)
    print(f"\n>> Cliente atualizado com sucesso!\n   {cliente}")
    pausar()


# ------------------------------------------------------------------ excluir
def _excluir(service: ClienteService):
    exibir_titulo("EXCLUIR CLIENTE")
    cliente_id = ler_inteiro("ID do cliente: ")
    cliente = service.buscar_por_id(cliente_id)

    # usa polimorfismo: __str__ chama exibir_dados() da subclasse correta
    confirmacao = ler_texto(
        f"Confirma a exclusão de '{cliente.nome}'? (s/n): "
    ).lower()
    if confirmacao == "s":
        service.excluir(cliente_id)
        print(">> Cliente excluído com sucesso!")
    else:
        print(">> Operação cancelada.")
    pausar()
