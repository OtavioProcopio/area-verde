# Módulo - Produtos e Categorias

## Status

Implementado.

Produtos compostos possuem modelagem, endpoints de composicao, integracao com
comandas/estoque e leitura correta em relatorios.

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
- Consultar, adicionar, editar e remover componentes de produto composto.

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
| `GET` | `/api/produtos/{id}/composicao` | Consulta composicao |
| `POST` | `/api/produtos/{id}/composicao/componentes` | Adiciona componente |
| `PUT` | `/api/produtos/{id}/composicao/componentes/{componente_id}` | Edita quantidade do componente |
| `DELETE` | `/api/produtos/{id}/composicao/componentes/{componente_id}` | Remove componente |

## Regras de negócio

- Categorias e produtos iniciam ativos.
- Categorias e produtos não são excluídos fisicamente.
- Não pode existir mais de uma categoria ativa com o mesmo nome.
- Categoria inativa não pode ser usada para criar ou editar produto.
- Produto pode controlar estoque ou não.
- Produto inicia com `tipoProduto=SIMPLES` quando o tipo nao e informado.
- Produto `COMPOSTO` e vendavel e baixa estoque pelos componentes.
- Produto `COMPOSTO` cobra o preco proprio e aparece como produto vendido nos
  relatorios de venda.
- Produto sem controle de estoque persiste valores de estoque zerados.
- `unidadeEstoque`, `quantidadeBaixaPorVenda` e `estoqueMinimo` definem como o
  produto participa dos fluxos de estoque e comanda.
- Produto composto nao pode ser componente de si mesmo.
- Produto composto nao pode usar outro produto composto como componente no MVP.
- Componentes de produto composto devem estar ativos, controlar estoque e ter
  quantidade de baixa maior que zero.
- Produto composto sem composicao nao pode ser vendido em comanda.

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

Adicionar componente:

```json
{
  "produtoComponenteId": 10,
  "quantidadeBaixa": 50
}
```

Fluxo recomendado para produto composto:

1. Criar produtos simples componentes com `controlaEstoque=true`.
2. Criar produto composto com `tipoProduto=COMPOSTO`.
3. Adicionar componentes em `/api/produtos/{id}/composicao/componentes`.
4. Vender o produto composto em `/api/comandas/{id}/itens`.
5. Consultar movimentos dos componentes em `/api/estoque/produtos/{id}/movimentos`.
6. Consultar venda em `/api/relatorios/produtos-mais-vendidos` e consumo fisico
   em `/api/relatorios/estoque-consumido`.

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
- `app/produto_composicao_test.py`

## O que ainda não está incluso

- Cadastro de fornecedores.
- Importação de produtos.
- Exclusão física de produtos.
- Produto composto dentro de produto composto.
- Montagem livre de drink na hora.

## Próximo passo relacionado

- Configurações.
