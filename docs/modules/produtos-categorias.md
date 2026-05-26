# Produtos e Categorias

Modulo responsavel pelo cadastro base de produtos do bar e suas categorias.
Ele viabiliza os proximos modulos de estoque e comandas, sem realizar baixa
automatica de estoque por venda neste momento.

## Categorias

Endpoints:

- `POST /api/categorias`
- `GET /api/categorias`
- `GET /api/categorias?ativo=true`
- `GET /api/categorias/{id}`
- `PUT /api/categorias/{id}`
- `PATCH /api/categorias/{id}/ativar`
- `PATCH /api/categorias/{id}/inativar`

Request:

```json
{
  "nome": "Cervejas"
}
```

Response:

```json
{
  "id": 1,
  "nome": "Cervejas",
  "ativo": true,
  "criadoEm": "2026-05-26T10:30:00",
  "atualizadoEm": "2026-05-26T10:30:00"
}
```

Regras principais:

- `nome` e obrigatorio, nao pode ser vazio e possui limite de 120 caracteres.
- Categorias iniciam ativas.
- Categorias nao sao excluidas fisicamente; use inativacao logica.
- Nao pode existir mais de uma categoria ativa com o mesmo nome.
- Uma categoria inativa nao pode ser usada para cadastrar ou editar produto.

## Produtos

Endpoints:

- `POST /api/produtos`
- `GET /api/produtos`
- `GET /api/produtos?ativo=true`
- `GET /api/produtos?categoriaId=1`
- `GET /api/produtos?nome=cerveja`
- `GET /api/produtos/{id}`
- `PUT /api/produtos/{id}`
- `PATCH /api/produtos/{id}/ativar`
- `PATCH /api/produtos/{id}/inativar`

Produto por unidade:

```json
{
  "nome": "Cerveja lata",
  "categoriaId": 1,
  "precoVenda": 7.00,
  "controlaEstoque": true,
  "unidadeEstoque": "UNIDADE",
  "quantidadeEstoque": 24,
  "quantidadeBaixaPorVenda": 1,
  "estoqueMinimo": 6
}
```

Produto fracionado em ml:

```json
{
  "nome": "Dose de pinga",
  "categoriaId": 2,
  "precoVenda": 5.00,
  "controlaEstoque": true,
  "unidadeEstoque": "ML",
  "quantidadeEstoque": 1000,
  "quantidadeBaixaPorVenda": 50,
  "estoqueMinimo": 200
}
```

Produto sem controle de estoque:

```json
{
  "nome": "Taxa de serviço",
  "categoriaId": 5,
  "precoVenda": 2.00,
  "controlaEstoque": false
}
```

Response:

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

Regras principais:

- `nome`, `categoriaId`, `precoVenda` e `controlaEstoque` sao obrigatorios.
- `precoVenda` nao pode ser negativo.
- Produtos iniciam ativos.
- Produtos nao sao excluidos fisicamente; use inativacao logica.
- Se `controlaEstoque=true`, `unidadeEstoque` e obrigatoria,
  `quantidadeBaixaPorVenda` deve ser maior que zero, e estoque atual/minimo nao
  podem ser negativos.
- Se `controlaEstoque=false`, a API persiste estoque zerado com
  `unidadeEstoque=UNIDADE`.

## Dados Iniciais

A migration do modulo cria categorias iniciais de forma idempotente:

- Cervejas
- Doses
- Refrigerantes
- Salgados
- Salgadinhos
- Avulsos
- Outros

Nenhum produto real e cadastrado automaticamente.

## Proxima Etapa

O modulo recomendado apos Produtos e Categorias e Estoque, pois ele depende dos
produtos cadastrados e sera usado depois por comandas.
