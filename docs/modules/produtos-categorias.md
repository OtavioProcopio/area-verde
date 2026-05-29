# Módulo - Produtos e Categorias

## Status

Implementado.

Modelagem de produtos compostos implementada parcialmente no Modulo 9.1.
Endpoints de composicao e integracao com comandas/estoque ainda estao pendentes.

## Objetivo

Manter o cadastro base de categorias e produtos vendidos pelo bar. Este módulo
é a base para estoque, comandas e relatórios.

## Casos de uso atendidos

- Criar categoria.
- Listar categorias.
- Consultar categoria por ID.
- Editar categoria.
- Ativar e inativar categoria.
- Criar produto.
- Listar produtos com filtros.
- Consultar produto por ID.
- Editar produto.
- Ativar e inativar produto.
- Configurar controle de estoque por produto.
- Classificar produto como `SIMPLES` ou `COMPOSTO`.
- Modelar composicao de produto composto por componentes de estoque.

## Entidades envolvidas

- `CategoriaProduto`
- `Produto`
- `TipoProduto`
- `ProdutoComposicao`
- `UnidadeEstoque`
- `ItemComanda`
- `MovimentoEstoque`

`ItemComanda` e `MovimentoEstoque` usam produto como referencia operacional em
vendas e movimentacoes, mas nao sao geridos diretamente por este modulo.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/categorias` | Cria categoria |
| `GET` | `/api/categorias` | Lista categorias |
| `GET` | `/api/categorias/{id}` | Consulta categoria |
| `PUT` | `/api/categorias/{id}` | Edita categoria |
| `PATCH` | `/api/categorias/{id}/ativar` | Ativa categoria |
| `PATCH` | `/api/categorias/{id}/inativar` | Inativa categoria |
| `POST` | `/api/produtos` | Cria produto |
| `GET` | `/api/produtos` | Lista produtos |
| `GET` | `/api/produtos/{id}` | Consulta produto |
| `PUT` | `/api/produtos/{id}` | Edita produto |
| `PATCH` | `/api/produtos/{id}/ativar` | Ativa produto |
| `PATCH` | `/api/produtos/{id}/inativar` | Inativa produto |

Nao existem endpoints de composicao nesta etapa. A tabela e as regras de
modelagem foram preparadas para o proximo incremento do Modulo 9.

## Regras de negócio

- Categorias e produtos iniciam ativos.
- Categorias e produtos não são excluídos fisicamente.
- Não pode existir mais de uma categoria ativa com o mesmo nome.
- Categoria inativa não pode ser usada para criar ou editar produto.
- Produto pode controlar estoque ou não.
- Produto inicia com `tipoProduto=SIMPLES` quando o tipo nao e informado.
- Produto `COMPOSTO` e vendavel, mas sua baixa por componentes sera integrada
  no modulo de comandas em etapa posterior.
- Produto sem controle de estoque persiste valores de estoque zerados.
- `unidadeEstoque`, `quantidadeBaixaPorVenda` e `estoqueMinimo` definem como o
  produto participa dos fluxos de estoque e comanda.
- Produto composto nao pode ser componente de si mesmo.
- Produto composto nao pode usar outro produto composto como componente no MVP.
- Componentes de produto composto devem estar ativos, controlar estoque e ter
  quantidade de baixa maior que zero.

## Validações

- `nome` de categoria é obrigatório e possui limite de 120 caracteres.
- `nome`, `categoriaId`, `precoVenda` e `controlaEstoque` são obrigatórios para
  produto.
- `tipoProduto`, quando informado, deve ser `SIMPLES` ou `COMPOSTO`.
- `precoVenda` não pode ser negativo.
- Se `controlaEstoque=true`, `unidadeEstoque` é obrigatória.
- Se `controlaEstoque=true`, `quantidadeBaixaPorVenda` deve ser maior que zero.
- Estoque atual e estoque mínimo não podem ser negativos.

## Exemplos de request

Categoria:

```json
{
  "nome": "Cervejas"
}
```

Produto por unidade:

```json
{
  "nome": "Cerveja lata",
  "categoriaId": 1,
  "precoVenda": 7.0,
  "tipoProduto": "SIMPLES",
  "controlaEstoque": true,
  "unidadeEstoque": "UNIDADE",
  "quantidadeEstoque": 24,
  "quantidadeBaixaPorVenda": 1,
  "estoqueMinimo": 6
}
```

Produto composto:

```json
{
  "nome": "Dose Mista A+B",
  "categoriaId": 2,
  "precoVenda": 12.0,
  "tipoProduto": "COMPOSTO",
  "controlaEstoque": false
}
```

Produto sem controle de estoque:

```json
{
  "nome": "Taxa de serviço",
  "categoriaId": 5,
  "precoVenda": 2.0,
  "controlaEstoque": false
}
```

## Exemplos de response

```json
{
  "id": 1,
  "nome": "Cerveja lata",
  "categoria": {
    "id": 1,
    "nome": "Cervejas"
  },
  "precoVenda": 7.0,
  "tipoProduto": "SIMPLES",
  "controlaEstoque": true,
  "unidadeEstoque": "UNIDADE",
  "quantidadeEstoque": 24.0,
  "quantidadeBaixaPorVenda": 1.0,
  "estoqueMinimo": 6.0,
  "ativo": true,
  "criadoEm": "2026-05-26T10:30:00",
  "atualizadoEm": "2026-05-26T10:30:00"
}
```

## Testes relacionados

- `app/produtos_categorias_test.py`

## O que ainda não está incluso

- Cadastro de fornecedores.
- Endpoints para gerenciar composicao de produtos.
- Baixa de estoque por componentes ao vender produto composto.
- Importação de produtos.
- Exclusão física de produtos.
- Relatórios por produto.

## Próximo passo relacionado

- Implementar os endpoints de composicao do Modulo 9.2.
