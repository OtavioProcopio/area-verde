# Módulo 3 - Estoque

## Objetivo

O módulo de Estoque permite consultar a posição atual dos produtos que controlam
estoque, identificar estoque baixo ou negativo, registrar entrada manual,
realizar ajuste manual e rastrear o histórico de movimentações por produto.

Este módulo depende do módulo de Produtos e Categorias. Ele não implementa baixa
automática por venda, devolução por cancelamento, Comandas, Caixa, Pagamentos,
Fiado, Relatórios, Frontend ou Deploy.

## Casos de uso atendidos

- Consultar estoque atual.
- Adicionar entrada de estoque.
- Ajustar estoque manualmente.
- Ver produtos com estoque baixo.
- Consultar movimentos de estoque.
- Visualizar alerta de estoque negativo.

## Endpoints

### GET /api/estoque

Lista produtos que controlam estoque.

Filtros opcionais:

- `categoriaId`
- `nome`
- `ativo`

Exemplo:

```http
GET /api/estoque?categoriaId=1&nome=cerveja&ativo=true
```

Response:

```json
[
  {
    "produtoId": 1,
    "nome": "Cerveja lata",
    "categoria": {
      "id": 1,
      "nome": "Cervejas"
    },
    "unidadeEstoque": "UNIDADE",
    "quantidadeEstoque": 24,
    "estoqueMinimo": 6,
    "estoqueBaixo": false,
    "estoqueNegativo": false,
    "ativo": true
  }
]
```

### GET /api/estoque/baixo

Lista produtos ativos, com controle de estoque, cuja quantidade atual é menor ou
igual ao estoque mínimo.

```json
[
  {
    "produtoId": 2,
    "nome": "Dose de pinga",
    "categoria": {
      "id": 2,
      "nome": "Doses"
    },
    "unidadeEstoque": "ML",
    "quantidadeEstoque": 150,
    "estoqueMinimo": 200,
    "estoqueBaixo": true,
    "estoqueNegativo": false,
    "ativo": true
  }
]
```

### GET /api/estoque/negativo

Lista produtos ativos, com controle de estoque, cuja quantidade atual está
negativa.

```json
[
  {
    "produtoId": 3,
    "nome": "Salgado",
    "categoria": {
      "id": 4,
      "nome": "Salgados"
    },
    "unidadeEstoque": "UNIDADE",
    "quantidadeEstoque": -2,
    "estoqueMinimo": 5,
    "estoqueBaixo": true,
    "estoqueNegativo": true,
    "ativo": true
  }
]
```

### GET /api/estoque/produtos/{produto_id}/movimentos

Lista movimentos de estoque de um produto. Se o produto existir e não possuir
movimentos, retorna lista vazia. A ordenação é decrescente por `criadoEm` e, em
caso de empate, por `id`.

```json
[
  {
    "id": 1,
    "produtoId": 1,
    "produtoNome": "Cerveja lata",
    "tipo": "ENTRADA",
    "origem": "ENTRADA_MANUAL",
    "quantidade": 24,
    "estoqueAntes": 0,
    "estoqueDepois": 24,
    "observacao": "Compra inicial",
    "criadoEm": "2026-05-26T10:30:00"
  }
]
```

### POST /api/estoque/produtos/{produto_id}/entrada

Registra entrada manual de estoque. A entrada soma ao estoque atual e cria um
movimento do tipo `ENTRADA` com origem `ENTRADA_MANUAL`.

Request:

```json
{
  "quantidade": 24,
  "observacao": "Compra do dia"
}
```

Response:

```json
{
  "id": 1,
  "produtoId": 1,
  "produtoNome": "Cerveja lata",
  "tipo": "ENTRADA",
  "origem": "ENTRADA_MANUAL",
  "quantidade": 24,
  "estoqueAntes": 10,
  "estoqueDepois": 34,
  "observacao": "Compra do dia",
  "criadoEm": "2026-05-26T10:30:00"
}
```

### POST /api/estoque/produtos/{produto_id}/ajuste

Registra ajuste manual de estoque. O ajuste define a nova quantidade real; a
quantidade do movimento é a diferença entre o novo estoque e o estoque anterior.

Request:

```json
{
  "novoEstoque": 7,
  "observacao": "Ajuste após contagem física"
}
```

Response:

```json
{
  "id": 2,
  "produtoId": 1,
  "produtoNome": "Cerveja lata",
  "tipo": "AJUSTE",
  "origem": "AJUSTE_MANUAL",
  "quantidade": -3,
  "estoqueAntes": 10,
  "estoqueDepois": 7,
  "observacao": "Ajuste após contagem física",
  "criadoEm": "2026-05-26T10:30:00"
}
```

## Regras de validação

- O produto deve existir. Erro: `produto_nao_encontrado`.
- Produto inativo não recebe entrada nem ajuste. Erro: `produto_inativo`.
- Produto sem controle de estoque não recebe entrada nem ajuste. Erro:
  `produto_sem_controle_estoque`.
- Entrada manual exige `quantidade > 0`. Erro: `quantidade_invalida`.
- Ajuste manual permite `novoEstoque = 0` e rejeita valor negativo. Erro:
  `novo_estoque_invalido`.

## Regras de estoque

- Entrada manual soma ao estoque atual.
- Ajuste manual define o novo estoque e registra a diferença no movimento.
- Estoque baixo ocorre quando `quantidadeEstoque <= estoqueMinimo` para produto
  ativo e com controle de estoque.
- Estoque negativo ocorre quando `quantidadeEstoque < 0` para produto ativo e com
  controle de estoque.
- Movimentos de estoque não possuem endpoint de exclusão.
- Entrada e ajuste atualizam `Produto.quantidade_estoque` e criam
  `MovimentoEstoque` em uma única transação.

## Histórico e evolução

O histórico é mantido na tabela `movimento_estoque` com tipo, origem,
quantidade, estoque anterior, estoque posterior, observação e data de criação.

A baixa automática por venda (`SAIDA_VENDA` e origem `COMANDA`) e a devolução por
cancelamento (`DEVOLUCAO_CANCELAMENTO` e origem `CANCELAMENTO`) serão
implementadas no futuro módulo de Comandas.
