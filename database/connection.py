"""
Módulo responsável por centralizar a configuração e a criação de
conexões com o banco de dados PostgreSQL.

Edite o dicionário DB_CONFIG abaixo com os dados do seu ambiente,
ou então defina as variáveis de ambiente correspondentes
(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD), que têm
prioridade sobre os valores padrão.
"""

import os
import psycopg2


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "loja_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def obter_conexao():
    """
    Cria e retorna uma nova conexão com o banco de dados PostgreSQL.

    Cada repositório é responsável por fechar a conexão que abrir,
    salvo quando uma conexão já existente é recebida como parâmetro
    (uso em operações transacionais que envolvem múltiplas tabelas,
    como a criação de um pedido completo).
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as erro:
        raise ConnectionError(
            "Não foi possível conectar ao banco de dados PostgreSQL. "
            "Verifique se o servidor está em execução e se os dados de "
            f"conexão em database/connection.py estão corretos. Detalhe: {erro}"
        ) from erro
