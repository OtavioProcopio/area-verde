# Area Verde API Documentation

Esta pasta contém a documentação inicial do sistema Area Verde, incluindo os
diagramas de domínio, a collection Postman e o ambiente de desenvolvimento.

## Objetivo

O Area Verde API apoiará a operação diária do bar, com foco inicial em comandas,
produtos, estoque, pagamentos, fiado e caixa. Esta primeira versão entrega o
bootstrap técnico, o modelo de dados inicial e a documentação-base para guiar as
próximas implementações.

## Arquivos

- `class_diagram.md` - Diagrama Mermaid com classes, enums e relacionamentos.
- `use_case_diagram.md` - Diagrama Mermaid com atores, módulos e casos de uso.
- `area_verde_collection.json` - Collection Postman inicial.
- `area_verde_dev.json` - Ambiente Postman de desenvolvimento.
- `git-flow.md` - Regras de branches, releases, hotfixes e proteção manual.
- `development-workflow.md` - Rotina de desenvolvimento e validações locais.
- `ci-cd.md` - Workflows de integração e entrega contínua.

## Como usar no Postman

1. Importe a collection `area_verde_collection.json`.
2. Importe o ambiente `area_verde_dev.json`.
3. Selecione o ambiente `Area Verde API - Dev`.
4. Execute a request `GET /health`.

Por padrão, o ambiente aponta para `http://localhost:8001`, usado pelo comando
`make run`. Ao usar Docker Compose, altere `baseUrl` para
`http://localhost:58001`.

## Endpoint disponível

### Health

- `GET /health` - Verificação de saúde da API.

## Endpoints planejados

Os endpoints abaixo ainda não foram implementados nesta etapa. Eles estão
registrados como norte inicial do MVP operacional.

### Produtos

- Criar, editar, inativar e consultar categorias.
- Criar, editar, inativar e consultar produtos.
- Definir controle de estoque e quantidade de baixa por venda.

### Estoque

- Consultar estoque atual.
- Registrar entrada e ajuste manual.
- Consultar produtos com estoque baixo e movimentos de estoque.
- Alertar estoque negativo quando configurado.

### Comandas

- Criar, listar, buscar, cancelar e fechar comandas.
- Adicionar, incrementar, decrementar e remover itens.
- Recalcular total e movimentar estoque automaticamente.

### Fiado

- Marcar comanda como fiado.
- Listar fiados pendentes.
- Destacar fiados vencidos pelo prazo configurado.
- Registrar pagamento de fiado.

### Caixa

- Abrir e fechar caixa diário.
- Registrar pagamentos, sangrias e reforços.
- Calcular dinheiro esperado e diferença de caixa.

### Relatórios

- Relatório diário.
- Relatório por forma de pagamento.
- Produtos mais vendidos.
- Fiados.
- Estoque baixo.
- Comandas.

## Entidades principais

- `ConfiguracaoSistema`
- `CategoriaProduto`
- `Produto`
- `Comanda`
- `ItemComanda`
- `Caixa`
- `Pagamento`
- `MovimentoCaixa`
- `MovimentoEstoque`
