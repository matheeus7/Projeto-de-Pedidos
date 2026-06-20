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
├── main.py                      # Ponto de entrada da aplicação
│
├── models/                      # Entidades de domínio (POO pura, sem SQL)
│   ├── pessoa.py                 # Classe abstrata Pessoa (ABC)
│   ├── cliente.py                # Cliente(Pessoa)
│   ├── funcionario.py            # Funcionario(Pessoa)
│   ├── produto.py
│   ├── pedido.py
│   └── item_pedido.py
│
├── repositories/                # Acesso a dados (SQL puro via psycopg2)
│   ├── cliente_repository.py
│   ├── produto_repository.py
│   └── pedido_repository.py
│
├── services/                    # Regras de negócio
│   ├── cliente_service.py
│   ├── produto_service.py
│   └── pedido_service.py
│
├── ui/                           # Interface em terminal (menus)
│   ├── menu_principal.py
│   ├── menu_cliente.py
│   ├── menu_produto.py
│   ├── menu_pedido.py
│   ├── menu_relatorios.py
│   └── helpers.py                # Funções auxiliares de entrada/saída
│
├── database/
│   └── connection.py             # Configuração e criação de conexões PostgreSQL
│
├── exceptions/
│   └── exceptions.py             # Exceções customizadas (uma por regra de negócio)
│
├── scripts/
│   └── create_tables.sql         # Script de criação do banco de dados
│
├── requirements.txt
└── README.md
```

---

## 2. Arquitetura

O projeto segue uma **arquitetura em camadas (layered architecture)**, em que cada
camada tem uma única responsabilidade e só conhece a camada imediatamente abaixo
dela. O fluxo de uma requisição sempre segue a mesma direção:

```
 UI (menus de terminal)
        │  chama métodos de
        ▼
 Services (regras de negócio)
        │  chama métodos de
        ▼
 Repositories (SQL / acesso a dados)
        │  usa
        ▼
 Database (conexão com PostgreSQL)

 Models são usados em todas as camadas acima (são os objetos que
 trafegam entre elas).
```

| Camada | Responsabilidade | NÃO deve fazer |
|---|---|---|
| **models/** | Representar as entidades do domínio, validar seus próprios atributos (encapsulamento) | Não contém SQL nem `input()`/`print()` |
| **repositories/** | Executar comandos SQL (INSERT/SELECT/UPDATE/DELETE) e converter linhas do banco em objetos de `models/` | Não contém regra de negócio (ex: não decide se um e-mail é duplicado) |
| **services/** | Concentrar **todas** as regras de negócio, orquestrar chamadas a um ou mais repositories, lançar exceções de domínio | Não acessa o banco diretamente, não interage com o terminal |
| **ui/** | Interação com o usuário (menus, `input()`, `print()`), captura e exibição amigável de exceções | Não contém SQL nem regra de negócio |
| **database/** | Configuração de conexão com o PostgreSQL | Não conhece SQL de entidades específicas |
| **exceptions/** | Vocabulário de erros do domínio, compartilhado entre `services` e `ui` | — |

**Por que essa separação importa:** se amanhã o projeto trocar a interface de
terminal por uma API REST ou uma interface gráfica, basta criar uma nova camada de
UI — `services` e `repositories` não mudam. Se o banco de dados mudar de
PostgreSQL para outro SGBD, só a camada `repositories`/`database` é afetada.

### Injeção de dependência simples

Cada `Service` recebe seu(s) `Repository` no construtor, com um valor padrão:

```python
class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository = None):
        self._repo = cliente_repository or ClienteRepository()
```

Isso permite testar a lógica de negócio com repositórios falsos (em memória), sem
precisar de um banco PostgreSQL real — técnica usada durante o desenvolvimento
deste projeto para validar todas as regras de negócio antes da integração final
com o banco.

---

## 3. Modelo de dados e relacionamentos

```
clientes (1) ────────< (N) pedidos (1) ────────< (N) itens_pedido (N) >──────── (1) produtos
```

- Um **cliente** pode possuir vários **pedidos** (`pedidos.cliente_id` → `clientes.id`).
- Um **pedido** pertence a um único **cliente**.
- Um **pedido** possui vários **itens** (`itens_pedido.pedido_id` → `pedidos.id`).
- Cada **item** referencia um **produto** (`itens_pedido.produto_id` → `produtos.id`).

### Tabelas

**clientes**: `id`, `nome`, `email` (único), `telefone`
**produtos**: `id`, `nome`, `descricao`, `preco`, `estoque`
**pedidos**: `id`, `cliente_id`, `data_pedido`, `valor_total`, `status`
**itens_pedido**: `id`, `pedido_id`, `produto_id`, `quantidade`, `valor_unitario`

O script completo, com chaves estrangeiras, `CHECK` constraints e índices, está em
[`scripts/create_tables.sql`](scripts/create_tables.sql).

---

## 4. Conceitos de POO aplicados

### 4.1 Classe abstrata (`models/pessoa.py`)

`Pessoa` é uma classe abstrata construída com `ABC` e `@abstractmethod`:

```python
from abc import ABC, abstractmethod

class Pessoa(ABC):
    @abstractmethod
    def exibir_dados(self) -> str:
        raise NotImplementedError
```

Ela **não pode ser instanciada diretamente** — tentar `Pessoa("nome", "email")`
lança `TypeError`. Sua função é definir um **contrato**: toda subclasse de
`Pessoa` é obrigada a implementar `exibir_dados()`. Isso garante consistência na
hierarquia e é a base para o polimorfismo descrito abaixo.

### 4.2 Herança

```
Pessoa (abstrata)
 ├── Cliente
 └── Funcionario
```

`Cliente` e `Funcionario` herdam de `Pessoa` e reutilizam, via `super().__init__()`,
a validação e o encapsulamento de `nome` e `email` já implementados na classe-mãe,
adicionando apenas seus atributos específicos (`telefone` em `Cliente`; `cargo` e
`salario` em `Funcionario`).

> **Nota:** o enunciado do banco de dados não define uma tabela `funcionarios`,
> portanto `Funcionario` não possui `repository`/persistência própria — ela existe
> na hierarquia de `models/` especificamente para demonstrar, de forma concreta e
> executável, a herança e o polimorfismo lado a lado com `Cliente`.

### 4.3 Polimorfismo

Mesmo método (`exibir_dados()`), comportamentos diferentes conforme a subclasse:

```python
pessoas = [
    Cliente("Ana Souza", "ana@email.com", "92999999999", id=1),
    Funcionario("Bruno Lima", "bruno@loja.com", "Vendedor", 2500.0, id=1),
]
for pessoa in pessoas:
    print(pessoa.exibir_dados())
```

Saída:
```
Cliente #1 | Nome: Ana Souza | E-mail: ana@email.com | Telefone: 92999999999
Funcionário #1 | Nome: Bruno Lima | Cargo: Vendedor | Salário: R$ 2500.00
```

O código que percorre a lista **não precisa saber** se está lidando com um
`Cliente` ou um `Funcionario` — cada objeto sabe exibir seus próprios dados.

### 4.4 Encapsulamento

Todos os atributos sensíveis são privados (prefixo `__`, *name mangling* do
Python) e expostos por meio de `@property`, que validam os valores antes de
aceitá-los. Exemplos:

```python
@property
def preco(self) -> float:
    return self.__preco

@preco.setter
def preco(self, valor: float):
    if valor is None or valor < 0:
        raise ValueError("O preço do produto não pode ser negativo.")
    self.__preco = float(valor)
```

Isso impede, por exemplo, `produto.preco = -50` em qualquer ponto do código —
mesmo fora da camada de `services` — pois a validação está no próprio objeto.
A regra de negócio "preço não pode ser negativo" é garantida tanto na entidade
(`models/produto.py`) quanto reforçada explicitamente no `ProdutoService`.

### 4.5 `__str__` nas entidades principais

`Cliente`, `Funcionario`, `Produto`, `ItemPedido` e `Pedido` implementam `__str__`,
de modo que `print(objeto)` sempre produz uma representação legível para o
usuário do terminal — usado extensivamente pelos menus em `ui/`.

### 4.6 Tratamento de exceções

O pacote `exceptions/exceptions.py` define uma hierarquia própria de exceções de
domínio, todas derivadas de `RegraDeNegocioError`:

```
RegraDeNegocioError
 ├── EntidadeNaoEncontradaError
 ├── EmailDuplicadoError
 ├── PrecoInvalidoError
 ├── EstoqueInvalidoError
 ├── EstoqueInsuficienteError
 ├── QuantidadeInvalidaError
 ├── PedidoSemItensError
 ├── ProdutoComPedidosError
 └── PedidoJaCanceladoError
```

Os `services` lançam essas exceções; a camada `ui` as captura (`ui/helpers.py →
tratar_erro()`) e exibe mensagens amigáveis, sem nunca expor um *stack trace* ao
usuário final. Erros de conexão com o banco (`ConnectionError`) também são
tratados de forma específica.

---

## 5. Regras de negócio

Todas implementadas na camada `services/`:

1. **E-mail de cliente não pode ser duplicado** — `ClienteService` consulta
   `buscar_por_email` antes de inserir/atualizar.
2. **Produto não pode ter preço negativo** — validado em `Produto` (setter) e em
   `ProdutoService`.
3. **Estoque não pode ser negativo** — validado em `Produto` (setter), em
   `ProdutoService`, e via `CHECK (estoque >= 0)` no banco.
4. **Pedido não pode ser criado sem itens** — `PedidoService.criar_pedido` lança
   `PedidoSemItensError` se a lista de itens estiver vazia.
5. **Não é possível comprar mais que o estoque disponível** — verificado antes de
   persistir e novamente no `UPDATE ... WHERE estoque >= quantidade` (proteção
   contra concorrência).
6. **Ao finalizar um pedido, o estoque é reduzido automaticamente** — feito em uma
   única transação atômica em `PedidoRepository.salvar_pedido_completo`.
7. **O valor total do pedido é calculado automaticamente** — propriedade
   `Pedido.valor_total`, soma dos subtotais de cada `ItemPedido`.
8. **Quantidade de item não pode ser ≤ 0** — validado em `ItemPedido` (setter) e em
   `PedidoService`.
9. **Produto associado a pedidos não pode ser excluído** —
   `ProdutoRepository.possui_pedidos()` consulta `itens_pedido`; se existir
   referência, `ProdutoService.excluir` lança `ProdutoComPedidosError`.

---

## 6. Decisões de projeto

- **Coluna `status` em `pedidos`**: o enunciado original lista apenas `id`,
  `cliente_id`, `data_pedido` e `valor_total` para a tabela `pedidos`, mas também
  exige a funcionalidade "cancelar pedido". Para viabilizar essa funcionalidade
  sem apagar o histórico (o que violaria o requisito de "consultar histórico de
  pedidos"), foi adicionada a coluna `status` (`CONFIRMADO` / `CANCELADO`). Um
  pedido cancelado continua no histórico, mas é excluído do relatório de "total
  vendido" e tem seu estoque restaurado automaticamente.
- **Transações atômicas**: criação e cancelamento de pedidos envolvem múltiplas
  tabelas (`pedidos`, `itens_pedido`, `produtos`). Ambas operações usam uma única
  conexão/transação no `PedidoRepository`, garantindo que, em caso de falha (ex:
  estoque insuficiente detectado no banco), nenhuma alteração parcial seja salva.
- **`Funcionario` sem tabela própria**: mantido apenas em `models/` para cumprir o
  requisito de herança/polimorfismo explicitado no enunciado, já que o modelo de
  dados fornecido não inclui uma tabela `funcionarios`.

---

## 7. Instalação

### 7.1 Pré-requisitos

- Python 3.9 ou superior
- PostgreSQL 13 ou superior instalado e em execução

### 7.2 Instalar dependências

```bash
cd projeto
pip install -r requirements.txt
```

### 7.3 Criar o banco de dados

Acesse o `psql` (ou outra ferramenta de administração) e crie o banco:

```sql
CREATE DATABASE loja_db;
```

### 7.4 Criar as tabelas

Com o banco `loja_db` criado, execute o script de criação das tabelas:

```bash
psql -U postgres -d loja_db -f scripts/create_tables.sql
```

O script também insere alguns clientes e produtos de exemplo, úteis para testar o
sistema imediatamente após a instalação.

### 7.5 Configurar a conexão

Edite `database/connection.py` caso seus dados de acesso ao PostgreSQL sejam
diferentes dos padrões (`localhost:5432`, usuário `postgres`, senha `postgres`,
banco `loja_db`):

```python
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "loja_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}
```

Alternativamente, defina as variáveis de ambiente `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER` e `DB_PASSWORD` antes de executar o sistema — elas têm prioridade sobre
os valores padrão e evitam editar o código-fonte.

---

## 8. Execução

A partir da pasta `projeto/`:

```bash
python main.py
```

O menu principal será exibido:

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

Navegue pelos submenus digitando o número da opção desejada e pressione ENTER.

---

## 9. Roteiro de uso / apresentação

Sugestão de sequência para demonstrar o sistema completo:

1. **Clientes → Listar clientes**: mostra os clientes de exemplo já cadastrados
   pelo script SQL.
2. **Produtos → Listar produtos**: mostra os produtos de exemplo (note que
   "Headset Gamer" tem estoque 0).
3. **Pedidos → Criar novo pedido**: crie um pedido para o cliente #1 com 2
   unidades do produto #1 — observe o cálculo automático do valor total.
4. **Produtos → Buscar produto por ID** (produto #1): confirme que o estoque foi
   reduzido automaticamente.
5. **Pedidos → Criar novo pedido** com o produto #4 (estoque 0): o sistema
   bloqueia a operação com `EstoqueInsuficienteError`.
6. **Produtos → Excluir produto** (produto #1, que já tem pedido): o sistema
   bloqueia com `ProdutoComPedidosError`.
7. **Pedidos → Cancelar pedido** (o pedido criado no passo 3): confirme que o
   estoque do produto #1 volta ao valor original.
8. **Relatórios → Total vendido**: confirme que o valor não inclui o pedido
   cancelado.
9. **Relatórios → Produtos com estoque baixo**: liste produtos com estoque ≤ 5.

Esse roteiro cobre o CRUD completo das três entidades principais e todas as nove
regras de negócio do sistema.
