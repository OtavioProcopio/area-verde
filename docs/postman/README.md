# Postman

Arquivos para importar e testar a API pelo Postman.

- [Collection](area-verde-collection.json)
- [Ambiente de desenvolvimento](area-verde-dev.json)

A collection cobre:

- health check;
- categorias e produtos;
- consultas e movimentos de estoque;
- abertura, itens, cancelamento e consulta de comandas;
- abertura, consulta, reforço, sangria e fechamento de caixa;
- fechamento de comanda com caixa aberto e consulta de pagamentos.

Por padrão, o ambiente aponta para a API local. Ajuste `baseUrl` conforme o modo
de execução usado:

- Local com `make run`: `http://localhost:8001`
- Docker Compose: `http://localhost:58001`
