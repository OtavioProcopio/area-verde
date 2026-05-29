# Postman

Arquivos para importar e testar a API pelo Postman.

- [Collection](area-verde-collection.json)
- [Ambiente de desenvolvimento](area-verde-dev.json)

A collection cobre:

- health check;
- abertura de caixa antes da operação;
- categorias, produtos simples, produtos compostos e composicao;
- consultas e movimentos de estoque;
- cadastro e consulta de clientes;
- bloqueio de cliente ativo duplicado;
- abertura, itens, cancelamento e consulta de comandas;
- vínculo de cliente em comanda;
- abertura rápida com caixa aberto;
- marcação, listagem e quitação de fiado;
- consulta de pendências após inativação de cliente;
- abertura, consulta, reforço, sangria e fechamento de caixa;
- regressão de fechamento bloqueado com comandas abertas;
- fechamento de comanda com caixa aberto e consulta de pagamentos;
- venda manual de produto composto e consulta de movimentos dos componentes;
- relatórios diário, por caixa, produtos mais vendidos, estoque consumido,
  fiados, estoque e comandas.

## Fluxo operacional recomendado

1. `GET /health`
2. `POST /api/caixas/abrir`
3. `POST /api/categorias`
4. `POST /api/produtos`
5. Criar produtos simples componentes com controle de estoque.
6. Criar produto composto com `tipoProduto=COMPOSTO`.
7. Configurar composicao em `/api/produtos/{produto_id}/composicao/componentes`.
8. `POST /api/estoque/produtos/{produto_id}/entrada` ou `/ajuste`
9. `POST /api/clientes`
10. `POST /api/comandas` com `nomeCliente`
11. `POST /api/comandas` com `clienteId`
12. `POST /api/comandas/{comanda_id}/itens`
13. Consultar movimentos em `/api/estoque/produtos/{produto_id}/movimentos`
14. Resolver a comanda por um dos caminhos:
    - `POST /api/comandas/{comanda_id}/fechar`, se o cliente pagou.
    - `POST /api/comandas/{comanda_id}/fiado`, se ficou pendente.
15. Se ficou fiado, usar `GET /api/fiados`
16. Se for quitar, usar `POST /api/fiados/{comanda_id}/quitar`
17. Fechar caixa com `POST /api/caixas/{caixa_id}/fechar`
18. Consultar venda em `/api/relatorios/produtos-mais-vendidos`
19. Consultar consumo fisico em `/api/relatorios/estoque-consumido`

Nao inclua na collection endpoints de Configuracoes, Acesso ou Frontend enquanto
esses modulos nao existirem no backend.

Por padrão, o ambiente aponta para a API local. Ajuste `baseUrl` conforme o modo
de execução usado:

- Local com `make run`: `http://localhost:8001`
- Docker Compose: `http://localhost:58001`
