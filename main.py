"""
Sistema de Loja e Pedidos
=========================
Ponto de entrada da aplicação.

Execução:
    python main.py

Pré-requisitos: PostgreSQL em execução, banco de dados criado e
script scripts/create_tables.sql executado. Veja README.md.
"""

from ui.menu_principal import iniciar_menu_principal


def main():
    iniciar_menu_principal()


if __name__ == "__main__":
    main()
