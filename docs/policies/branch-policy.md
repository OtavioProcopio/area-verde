# Branch Policy

## Padrão de nomes

Use nomes curtos, descritivos e em kebab-case.

## Exemplos

- `feature/produtos-categorias`
- `feature/estoque`
- `feature/comandas`
- `feature/pagamentos-fechamento`
- `feature/caixa-diario`
- `feature/fiado-pendencias`
- `feature/relatorios-basicos`
- `docs/endurece-politicas-agentes`
- `chore/atualiza-dependencias`
- `bugfix/corrige-fechamento-comanda`
- `release/v0.1.0`
- `hotfix/corrige-migration-producao`

## Regras

- Use `feature/*` para módulos e novas capacidades.
- Use `bugfix/*` para correções comuns.
- Use `docs/*` para mudanças exclusivas de documentação.
- Use `chore/*` para manutenção (dependências, configs, automações) sem mudança de comportamento.
- Use `release/*` apenas para preparação de versão.
- Use `hotfix/*` apenas para correção urgente a partir de `main`.
- O nome da branch deve indicar o escopo real.
- Não usar branch genérica quando o módulo for específico.
- Não reutilizar branch antiga para novo módulo.
