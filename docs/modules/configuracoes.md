# Módulo - Configurações

## Status

Implementado.

## Objetivo

Permitir configurar parâmetros operacionais simples do sistema.

## Casos de uso atendidos

- Configurar nome do bar.
- Configurar dias para vencimento/alerta de fiado.
- Configurar permissão de estoque negativo.
- Consultar configuração atual.
- Criar configuração padrão quando ainda não existir registro.
- Atualizar configuração completa.
- Atualizar configuração parcial.

## Entidades envolvidas

- `ConfiguracaoSistema`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/configuracoes` | Consulta configuração atual |
| `PUT` | `/api/configuracoes` | Atualiza configuração completa |
| `PATCH` | `/api/configuracoes` | Atualiza configuração parcial |

## Regras de negócio

- O sistema mantém um único registro operacional de configuração.
- Se não existir registro, `GET /api/configuracoes` cria a configuração padrão.
- A configuração padrão nasce com:
  - `nome_bar = "Area Verde"`
  - `dias_para_alerta_fiado = 7`
  - `permitir_estoque_negativo = true`
  - senha ainda não configurada
- `permitir_estoque_negativo=false` bloqueia baixa por venda que deixaria saldo
  negativo em produto simples ou componente de produto composto.
- Ajuste manual continua rejeitando `novoEstoque < 0`.
- O módulo de Fiado / Pendências usa `dias_para_alerta_fiado` como prazo padrão
  quando o request não informa `vencimentoEm`.

## Validações

- `nomeBar` é obrigatório e aceita até 120 caracteres.
- `diasParaAlertaFiado` deve ser maior que zero.
- `observacao` aceita até 500 caracteres.
- O response nunca expõe `senha_acesso_hash`.

## Exemplos de request

**PUT /api/configuracoes**
```json
{
  "nomeBar": "Area Verde Matriz",
  "diasParaAlertaFiado": 10,
  "permitirEstoqueNegativo": false,
  "observacao": "Configuração principal"
}
```

**PATCH /api/configuracoes**
```json
{
  "permitirEstoqueNegativo": true
}
```

## Exemplos de response

```json
{
  "id": 1,
  "nomeBar": "Area Verde Matriz",
  "diasParaAlertaFiado": 10,
  "permitirEstoqueNegativo": false,
  "observacao": "Configuração principal",
  "senhaConfigurada": true,
  "criadoEm": "2026-06-01T00:10:00",
  "atualizadoEm": "2026-06-01T00:20:00"
}
```

## Testes relacionados

- `app/configuracoes_test.py`

## O que ainda não está incluso

- Múltiplos perfis de configuração.
- Histórico/versionamento de parâmetros.
- Gestão avançada de preferências por usuário.

## Próximo passo relacionado

- Release MVP.
