# Migration Policy

## Regras gerais

- Toda alteração de schema deve ter migration Alembic.
- Não alterar banco manualmente sem migration.
- Migration deve ter `upgrade` e `downgrade` coerentes.
- Migration deve alterar apenas o escopo necessário.
- Não remover índice, coluna ou tabela de outro módulo sem justificativa explícita.
- Não misturar alteração de schema de módulos diferentes sem necessidade clara.

## Migration já mergeada

Antes de release/prod:

- Pode ser corrigida se ainda não foi aplicada em ambiente compartilhado.
- A correção deve ser explicada na PR.

Depois de release/prod:

- Não editar migration antiga.
- Criar nova migration corretiva.

## Checklist

- [ ] A migration altera apenas o necessário.
- [ ] Não remove índices de outros módulos.
- [ ] Não recria tabela já existente sem necessidade.
- [ ] `alembic upgrade head` funciona.
- [ ] `alembic downgrade -1` foi considerado ou testado quando aplicável.

## Referências

- [Banco de dados e migrations](../architecture/database.md)
- [Agent Policy](agent-policy.md)
