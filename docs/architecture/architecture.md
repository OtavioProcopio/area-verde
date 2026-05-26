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
