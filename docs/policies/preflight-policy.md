# Preflight Policy

## Preflight antes de qualquer tarefa

Antes de qualquer agente ou desenvolvedor alterar arquivos, execute:

```bash
git status
git branch --show-current
git fetch origin
git checkout develop
git pull origin develop
git branch --show-current
git log --oneline -5
```

Se houver alterações locais não commitadas antes de começar, pare e informe o
estado do repositório. Não sobrescreva trabalho local sem autorização explícita.

## Regras

- Se a tarefa for feature, criar branch `feature/*` a partir de `develop`.
- Se a tarefa for bugfix comum, criar branch `bugfix/*` a partir de `develop`.
- Se a tarefa for documentação, criar branch `docs/*` a partir de `develop`.
- Nunca criar feature a partir de `main`.
- Nunca abrir PR de feature para `main`.
- Nunca trabalhar direto em `develop`.
- Nunca trabalhar direto em `main`.
- Sempre confirmar base da PR antes de abrir.
- Toda branch comum deve nascer da `develop` atualizada, não de uma branch antiga.

## Checklist obrigatório antes de abrir PR

```bash
git status
git branch --show-current
git diff --check
git log --oneline --decorate -5
```

Confirme:

- A branch atual não é `main`.
- A branch atual não é `develop`.
- A branch nasceu da `develop` atualizada.
- A PR será aberta para a base correta.

## Verificação da base da PR

Se usar GitHub CLI:

```bash
gh pr create --base develop --head nome-da-branch
```

Se usar interface web, confirmar visualmente:

```text
base: develop
compare: branch de trabalho
```

Se a base aparecer como `main`, pare. Não abra a PR.
