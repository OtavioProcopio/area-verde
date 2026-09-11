# Módulo - Acesso / Senha

## Status

Implementado.

## Objetivo

Oferecer um fluxo simples de acesso administrativo para o MVP, baseado em uma
única senha operacional armazenada como hash na `ConfiguracaoSistema`.

## Casos de uso atendidos

- Validar senha de acesso.
- Definir senha inicial.
- Alterar senha existente.
- Bloquear validação quando a senha ainda não foi configurada.
- Nunca expor hash em responses.

## Entidades envolvidas

- `ConfiguracaoSistema`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/acesso/validar` | Valida a senha operacional |
| `PUT` | `/api/acesso/senha` | Define ou altera a senha operacional |

## Regras de negócio

- O módulo usa uma única senha operacional para o MVP.
- A senha é persistida apenas como hash.
- Se ainda não existir configuração, o fluxo cria a configuração padrão antes de
  salvar a senha.
- Validar acesso sem senha configurada retorna erro funcional.
- Alterar senha existente exige `senhaAtual`.
- A senha nova deve possuir ao menos 4 caracteres.

## Validações

- `senha_nao_configurada`
- `senha_invalida`
- `senha_atual_obrigatoria`
- `senha_atual_invalida`
- `nova_senha_invalida`

## Exemplos de request

**POST /api/acesso/validar**
```json
{
  "senha": "1234"
}
```

**PUT /api/acesso/senha**
```json
{
  "novaSenha": "1234"
}
```

**PUT /api/acesso/senha** com troca:
```json
{
  "senhaAtual": "1234",
  "novaSenha": "5678"
}
```

## Exemplos de response

**POST /api/acesso/validar**
```json
{
  "valido": true
}
```

**PUT /api/acesso/senha**
```json
{
  "senhaConfigurada": true
}
```

## Testes relacionados

- `app/configuracoes_test.py`

## O que ainda não está incluso

- Múltiplos usuários.
- Perfis e permissões.
- Sessão/token.
- Recuperação de senha.

## Próximo passo relacionado

- Frontend operacional.
