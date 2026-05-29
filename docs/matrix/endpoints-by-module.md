# Endpoints por Modulo

## Objetivo

Mapear as rotas reais registradas em `app/api.py` e nos controllers em
`app/adapter/controllers/`. Esta matriz nao inventa endpoints futuros.

## Health

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `GET` | `/health` | `app/api.py` | Verificar saude da API | Implementado |

## Produtos e Categorias

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/categorias` | `categoria_produto_controller.py` | Cadastrar categoria | Implementado |
| `GET` | `/api/categorias` | `categoria_produto_controller.py` | Listar categorias | Implementado |
| `GET` | `/api/categorias/{categoria_id}` | `categoria_produto_controller.py` | Consultar categoria | Implementado |
| `PUT` | `/api/categorias/{categoria_id}` | `categoria_produto_controller.py` | Editar categoria | Implementado |
| `PATCH` | `/api/categorias/{categoria_id}/ativar` | `categoria_produto_controller.py` | Ativar categoria | Implementado |
| `PATCH` | `/api/categorias/{categoria_id}/inativar` | `categoria_produto_controller.py` | Inativar categoria | Implementado |
| `POST` | `/api/produtos` | `produto_controller.py` | Cadastrar produto | Implementado |
| `GET` | `/api/produtos` | `produto_controller.py` | Listar produtos | Implementado |
| `GET` | `/api/produtos/{produto_id}` | `produto_controller.py` | Consultar produto | Implementado |
| `PUT` | `/api/produtos/{produto_id}` | `produto_controller.py` | Editar produto | Implementado |
| `PATCH` | `/api/produtos/{produto_id}/ativar` | `produto_controller.py` | Ativar produto | Implementado |
| `PATCH` | `/api/produtos/{produto_id}/inativar` | `produto_controller.py` | Inativar produto | Implementado |
| `GET` | `/api/produtos/{produto_id}/composicao` | `produto_composicao_controller.py` | Consultar composicao | Implementado |
| `POST` | `/api/produtos/{produto_id}/composicao/componentes` | `produto_composicao_controller.py` | Adicionar componente | Implementado |
| `PUT` | `/api/produtos/{produto_id}/composicao/componentes/{componente_id}` | `produto_composicao_controller.py` | Editar componente | Implementado |
| `DELETE` | `/api/produtos/{produto_id}/composicao/componentes/{componente_id}` | `produto_composicao_controller.py` | Remover componente | Implementado |

## Estoque

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `GET` | `/api/estoque` | `estoque_controller.py` | Consultar estoque | Implementado |
| `GET` | `/api/estoque/baixo` | `estoque_controller.py` | Consultar estoque baixo | Implementado |
| `GET` | `/api/estoque/negativo` | `estoque_controller.py` | Consultar estoque negativo | Implementado |
| `GET` | `/api/estoque/produtos/{produto_id}/movimentos` | `estoque_controller.py` | Consultar movimentos do produto | Implementado |
| `POST` | `/api/estoque/produtos/{produto_id}/entrada` | `estoque_controller.py` | Registrar entrada manual | Implementado |
| `POST` | `/api/estoque/produtos/{produto_id}/ajuste` | `estoque_controller.py` | Registrar ajuste manual | Implementado |

## Clientes

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/clientes` | `cliente_controller.py` | Cadastrar cliente | Implementado |
| `GET` | `/api/clientes` | `cliente_controller.py` | Listar e buscar clientes | Implementado |
| `GET` | `/api/clientes/{cliente_id}` | `cliente_controller.py` | Consultar cliente | Implementado |
| `PUT` | `/api/clientes/{cliente_id}` | `cliente_controller.py` | Editar cliente | Implementado |
| `PATCH` | `/api/clientes/{cliente_id}/ativar` | `cliente_controller.py` | Ativar cliente | Implementado |
| `PATCH` | `/api/clientes/{cliente_id}/inativar` | `cliente_controller.py` | Inativar cliente | Implementado |
| `GET` | `/api/clientes/{cliente_id}/pendencias` | `cliente_controller.py` | Consultar pendencias do cliente | Implementado |

## Comandas e Itens

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/comandas` | `comanda_controller.py` | Criar comanda | Implementado |
| `GET` | `/api/comandas` | `comanda_controller.py` | Listar comandas | Implementado |
| `GET` | `/api/comandas/abertas` | `comanda_controller.py` | Listar comandas abertas | Implementado |
| `GET` | `/api/comandas/{comanda_id}` | `comanda_controller.py` | Consultar comanda | Implementado |
| `PATCH` | `/api/comandas/{comanda_id}/cliente` | `comanda_controller.py` | Vincular cliente | Implementado |
| `POST` | `/api/comandas/{comanda_id}/itens` | `comanda_controller.py` | Adicionar item | Implementado |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/incrementar` | `comanda_controller.py` | Aumentar item | Implementado |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/diminuir` | `comanda_controller.py` | Diminuir item | Implementado |
| `DELETE` | `/api/comandas/{comanda_id}/itens/{item_id}` | `comanda_controller.py` | Remover item | Implementado |
| `PATCH` | `/api/comandas/{comanda_id}/cancelar` | `comanda_controller.py` | Cancelar comanda | Implementado |

## Pagamentos e Fechamento

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/comandas/{comanda_id}/fechar` | `pagamento_controller.py` | Fechar comanda paga | Implementado |
| `GET` | `/api/comandas/{comanda_id}/pagamentos` | `pagamento_controller.py` | Listar pagamentos da comanda | Implementado |

## Fiado / Pendencias

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/comandas/{comanda_id}/fiado` | `fiado_controller.py` | Marcar comanda como fiado | Implementado |
| `GET` | `/api/fiados` | `fiado_controller.py` | Listar pendencias | Implementado |
| `GET` | `/api/fiados/vencidos` | `fiado_controller.py` | Listar pendencias vencidas | Implementado |
| `GET` | `/api/fiados/{comanda_id}` | `fiado_controller.py` | Consultar pendencia | Implementado |
| `POST` | `/api/fiados/{comanda_id}/quitar` | `fiado_controller.py` | Quitar pendencia | Implementado |

## Caixa Diario

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `POST` | `/api/caixas/abrir` | `caixa_controller.py` | Abrir caixa | Implementado |
| `GET` | `/api/caixas/aberto` | `caixa_controller.py` | Consultar caixa aberto | Implementado |
| `GET` | `/api/caixas` | `caixa_controller.py` | Listar caixas | Implementado |
| `GET` | `/api/caixas/{caixa_id}` | `caixa_controller.py` | Consultar caixa por ID | Implementado |
| `POST` | `/api/caixas/{caixa_id}/reforcos` | `caixa_controller.py` | Registrar reforco | Implementado |
| `POST` | `/api/caixas/{caixa_id}/sangrias` | `caixa_controller.py` | Registrar sangria | Implementado |
| `POST` | `/api/caixas/{caixa_id}/fechar` | `caixa_controller.py` | Fechar caixa | Implementado |

## Relatorios basicos

| Metodo | Endpoint | Controller | Caso de uso | Status |
|---|---|---|---|---|
| `GET` | `/api/relatorios/diario` | `relatorio_controller.py` | Consultar relatorio diario | Implementado |
| `GET` | `/api/relatorios/caixas/{caixa_id}` | `relatorio_controller.py` | Consultar relatorio por caixa | Implementado |
| `GET` | `/api/relatorios/produtos-mais-vendidos` | `relatorio_controller.py` | Listar produtos mais vendidos | Implementado |
| `GET` | `/api/relatorios/fiados` | `relatorio_controller.py` | Consultar relatorio de fiados | Implementado |
| `GET` | `/api/relatorios/estoque` | `relatorio_controller.py` | Consultar relatorio de estoque | Implementado |
| `GET` | `/api/relatorios/comandas` | `relatorio_controller.py` | Consultar comandas por status | Implementado |

## Modulos sem endpoints implementados

| Modulo | Status | Observacao |
|---|---|---|
| Configuracoes | Pendente | Existe entidade `ConfiguracaoSistema`, mas nao ha controller/rotas |
| Acesso / Senha simples | Pendente | Sem controller/rotas |
| Frontend operacional | Futuro | Fora da API atual |
| Release MVP | Futuro | Nao e endpoint |
