# Módulo - Produtos e Categorias

## Status

Implementado.

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

## Entidades envolvidas

- `CategoriaProduto`
- `Produto`
- `UnidadeEstoque`

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

## Regras de negócio

- Categorias e produtos iniciam ativos.
- Categorias e produtos não são excluídos fisicamente.
- Não pode existir mais de uma categoria ativa com o mesmo nome.
- Categoria inativa não pode ser usada para criar ou editar produto.
- Produto pode controlar estoque ou não.
- Produto sem controle de estoque persiste valores de estoque zerados.

## Validações

- `nome` de categoria é obrigatório e possui limite de 120 caracteres.
- `nome`, `categoriaId`, `precoVenda` e `controlaEstoque` são obrigatórios para
  produto.
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
  "controlaEstoque": true,
  "unidadeEstoque": "UNIDADE",
  "quantidadeEstoque": 24,
  "quantidadeBaixaPorVenda": 1,
  "estoqueMinimo": 6
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
- Importação de produtos.
- Exclusão física de produtos.
- Relatórios por produto.

## Próximo passo relacionado

- Usar produtos cadastrados no módulo de Pagamentos e Fechamento.
