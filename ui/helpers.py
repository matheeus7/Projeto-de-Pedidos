"""Funções auxiliares de entrada/saída compartilhadas pelos menus."""

from exceptions.exceptions import RegraDeNegocioError


def ler_texto(mensagem: str, obrigatorio: bool = True) -> str:
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print(">> Este campo é obrigatório. Tente novamente.")


def ler_inteiro(mensagem: str) -> int:
    while True:
        valor = input(mensagem).strip()
        try:
            return int(valor)
        except ValueError:
            print(">> Digite um número inteiro válido.")


def ler_float(mensagem: str) -> float:
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print(">> Digite um número válido (ex: 19.90).")


def ler_opcao(mensagem: str) -> str:
    return input(mensagem).strip()


def pausar():
    input("\nPressione ENTER para continuar...")


def exibir_titulo(titulo: str):
    print("\n" + "=" * 55)
    print(titulo.center(55))
    print("=" * 55)


def tratar_erro(erro: Exception):
    """Padroniza a exibição de erros para o usuário do terminal."""
    if isinstance(erro, RegraDeNegocioError):
        print(f"\n[Regra de negócio] {erro}")
    elif isinstance(erro, (ValueError, TypeError)):
        print(f"\n[Dados inválidos] {erro}")
    elif isinstance(erro, ConnectionError):
        print(f"\n[Erro de conexão] {erro}")
    else:
        print(f"\n[Erro inesperado] {erro}")
