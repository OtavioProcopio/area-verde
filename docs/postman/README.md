# Postman

Arquivos para importar e testar a API pelo Postman.

- [Collection](area-verde-collection.json)
- [Ambiente de desenvolvimento](area-verde-dev.json)

A collection cobre:

- health check;
- abertura de caixa antes da operação;
- categorias e produtos;
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
- fechamento de comanda com caixa aberto e consulta de pagamentos.
- relatórios diário, por caixa, produtos mais vendidos, fiados, estoque e
  comandas.

## Fluxo operacional recomendado

1. `GET /health`
2. `POST /api/caixas/abrir`
3. `POST /api/categorias`
4. `POST /api/produtos`
5. Opcionalmente, configurar composicao em `/api/produtos/{produto_id}/composicao`
6. `POST /api/estoque/produtos/{produto_id}/entrada` ou `/ajuste`
7. `POST /api/clientes`
8. `POST /api/comandas` com `nomeCliente`
9. `POST /api/comandas` com `clienteId`
10. `POST /api/comandas/{comanda_id}/itens`
11. Resolver a comanda por um dos caminhos:
    - `POST /api/comandas/{comanda_id}/fechar`, se o cliente pagou.
    - `POST /api/comandas/{comanda_id}/fiado`, se ficou pendente.
12. Se ficou fiado, usar `GET /api/fiados`
13. Se for quitar, usar `POST /api/fiados/{comanda_id}/quitar`
14. Fechar caixa com `POST /api/caixas/{caixa_id}/fechar`
15. Consultar relatórios em `GET /api/relatorios/*`

Os endpoints de composicao de produtos compostos existem no backend. A
collection completa do Modulo 9 fica para a etapa documental final.

Nao inclua na collection endpoints de Configuracoes, Acesso ou Frontend enquanto
esses modulos nao existirem no backend.

Por padrão, o ambiente aponta para a API local. Ajuste `baseUrl` conforme o modo
de execução usado:

- Local com `make run`: `http://localhost:8001`
- Docker Compose: `http://localhost:58001`
