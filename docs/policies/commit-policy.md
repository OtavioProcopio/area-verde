# Commit Policy

## Padrão

Use Conventional Commits.

## Tipos

- `feat`: nova funcionalidade.
- `fix`: correção.
- `docs`: documentação.
- `test`: testes.
- `refactor`: refatoração sem mudança de comportamento.
- `ci`: pipeline e automações de CI.
- `chore`: manutenção.

## Exemplos

```text
feat: implementa modulo de estoque
fix: corrige calculo do total da comanda
docs: organiza documentacao dos modulos
test: adiciona testes de cancelamento de comanda
ci: adiciona workflow de validacao
chore: atualiza dependencias
```

## Regras

- Uma mensagem deve descrever a alteração principal.
- Evite commits gigantes com temas diferentes.
- Não misture documentação, feature e refatoração sem necessidade.
