# Postman

Arquivos para importar e testar a API pelo Postman.

- [Collection](area-verde-collection.json)
- [Ambiente de desenvolvimento](area-verde-dev.json)

A collection cobre:

- health check;
- categorias e produtos;
- consultas e movimentos de estoque;
- cadastro e consulta de clientes;
- abertura, itens, cancelamento e consulta de comandas;
- vínculo de cliente em comanda;
- marcação, listagem e quitação de fiado;
- abertura, consulta, reforço, sangria e fechamento de caixa;
- regressão de fechamento bloqueado com comandas abertas;
- fechamento de comanda com caixa aberto e consulta de pagamentos.

Por padrão, o ambiente aponta para a API local. Ajuste `baseUrl` conforme o modo
de execução usado:

- Local com `make run`: `http://localhost:8001`
- Docker Compose: `http://localhost:58001`
