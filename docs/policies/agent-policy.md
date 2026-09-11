# Agent Policy

## Regras para agentes de código

- Sempre ler `README.md`.
- Sempre ler `docs/README.md`.
- Sempre ler a policy correspondente antes de alterar código.
- Sempre executar o preflight obrigatório antes de alterar arquivos.
- Nunca trabalhar direto em `main`.
- Nunca trabalhar direto em `develop`.
- Criar branch específica.
- Não implementar módulo fora do escopo.
- Não reestruturar projeto sem autorização.
- Não commitar secrets.
- Rodar testes antes de finalizar quando houver alteração de código.
- Atualizar documentação quando alterar comportamento do sistema.
- Informar arquivos criados e alterados.
- Informar comandos executados.
- Informar resultado dos testes.
- Informar comandos que falharam e como foram contornados.

## Preflight obrigatório para agentes

Antes de alterar qualquer arquivo, o agente deve executar:

```bash
git status
git branch --show-current
git fetch origin
git checkout develop
git pull origin develop
git checkout -b <tipo>/<nome-da-tarefa>
```

O agente deve informar na resposta final:

- branch inicial detectada;
- branch base usada;
- branch criada;
- se `origin/develop` foi atualizado;
- se havia alterações locais antes de começar.

## Regras explícitas

- O agente não pode assumir que já está em `develop`.
- O agente não pode assumir que `develop` está atualizado.
- O agente não pode abrir PR para `main` em feature comum.
- O agente não pode prosseguir se houver conflito local não resolvido.
- O agente não pode dizer que usou DevContainer se não usou.
- O agente deve separar validações feitas no DevContainer das validações feitas no host.
- O agente deve declarar comandos que falharam e como contornou.
- O agente deve consultar a [Migration Policy](migration-policy.md) antes de alterar migrations.
- O agente deve consultar a [Documentation Policy](documentation-policy.md) quando alterar comportamento ou documentação de módulo.

## Resposta final obrigatória do agente

```markdown
## Branch inicial detectada

## Branch base atualizada

## Branch criada

## Arquivos criados

## Arquivos alterados

## Funcionalidades ou documentos alterados

## Validações no DevContainer

## Validações no host

## Comandos que falharam

## Ajustes pendentes

## Pull Request

## Observações
```

## Referências

- [Preflight Policy](preflight-policy.md)
- [Pull Request Policy](pull-request-policy.md)
- [DevContainer Policy](devcontainer-policy.md)
- [Migration Policy](migration-policy.md)
- [Documentation Policy](documentation-policy.md)
