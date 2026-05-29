# Matriz Funcional do MVP

## Objetivo

Relacionar modulos, casos de uso, endpoints, entidades, testes e status de
implementacao. A matriz foi conferida contra `app/api.py`,
`app/adapter/controllers/`, `app/core/domain/models.py` e `app/*_test.py`.

## Legenda de status

| Status | Significado |
|---|---|
| Implementado | Existe no backend e possui documentacao minima |
| Parcial | Existe parte estrutural, mas ainda ha lacunas operacionais |
| Pendente | Ainda nao implementado |
| Futuro | Fora do MVP imediato |

## Matriz

| Modulo | Caso de uso | Endpoint/API | Entidades | Testes | Status | Observacoes |
|---|---|---|---|---|---|---|
| Health | Verificar saude da API | `GET /health` | N/A | `app/health_test.py` | Implementado | Endpoint tecnico |
| Produtos e Categorias | Cadastrar, listar, consultar, editar, ativar e inativar categoria | `/api/categorias*` | `CategoriaProduto` | `app/produtos_categorias_test.py` | Implementado | Sem exclusao fisica |
| Produtos e Categorias | Cadastrar, listar, consultar, editar, ativar e inativar produto | `/api/produtos*` | `Produto`, `CategoriaProduto`, `UnidadeEstoque` | `app/produtos_categorias_test.py` | Implementado | Inclui controle de estoque por produto |
| Produtos Compostos | Modelar e gerenciar composicao | `/api/produtos/{produto_id}/composicao*` | `Produto`, `TipoProduto`, `ProdutoComposicao` | `app/produtos_categorias_test.py`, `app/produto_composicao_test.py`, `app/bootstrap_test.py` | Implementado | Produto composto usa componentes simples com controle de estoque |
| Estoque | Consultar estoque, baixo e negativo | `GET /api/estoque*` | `Produto`, `MovimentoEstoque` | `app/estoque_test.py` | Implementado | Lista apenas produtos com controle de estoque |
| Estoque | Registrar entrada e ajuste manual | `POST /api/estoque/produtos/{produto_id}/entrada`, `POST /api/estoque/produtos/{produto_id}/ajuste` | `Produto`, `MovimentoEstoque` | `app/estoque_test.py` | Implementado | Movimentos manuais ficam historizados |
| Estoque | Baixa/devolucao automatica por comanda | API de itens de comanda | `Produto`, `ProdutoComposicao`, `ItemComanda`, `MovimentoEstoque` | `app/comandas_test.py` | Implementado | Produto simples baixa a si mesmo; composto baixa componentes |
| Caixa Diario | Abrir e consultar caixa | `POST /api/caixas/abrir`, `GET /api/caixas/aberto`, `GET /api/caixas/{caixa_id}` | `Caixa`, `MovimentoCaixa` | `app/caixa_test.py` | Implementado | Criar comanda exige caixa aberto |
| Caixa Diario | Registrar reforco e sangria | `POST /api/caixas/{caixa_id}/reforcos`, `POST /api/caixas/{caixa_id}/sangrias` | `Caixa`, `MovimentoCaixa` | `app/caixa_test.py` | Implementado | Atualiza dinheiro esperado |
| Caixa Diario | Fechar caixa | `POST /api/caixas/{caixa_id}/fechar` | `Caixa`, `Comanda`, `Pagamento` | `app/caixa_test.py`, `app/fiado_test.py` | Implementado | Bloqueia comanda `ABERTA`, permite `PENDENTE` |
| Clientes | Cadastrar, listar, consultar e editar cliente | `/api/clientes*` | `Cliente` | `app/clientes_test.py` | Implementado | Busca por nome/apelido e telefone |
| Clientes | Ativar, inativar e validar duplicidade ativa | `PATCH /api/clientes/{cliente_id}/ativar`, `PATCH /api/clientes/{cliente_id}/inativar` | `Cliente` | `app/clientes_test.py` | Implementado | Cliente inativo mantem historico |
| Clientes | Consultar pendencias do cliente | `GET /api/clientes/{cliente_id}/pendencias` | `Cliente`, `Comanda` | `app/clientes_test.py`, `app/fiado_test.py` | Implementado | Pendencias de inativos continuam visiveis |
| Comandas e Itens | Criar comanda rapida ou com cliente | `POST /api/comandas` | `Comanda`, `Cliente`, `Caixa` | `app/comandas_test.py`, `app/fiado_test.py` | Implementado | Exige caixa aberto |
| Comandas e Itens | Listar e consultar comandas | `GET /api/comandas`, `GET /api/comandas/abertas`, `GET /api/comandas/{comanda_id}` | `Comanda`, `ItemComanda` | `app/comandas_test.py` | Implementado | Filtros por status, nome e data |
| Comandas e Itens | Vincular cliente a comanda aberta | `PATCH /api/comandas/{comanda_id}/cliente` | `Comanda`, `Cliente` | `app/fiado_test.py` | Implementado | Cliente deve estar ativo |
| Comandas e Itens | Adicionar, incrementar, diminuir e remover item | `/api/comandas/{comanda_id}/itens*` | `Comanda`, `ItemComanda`, `Produto`, `MovimentoEstoque` | `app/comandas_test.py` | Implementado | Recalcula total e movimenta estoque |
| Comandas e Itens | Cancelar comanda | `PATCH /api/comandas/{comanda_id}/cancelar` | `Comanda`, `ItemComanda`, `MovimentoEstoque` | `app/comandas_test.py` | Implementado | Devolve estoque proporcional |
| Pagamentos e Fechamento | Fechar comanda com DINHEIRO, PIX ou CARTAO | `POST /api/comandas/{comanda_id}/fechar` | `Comanda`, `Pagamento`, `Caixa` | `app/pagamentos_test.py`, `app/caixa_test.py` | Implementado | `FIADO` nao e pagamento recebido |
| Pagamentos e Fechamento | Listar pagamentos da comanda | `GET /api/comandas/{comanda_id}/pagamentos` | `Pagamento` | `app/pagamentos_test.py` | Implementado | Retorna lista vazia quando nao ha pagamentos |
| Fiado / Pendencias | Marcar comanda como fiado | `POST /api/comandas/{comanda_id}/fiado` | `Comanda`, `Cliente`, `Caixa` | `app/fiado_test.py` | Implementado | Cliente cadastrado e ativo obrigatorio |
| Fiado / Pendencias | Listar, filtrar, consultar vencidos e pendencia por comanda | `GET /api/fiados*` | `Comanda`, `Cliente` | `app/fiado_test.py` | Implementado | `PENDENTE` representa valor a receber |
| Fiado / Pendencias | Quitar fiado | `POST /api/fiados/{comanda_id}/quitar` | `Comanda`, `Pagamento`, `Caixa`, `FormaPagamento` | `app/fiado_test.py` | Implementado | Quitacao exige caixa aberto e nao aceita `FIADO` |
| Relatorios basicos | Relatorio diario, por caixa, produtos mais vendidos, fiados, estoque e comandas | `/api/relatorios*` | `Comanda`, `ItemComanda`, `Produto`, `Cliente`, `Pagamento`, `Caixa`, `MovimentoCaixa`, `MovimentoEstoque` | `app/relatorios_test.py` | Implementado | Consulta consolidada sem alterar dados |
| Configuracoes | Nome do bar, dias de fiado, estoque negativo e senha simples | A definir | `ConfiguracaoSistema` | A criar | Parcial | Entidade existe, modulo operacional pendente |
| Acesso / Senha | Acessar sistema com senha simples | A definir | `ConfiguracaoSistema` | A criar | Pendente | Sem endpoints ou use cases |
| Release MVP | Preparar versao estavel | N/A | N/A | Validacoes de CI | Futuro | Apos modulos essenciais |
| Frontend operacional | Operacao visual do bar | N/A | API existente | A definir | Futuro | Fora do backend atual |
