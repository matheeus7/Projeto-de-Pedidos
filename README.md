# Sistema de Loja e Pedidos

Sistema de terminal em **Python 3 + PostgreSQL** para gerenciar clientes, produtos,
pedidos e estoque, desenvolvido em **arquitetura em camadas** com **Programação
Orientada a Objetos**, sem frameworks externos (apenas `psycopg2` para acesso ao
banco de dados).

---

## Sumário

1. [Estrutura do projeto](#1-estrutura-do-projeto)
2. [Arquitetura](#2-arquitetura)
3. [Modelo de dados e relacionamentos](#3-modelo-de-dados-e-relacionamentos)
4. [Conceitos de POO aplicados](#4-conceitos-de-poo-aplicados)
5. [Regras de negócio](#5-regras-de-negócio)
6. [Decisões de projeto](#6-decisões-de-projeto)
7. [Instalação](#7-instalação)
8. [Execução](#8-execução)
9. [Roteiro de uso / apresentação](#9-roteiro-de-uso--apresentação)

---

## 1. Estrutura do projeto

```
projeto/
│
├── main.py
│
├── models/
│   ├── pessoa.py            # Classe abstrata Pessoa (ABC + @abstractmethod)
│   ├── pessoa_fisica.py     # PessoaFisica(Pessoa) — cliente com CPF
│   ├── pessoa_juridica.py   # PessoaJuridica(Pessoa) — cliente com CNPJ
│   ├── produto.py
│   ├── pedido.py
│   └── item_pedido.py
│
├── repositories/
│   ├── cliente_repository.py   # INSERT/SELECT/UPDATE/DELETE em `clientes`
│   ├── produto_repository.py
│   └── pedido_repository.py
│
├── services/
│   ├── cliente_service.py      # Regras de negócio (cadastrar_pf/pj, atualizar_pf/pj)
│   ├── produto_service.py
│   └── pedido_service.py
│
├── ui/
│   ├── menu_principal.py
│   ├── menu_cliente.py         # Fluxos distintos para PF e PJ
│   ├── menu_produto.py
│   ├── menu_pedido.py
│   ├── menu_relatorios.py
│   └── helpers.py
│
├── database/
│   └── connection.py
│
├── exceptions/
│   └── exceptions.py
│
├── scripts/
│   ├── create_tables.sql       # Banco do zero (inclui colunas PF/PJ)
│  
│
├── requirements.txt
└── README.md
```

---

## 2. Arquitetura

O projeto segue **arquitetura em camadas (layered architecture)**:

```
 UI (menus de terminal)
        │
        ▼
 Services (regras de negócio)
        │
        ▼
 Repositories (SQL via psycopg2)
        │
        ▼
 Database (conexão PostgreSQL)

 Models trafegam entre todas as camadas.
```

| Camada | Responsabilidade | NÃO faz |
|---|---|---|
| **models/** | Entidades, encapsulamento, validação de atributos | SQL, `print()` |
| **repositories/** | SQL puro, converte linhas em objetos (O/R mapping) | Regra de negócio |
| **services/** | Todas as regras de negócio, orquestra repositories | SQL direto, `input()` |
| **ui/** | Menus, `input()`, exibição de erros | SQL, regra de negócio |
| **database/** | Configuração de conexão | SQL de entidades |
| **exceptions/** | Vocabulário de erros do domínio | — |

### Injeção de dependência simples

Cada Service recebe seus Repositories no construtor com valores padrão,
o que permite substituir por implementações falsas (em memória) para testar
a lógica de negócio sem banco real:

```python
class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository = None):
        self._repo = cliente_repository or ClienteRepository()
```

---

## 3. Modelo de dados e relacionamentos

```
clientes (1) ────────< (N) pedidos (1) ────────< (N) itens_pedido (N) >──────── (1) produtos
```

### Tabela `clientes` — padrão Single Table Inheritance

Armazena Pessoa Física e Pessoa Jurídica na mesma tabela, com a coluna
discriminadora `tipo_pessoa`:

| Coluna | PF | PJ |
|---|---|---|
| `id`, `nome`, `email`, `telefone` | ✓ | ✓ |
| `tipo_pessoa` | `'PF'` | `'PJ'` |
| `cpf` | ✓ obrigatório | — |
| `cnpj` | — | ✓ obrigatório |
| `nome_fantasia` | — | opcional |

Para PJ, a coluna `nome` armazena a **razão social**; `PessoaJuridica.razao_social`
é uma propriedade que delega para `self.nome` (herdado de `Pessoa`).

---

## 4. Conceitos de POO aplicados

### 4.1 Classe abstrata (`models/pessoa.py`)

`Pessoa` usa `ABC` e `@abstractmethod` — não pode ser instanciada diretamente:

```python
from abc import ABC, abstractmethod

class Pessoa(ABC):
    def __init__(self, nome: str, email: str = None):
        self._validar_nome(nome)
        self.__nome = nome.strip()
        self.__email = email.strip().lower() if email else None

    @abstractmethod
    def exibir_dados(self) -> str:
        """Cada subclasse define como exibe seus dados."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.exibir_dados()
```

Tentar `Pessoa("Ana", "ana@email.com")` lança `TypeError` em tempo de execução.

### 4.2 Herança e uso de `super()`

```
Pessoa (abstrata)
├── PessoaFisica   — acrescenta cpf, telefone
└── PessoaJuridica — acrescenta cnpj, nome_fantasia, telefone
```

Ambas as subclasses chamam `super().__init__()` para reutilizar a validação
de `nome` e `email` já implementada em `Pessoa`:

```python
class PessoaFisica(Pessoa):
    def __init__(self, nome, email, cpf, telefone=None, id=None):
        super().__init__(nome, email)   # <-- herança via super()
        self.__cpf = cpf
        self.__telefone = telefone

class PessoaJuridica(Pessoa):
    def __init__(self, razao_social, email, cnpj, nome_fantasia=None, telefone=None, id=None):
        super().__init__(razao_social, email)   # razao_social é o `nome` de Pessoa
        self.__cnpj = cnpj
        self.__nome_fantasia = nome_fantasia
```

### 4.3 Polimorfismo — sobrescrita de `exibir_dados()`

Mesmo método, comportamentos completamente distintos:

```python
clientes = [
    PessoaFisica("Ana Souza", "ana@email.com", "123.456.789-00", id=1),
    PessoaJuridica("Tech Dist Ltda", "td@techdist.com", "12.345.678/0001-99",
                   nome_fantasia="TechDist", id=2),
]
for cliente in clientes:
    print(cliente.exibir_dados())   # mesmo método, resultado diferente
```

Saída:
```
[PF] Cliente #1 | Nome: Ana Souza | CPF: 123.456.789-00 | E-mail: ana@email.com | Telefone: não informado
[PJ] Cliente #2 | Razão Social: Tech Dist Ltda | Nome Fantasia: TechDist | CNPJ: 12.345.678/0001-99 | E-mail: td@techdist.com | Telefone: não informado
```

O polimorfismo aparece também no mapeamento O/R dentro do `ClienteRepository`:

```python
def _mapear(linha) -> Cliente:
    id_, nome, email, telefone, tipo_pessoa, cpf, cnpj, nome_fantasia = linha
    if tipo_pessoa == "PF":
        return PessoaFisica(nome=nome, email=email, cpf=cpf, telefone=telefone, id=id_)
    return PessoaJuridica(razao_social=nome, email=email, cnpj=cnpj,
                          nome_fantasia=nome_fantasia, telefone=telefone, id=id_)
```

E no menu de clientes, com `isinstance()`:

```python
cliente = service.buscar_por_id(id)
if isinstance(cliente, PessoaFisica):
    _atualizar_pf(service, id, cliente)   # coleta CPF
else:
    _atualizar_pj(service, id, cliente)   # coleta CNPJ + nome_fantasia
```

### 4.4 Encapsulamento

Todos os atributos são privados (`__prefixo`) e expostos com `@property` + setter
que validam antes de aceitar o valor:

```python
# Em PessoaJuridica
@property
def cnpj(self) -> str:
    return self.__cnpj

@cnpj.setter
def cnpj(self, valor: str):
    if not valor or not str(valor).strip():
        raise ValueError("O CNPJ não pode ser vazio.")
    self.__cnpj = valor.strip()

# Propriedade que delega para Pessoa.nome (encapsulamento + herança)
@property
def razao_social(self) -> str:
    return self.nome

@razao_social.setter
def razao_social(self, valor: str):
    self.nome = valor   # aciona a validação de Pessoa._validar_nome()
```

### 4.5 `__str__` nas entidades

Todas as entidades implementam `__str__`, que delega para `exibir_dados()`,
permitindo `print(cliente)` em qualquer ponto do código sem `if/else` de tipo.

### 4.6 Tratamento de exceções

Hierarquia de exceções do domínio em `exceptions/exceptions.py`:

```
RegraDeNegocioError
 ├── EntidadeNaoEncontradaError
 ├── EmailDuplicadoError
 ├── DocumentoDuplicadoError     ← CPF ou CNPJ já cadastrado
 ├── TipoPessoaInvalidoError
 ├── PrecoInvalidoError
 ├── EstoqueInvalidoError
 ├── EstoqueInsuficienteError
 ├── QuantidadeInvalidaError
 ├── PedidoSemItensError
 ├── ProdutoComPedidosError
 └── PedidoJaCanceladoError
```

---

## 5. Regras de negócio

| # | Regra | Onde está |
|---|---|---|
| 1 | E-mail único entre todos os clientes | `ClienteService._verificar_email_unico()` |
| 2 | CPF único entre todas as Pessoas Físicas | `ClienteService._verificar_cpf_unico()` |
| 3 | CNPJ único entre todas as Pessoas Jurídicas | `ClienteService._verificar_cnpj_unico()` |
| 4 | O tipo de pessoa (PF/PJ) não pode mudar após o cadastro | `ClienteService._buscar_como()` |
| 5 | Produto não pode ter preço negativo | `ProdutoService._validar_preco()` |
| 6 | Estoque não pode ser negativo | `ProdutoService._validar_estoque()` |
| 7 | Pedido não pode ser criado sem itens | `PedidoService.criar_pedido()` |
| 8 | Quantidade do item deve ser > 0 | `PedidoService` + setter de `ItemPedido` |
| 9 | Não é possível comprar acima do estoque disponível | `PedidoService` + UPDATE atômico |
| 10 | Ao finalizar pedido, estoque é reduzido automaticamente | `PedidoRepository` (transação) |
| 11 | Valor total do pedido calculado automaticamente | `Pedido.valor_total` (property) |
| 12 | Produto com pedidos associados não pode ser excluído | `ProdutoService.excluir()` |

---

## 6. Decisões de projeto

### Hierarquia de clientes: PF e PJ na mesma tabela (Single Table Inheritance)

Optou-se por armazenar `PessoaFisica` e `PessoaJuridica` na tabela `clientes`
com uma coluna discriminadora `tipo_pessoa`, em vez de duas tabelas separadas.
Isso simplifica os JOINs nos pedidos e mantém a FK `pedidos.cliente_id → clientes.id`
sem ambiguidade. As colunas exclusivas de cada tipo são `nullable` e protegidas
por `CHECK` constraints no banco.

### `razao_social` como `nome` de `Pessoa`

Para PJ, a coluna `nome` do banco armazena a razão social. A propriedade
`PessoaJuridica.razao_social` delega para `self.nome` (herdado de `Pessoa`),
evitando duplicação de dado no banco e mantendo o comportamento consistente com
a classe abstrata — que já valida e encapsula `nome`.

### Coluna `status` em `pedidos`

Adicionada além do esquema original para viabilizar o cancelamento de pedidos
sem apagar o histórico. Um pedido cancelado restaura o estoque automaticamente
(via transação atômica no repository) e é excluído do relatório de total vendido.

### `Funcionario` removido do domínio

A classe `Funcionario` existia apenas para demonstrar herança. Com a refatoração,
o polimorfismo e a herança são demonstrados por `PessoaFisica` e `PessoaJuridica`,
que pertencem ao domínio real do sistema.

---

## 7. Instalação

### 7.1 Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL 13 ou superior

### 7.2 Instalar dependências

```bash
cd projeto
pip install -r requirements.txt
```

### 7.3 Banco de dados novo

```bash
# 1. Criar o banco
psql -U postgres -c "CREATE DATABASE loja_db;"

# 2. Criar as tabelas e inserir dados de exemplo
psql -U postgres -d loja_db -f scripts/create_tables.sql
```

### 7.4 Configurar a conexão

Edite `database/connection.py` ou defina as variáveis de ambiente:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=loja_db
export DB_USER=postgres
export DB_PASSWORD=postgres
```

---

## 8. Execução

```bash
python main.py
```

```
=======================================================
           SISTEMA DE LOJA E PEDIDOS
=======================================================
1 - Clientes
2 - Produtos
3 - Pedidos
4 - Relatórios
0 - Sair
```

---

## 9. Roteiro de uso / apresentação

Sequência para demonstrar todos os conceitos do projeto:

1. **Clientes → Listar clientes** — mostra um PF e um PJ já cadastrados pelo
   script de exemplo (`exibir_dados()` com saída diferente para cada tipo).
2. **Clientes → Cadastrar (PF)** — cadastre uma nova Pessoa Física e veja a
   validação de e-mail duplicado se repetir o e-mail.
3. **Clientes → Cadastrar (PJ)** — cadastre uma Pessoa Jurídica. Note que o
   menu coleta campos diferentes de forma automática (`isinstance()` no menu).
4. **Clientes → Atualizar** — atualize qualquer cliente; o sistema detecta o
   tipo via `isinstance()` e exibe apenas os campos relevantes.
5. **Produtos → Listar** — veja o estoque atual (Headset Gamer = 0).
6. **Pedidos → Criar novo pedido** — tente incluir o Headset Gamer (estoque 0):
   o sistema bloqueia com `EstoqueInsuficienteError`.
7. **Pedidos → Criar novo pedido** — crie com itens válidos e observe o cálculo
   automático do total e a baixa automática de estoque.
8. **Produtos → Excluir** o produto do pedido — bloqueado por `ProdutoComPedidosError`.
9. **Pedidos → Cancelar** — cancele o pedido; o estoque é restaurado automaticamente.
10. **Relatórios → Total vendido** — confirma que o pedido cancelado não entra no total.
