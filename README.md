# Area Verde API

API inicial para apoiar a operação do bar Area Verde. O projeto foi
estruturado a partir dos diagramas em `docs/` e espelha o padrão técnico do
repositório `shortsmaker-api`: FastAPI, Clean Architecture, SQLModel, Alembic,
Dependency Injector, Docker e DevContainer.

## Estrutura do Projeto

O projeto segue os princípios de **Clean Architecture**:

- `app/core`: entidades de domínio, enums, interfaces e futuros casos de uso.
- `app/adapter`: controladores HTTP, repositórios e integrações de entrada.
- `app/infra`: configuração técnica, banco de dados, injeção de dependências e logs.
- `docs`: documentação inicial, diagramas Mermaid e arquivos Postman.

## Domínio Inicial

O primeiro incremento cobre o MVP operacional do bar:

- produtos e categorias;
- controle de estoque;
- comandas e itens;
- pagamentos e fiado;
- caixa diário;
- movimentos de caixa e estoque.

Os fluxos completos de venda ainda não foram implementados como endpoints. A API
começa com o bootstrap técnico, o modelo inicial do domínio e o endpoint de
saúde.

## Desenvolvimento

Para iniciar o desenvolvimento, abra este projeto no **VS Code DevContainer** ou
use o ambiente local Python.

Antes de subir o Docker Compose local, crie seu arquivo de ambiente:

```bash
cp app/.env.example app/.env
# edite app/.env e preencha POSTGRES_PASSWORD
```

### Comandos Úteis

Execute os comandos dentro da pasta `app/`.

```bash
# instalar dependências
make install

# rodar projeto localmente
make run

# rodar testes
make test

# rodar build
make build

# rodar lint e type check
make lint

# formatar código
make format
```

### Docker

Execute os comandos dentro da pasta `app/`.

- `make docker-build`: constrói a imagem da API.
- `make up`: sobe API e Postgres em modo daemon.
- `make down`: para e remove os containers.
- `make ps`: lista os containers.
- `make logs`: mostra logs em tempo real.
- `make migrate`: executa as migrações dentro do container da API.

Com Docker, a API fica disponível em `http://localhost:58001` e o Postgres em
`localhost:55433`.

## Fluxo de desenvolvimento

Branch principal de desenvolvimento:

- `develop`

Branch estável:

- `main`

Fluxo padrão:

1. Criar branch a partir de `develop`.
2. Desenvolver a funcionalidade.
3. Abrir Pull Request para `develop`.
4. Aguardar CI passar.
5. Fazer merge.
6. Criar `release/*` quando for preparar versão.
7. Fazer merge da release em `main`.
8. Gerar tag de versão.

Exemplo:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/comandas
```

Commits devem seguir Conventional Commits:

```bash
feat: adiciona criação de comanda
fix: corrige cálculo do total da comanda
docs: adiciona documentação do fluxo git
ci: adiciona workflow do GitHub Actions
```

## Documentação

- [Documentação inicial](docs/README.md)
- [Diagrama de classes](docs/class_diagram.md)
- [Diagrama de casos de uso](docs/use_case_diagram.md)
- [Git Flow](docs/git-flow.md)
- [Workflow de desenvolvimento](docs/development-workflow.md)
- [CI/CD](docs/ci-cd.md)
- [Guia de contribuição](CONTRIBUTING.md)

## Referência

Este projeto foi configurado tomando como espelho o repositório
`byt3un1on/shortsmaker-api`.
