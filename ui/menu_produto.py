"""Submenu de gerenciamento de Produtos."""

from services.produto_service import ProdutoService
from ui.helpers import ler_texto, ler_inteiro, ler_float, pausar, exibir_titulo, tratar_erro


def menu_produtos(service: ProdutoService):
    while True:
        exibir_titulo("MENU PRODUTOS")
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Buscar produto por ID")
        print("4 - Atualizar produto")
        print("5 - Excluir produto")
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


def _cadastrar(service: ProdutoService):
    exibir_titulo("CADASTRAR PRODUTO")
    nome = ler_texto("Nome: ")
    descricao = ler_texto("Descrição (opcional): ", obrigatorio=False)
    preco = ler_float("Preço (ex: 19.90): ")
    estoque = ler_inteiro("Estoque inicial: ")

    produto = service.cadastrar(nome, descricao or None, preco, estoque)
    print(f"\n>> Produto cadastrado com sucesso! {produto}")
    pausar()


def _listar(service: ProdutoService):
    exibir_titulo("LISTA DE PRODUTOS")
    produtos = service.listar()
    if not produtos:
        print("Nenhum produto cadastrado.")
    for produto in produtos:
        print(produto)
    pausar()


def _buscar(service: ProdutoService):
    exibir_titulo("BUSCAR PRODUTO POR ID")
    produto_id = ler_inteiro("ID do produto: ")
    produto = service.buscar_por_id(produto_id)
    print(f"\n{produto}")
    if produto.descricao:
        print(f"Descrição: {produto.descricao}")
    pausar()


def _atualizar(service: ProdutoService):
    exibir_titulo("ATUALIZAR PRODUTO")
    produto_id = ler_inteiro("ID do produto: ")
    atual = service.buscar_por_id(produto_id)
    print(f"Dados atuais: {atual}")

    nome = ler_texto(f"Novo nome [{atual.nome}]: ", obrigatorio=False) or atual.nome
    descricao = ler_texto(
        f"Nova descrição [{atual.descricao or '-'}]: ", obrigatorio=False
    ) or atual.descricao

    preco_str = ler_texto(f"Novo preço [{atual.preco:.2f}]: ", obrigatorio=False)
    preco = float(preco_str.replace(",", ".")) if preco_str else atual.preco

    estoque_str = ler_texto(f"Novo estoque [{atual.estoque}]: ", obrigatorio=False)
    estoque = int(estoque_str) if estoque_str else atual.estoque

    produto = service.atualizar(produto_id, nome, descricao, preco, estoque)
    print(f"\n>> Produto atualizado com sucesso! {produto}")
    pausar()


def _excluir(service: ProdutoService):
    exibir_titulo("EXCLUIR PRODUTO")
    produto_id = ler_inteiro("ID do produto: ")
    produto = service.buscar_por_id(produto_id)
    confirmacao = ler_texto(f"Confirma a exclusão de '{produto.nome}'? (s/n): ").lower()
    if confirmacao == "s":
        service.excluir(produto_id)
        print(">> Produto excluído com sucesso!")
    else:
        print(">> Operação cancelada.")
    pausar()
