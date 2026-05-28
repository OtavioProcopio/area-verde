# Módulo - Clientes

## Status

Implementado.

## Objetivo

Registrar clientes simples para permitir histórico confiável de fiado sem
obrigar cadastro completo para toda comanda. A abertura rápida por nome/apelido
continua disponível para atendimento comum.

## Casos de uso atendidos

- Criar cliente.
- Listar clientes com filtros por ativo, nome/apelido e telefone.
- Consultar cliente por ID.
- Editar dados cadastrais.
- Ativar e inativar cliente.
- Consultar pendências do cliente.
- Usar cliente como vínculo opcional em comanda.
- Bloquear duplicidade de cliente ativo por nome ou telefone normalizados.

## Entidades envolvidas

- `Cliente`
- `Comanda`
- `StatusComanda`

## Entidade Cliente

Campos:

- `id`
- `nome`
- `apelido`
- `telefone`
- `observacao`
- `ativo`
- `criado_em`
- `atualizado_em`

O cliente inicia ativo. Não há exclusão física no MVP.

Clientes ativos devem ser únicos por:

- nome normalizado com `trim` e comparação case-insensitive;
- telefone normalizado, quando informado, removendo espaços e caracteres comuns
  como `(`, `)`, `-` e `.`.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/clientes` | Cria cliente |
| `GET` | `/api/clientes` | Lista clientes |
| `GET` | `/api/clientes/{cliente_id}` | Consulta cliente |
| `PUT` | `/api/clientes/{cliente_id}` | Edita cliente |
| `PATCH` | `/api/clientes/{cliente_id}/ativar` | Ativa cliente |
| `PATCH` | `/api/clientes/{cliente_id}/inativar` | Inativa cliente |
| `GET` | `/api/clientes/{cliente_id}/pendencias` | Lista resumo de pendências |

## Requests

**POST /api/clientes**
```json
{
  "nome": "João da Oficina",
  "apelido": "João",
  "telefone": "16999999999",
  "observacao": "Cliente costuma pagar no fim da semana"
}
```

## Responses

**POST /api/clientes**
```json
{
  "id": 1,
  "nome": "João da Oficina",
  "apelido": "João",
  "telefone": "16999999999",
  "observacao": "Cliente costuma pagar no fim da semana",
  "ativo": true,
  "criadoEm": "2026-05-27T10:00:00",
  "atualizadoEm": "2026-05-27T10:00:00"
}
```

**GET /api/clientes/{cliente_id}/pendencias**
```json
{
  "cliente": {
    "id": 1,
    "nome": "João da Oficina",
    "apelido": "João",
    "telefone": "16999999999",
    "ativo": true
  },
  "totalPendente": "80.00",
  "totalVencido": "0.00",
  "pendencias": []
}
```

## Validações

- `nome` é obrigatório, não pode ser vazio e aceita até 160 caracteres.
- `apelido` é opcional e aceita até 160 caracteres.
- `telefone` é opcional e aceita até 40 caracteres.
- `observacao` é opcional e aceita até 500 caracteres.
- Cliente inexistente retorna `cliente_nao_encontrado`.
- Cliente inativo não pode ser usado para nova comanda com vínculo nem para fiado.
- Cliente ativo duplicado retorna `cliente_duplicado`.

## Regras de ativação

Cliente inativo permanece no histórico, mas não pode ser usado para novo fiado.
Reativar cliente libera novamente o uso em comandas futuras.

Inativar cliente não oculta nem remove pendências. Elas continuam aparecendo em:

- `GET /api/clientes/{cliente_id}/pendencias`
- `GET /api/fiados`
- `GET /api/fiados/vencidos`
- `GET /api/fiados/{comanda_id}`

## Testes relacionados

- `app/clientes_test.py`
- `app/fiado_test.py`

## Fora de escopo

- CPF obrigatório.
- Limite de crédito.
- Juros.
- Parcelamento.
- Exclusão física.

## Próximo passo relacionado

- Usar clientes e pendências em relatórios básicos.
