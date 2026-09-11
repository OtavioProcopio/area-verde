# Arquitetura do Projeto

## Visão geral

O Area Verde API segue Clean Architecture em camadas, com FastAPI na entrada
HTTP, regras de negócio nos services/use cases, domínio isolado em `core` e
persistência via repositories.

## Componentes principais

- FastAPI: camada HTTP e roteamento.
- SQLModel: entidades de domínio e mapeamento ORM.
- Alembic: versionamento do schema de banco.
- PostgreSQL: banco principal.
- Dependency Injector: configuração de dependências de infraestrutura.
- Pytest: suíte de testes automatizados.

## Modulos funcionais atuais

| Modulo | Entrada HTTP | Use case | Repositories principais |
|---|---|---|---|
| Produtos e Categorias | `categoria_produto_controller.py`, `produto_controller.py` | `categoria_produto_service.py`, `produto_service.py` | `categoria_produto_repository.py`, `produto_repository.py` |
| Estoque | `estoque_controller.py` | `estoque_service.py` | `produto_repository.py`, `movimento_estoque_repository.py` |
| Clientes | `cliente_controller.py` | `cliente_service.py` | `cliente_repository.py`, `comanda_repository.py` |
| Comandas e Itens | `comanda_controller.py` | `comanda_service.py` | `comanda_repository.py`, `produto_repository.py`, `caixa_repository.py` |
| Pagamentos e Fechamento | `pagamento_controller.py` | `pagamento_service.py` | `comanda_repository.py`, `pagamento_repository.py`, `caixa_repository.py` |
| Caixa Diario | `caixa_controller.py` | `caixa_service.py` | `caixa_repository.py`, `comanda_repository.py` |
| Fiado / Pendencias | `fiado_controller.py` | `fiado_service.py` | `comanda_repository.py`, `cliente_repository.py`, `pagamento_repository.py`, `caixa_repository.py` |

Relatorios, Configuracoes, Acesso/Senha e Frontend ainda nao possuem modulos
operacionais completos.

## Estrutura

```text
app/
  adapter/
    controllers/
    dtos/
    repositories/
  core/
    application/
      use_cases/
    domain/
      enums/
      exceptions/
      models.py
    interfaces/
      adapters/
        repositories/
  infra/
    config/
  migrations/
    versions/
```

## Fluxo de chamada

```text
HTTP -> Controller -> DTO -> Service/Use Case -> Repository -> Banco
```

O retorno segue o caminho inverso, formatado por DTOs de resposta.

## Migrations

Alterações de schema devem ser feitas por migrations Alembic versionadas em
`app/migrations/versions/`.
