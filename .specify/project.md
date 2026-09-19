# Area Verde API

> Identidade e princípios **deste** projeto. Este arquivo **é versionado** — é o que o time
> compartilha. Os princípios da organização ficam em `.specify/memory/constitution.md`, que o
> `/bu:constitution` gera a cada clone e o `.gitignore` mantém fora do git.

## Identidade

- **Projeto**: Area Verde API
- **Tipo**: api
- **Stack**: Python, FastAPI, SQLModel, PostgreSQL, Alembic, Docker
- **Domínio**: API para o MVP de controle operacional de um bar — produtos, estoque, comandas, pagamentos, fiado, caixa e relatórios
- **Cobertura mínima acordada**: 90%

## Princípios específicos deste projeto

> Entram aqui, e só aqui, as regras que valem para **este** repositório e que não estão nos
> princípios da organização: restrição regulatória, SLA, compatibilidade obrigatória, limite de
> dependência, janela de manutenção. Cada princípio declara o que **proíbe** — princípio que não
> proíbe nada não é portão.

### Princípio 1 — Migrations Alembic

Toda alteração de schema do banco (tabela, coluna, índice, constraint) exige migration Alembic
com `upgrade` e `downgrade` coerentes, e altera apenas o escopo necessário — proíbe editar o
banco manualmente e proíbe remover índice/coluna/tabela de outro módulo sem justificativa
explícita na PR. Migration já aplicada em ambiente compartilhado (release/prod) não é editada:
correção vira migration nova. Referência: `docs/policies/migration-policy.md`.

## Emendas

| Versão | Data | O que mudou |
|---|---|---|
| 1.0.0 | 2026-09-18 | ratificação inicial |
