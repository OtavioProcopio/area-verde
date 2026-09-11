# Testes por Modulo

## Objetivo

Relacionar os arquivos de teste existentes com os modulos do MVP. A coluna de
lacunas registra pontos ainda nao cobertos ou que devem ser reavaliados no
modulo de Relatorios.

| Modulo | Arquivo de teste | O que cobre | Lacunas |
|---|---|---|---|
| Health | `app/health_test.py` | `GET /health` | Sem lacuna relevante |
| Bootstrap / Infra | `app/bootstrap_test.py` | criacao da app, schema SQLModel, indices, defaults e container | Nao cobre execucao real de migrations em PostgreSQL |
| Produtos e Categorias | `app/produtos_categorias_test.py` | ciclo de vida de categoria/produto, filtros, validacoes, ML e produto sem estoque | Nao cobre relatorios por produto |
| Produtos Compostos | `app/produto_composicao_test.py`, `app/comandas_test.py`, `app/relatorios_test.py` | endpoints de composicao, validacoes, venda de composto, baixa/devolucao de componentes, transacao, produto vendido e consumo de estoque por componente | Nao cobre produto composto dentro de produto composto, fora do MVP |
| Estoque | `app/estoque_test.py` | consulta de estoque, baixo, negativo, entrada, ajuste, historico e validacoes | Nao cobre inventario ou relatorio consolidado |
| Comandas e Itens | `app/comandas_test.py` | criacao, caixa obrigatorio, filtros, itens, snapshots, baixa/devolucao e cancelamento | Nao cobre fluxo visual/front-end |
| Pagamentos e Fechamento | `app/pagamentos_test.py` | fechamento por DINHEIRO/PIX/CARTAO, bloqueio de FIADO, valores invalidos, listagem de pagamentos e bloqueio de alteracoes | Nao cobre integracao real com meios de pagamento |
| Caixa Diario | `app/caixa_test.py` | abertura, caixa aberto, listagem, reforco, sangria, fechamento, vinculo de pagamento e regressao de caixa fechado | Nao cobre relatorio de fechamento por caixa |
| Clientes | `app/clientes_test.py` | cadastro, busca, filtros, edicao, ativacao, inativacao e duplicidade normalizada | Nao cobre importacao ou campos fiscais, fora do MVP |
| Fiado / Pendencias | `app/fiado_test.py` | cliente em comanda, fiado, vencidos, consulta, quitacao, cliente inativo, caixa aberto e fechamento com pendencias | Nao cobre pagamento parcial, juros ou cobranca automatica |
| Relatorios basicos | `app/relatorios_test.py` | diario, caixa, produtos mais vendidos, consumo de estoque, fiados, estoque, comandas, filtros e validacoes | Nao cobre exportacao PDF/Excel ou dashboard visual, fora do escopo |
| Configuracoes | `app/configuracoes_test.py` | consulta, criacao padrao, update, patch, CORS e regra de estoque negativo | Nao cobre interface visual do frontend |
| Acesso / Senha | `app/configuracoes_test.py` | definir senha, alterar senha, validar senha e erros esperados | Nao cobre sessao/token, fora do MVP |
| Frontend operacional | A criar | Fora da API atual | Definir estrategia propria quando o frontend existir |
