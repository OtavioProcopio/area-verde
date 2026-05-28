# Módulo - Estoque

## Status

Implementado.

## Objetivo

Consultar a posição atual de estoque, registrar entradas e ajustes manuais,
identificar estoque baixo ou negativo e manter histórico de movimentações por
produto.

## Casos de uso atendidos

- Consultar estoque atual.
- Filtrar estoque por categoria, nome e status.
- Listar produtos com estoque baixo.
- Listar produtos com estoque negativo.
- Registrar entrada manual.
- Registrar ajuste manual.
- Consultar histórico de movimentos por produto.
- Registrar baixa automática por venda via comanda.
- Registrar devolução automática por cancelamento, redução ou remoção de item.

## Entidades envolvidas

- `Produto`
- `CategoriaProduto`
- `MovimentoEstoque`
- `TipoMovimentoEstoque`
- `OrigemMovimentoEstoque`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/estoque` | Lista produtos que controlam estoque |
| `GET` | `/api/estoque/baixo` | Lista produtos com estoque baixo |
| `GET` | `/api/estoque/negativo` | Lista produtos com estoque negativo |
| `GET` | `/api/estoque/produtos/{produto_id}/movimentos` | Lista movimentos do produto |
| `POST` | `/api/estoque/produtos/{produto_id}/entrada` | Registra entrada manual |
| `POST` | `/api/estoque/produtos/{produto_id}/ajuste` | Registra ajuste manual |

## Regras de negócio

- Apenas produtos com `controlaEstoque=true` aparecem na consulta de estoque.
- Entrada manual soma ao estoque atual.
- Ajuste manual define a nova quantidade de estoque.
- Movimento de ajuste registra a diferença entre estoque novo e anterior.
- Estoque baixo ocorre quando `quantidadeEstoque <= estoqueMinimo`.
- Estoque negativo ocorre quando `quantidadeEstoque < 0`.
- Movimentos de estoque não possuem endpoint de exclusão.
- Movimentos manuais usam origem `ENTRADA_MANUAL` ou `AJUSTE_MANUAL`.
- Movimentos automáticos por comanda usam origem `COMANDA` ou `CANCELAMENTO`.

## Validações

- Produto deve existir. Erro: `produto_nao_encontrado`.
- Produto inativo não recebe entrada nem ajuste. Erro: `produto_inativo`.
- Produto sem controle de estoque não recebe entrada nem ajuste. Erro:
  `produto_sem_controle_estoque`.
- Entrada exige `quantidade > 0`. Erro: `quantidade_invalida`.
- Ajuste rejeita `novoEstoque < 0`. Erro: `novo_estoque_invalido`.

## Exemplos de request

Entrada:

```json
{
  "quantidade": 24,
  "observacao": "Compra do dia"
}
```

Ajuste:

```json
{
  "novoEstoque": 7,
  "observacao": "Ajuste após contagem física"
}
```

## Exemplos de response

```json
{
  "id": 1,
  "produtoId": 1,
  "produtoNome": "Cerveja lata",
  "tipo": "ENTRADA",
  "origem": "ENTRADA_MANUAL",
  "quantidade": 24.0,
  "estoqueAntes": 10.0,
  "estoqueDepois": 34.0,
  "observacao": "Compra do dia",
  "criadoEm": "2026-05-26T10:30:00"
}
```

## Testes relacionados

- `app/estoque_test.py`

## O que ainda não está incluso

- Inventário completo.
- Transferência entre depósitos.
- Bloqueio global de venda por estoque negativo.

## Próximo passo relacionado

- Usar movimentos de estoque em relatórios e conferências operacionais.
