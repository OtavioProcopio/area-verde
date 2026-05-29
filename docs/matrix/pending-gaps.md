# Pendencias, Lacunas e Inconsistencias

## Alta prioridade

| Item | Tipo | Local | Descricao | Recomendacao |
|---|---|---|---|---|
| Relatorios basicos | Funcionalidade pendente | `docs/modules/relatorios.md` | Proximo modulo funcional ainda nao possui endpoints, use cases ou testes | Implementar modulo 8 usando as entidades ja disponiveis |
| Configuracoes operacionais | Funcionalidade pendente | `ConfiguracaoSistema` / `docs/modules/configuracoes.md` | A entidade existe, mas nao ha controller, service operacional ou endpoints | Definir escopo antes do release MVP |
| Acesso / Senha simples | Funcionalidade pendente | Roadmap | `senha_acesso_hash` existe na entidade de configuracao, mas nao ha fluxo de acesso | Implementar somente depois de relatorios/configuracoes, conforme roadmap |

## Media prioridade

| Item | Tipo | Local | Descricao | Recomendacao |
|---|---|---|---|---|
| Testes de relatorios | Cobertura ausente | `app/*_test.py` | Nao ha testes porque o modulo ainda nao existe | Criar testes de agregacao no PR do modulo 8 |
| Parametro `permitir_estoque_negativo` | Decisao futura | `ConfiguracaoSistema` e Estoque/Comandas | A entidade tem o parametro, mas a regra operacional ainda permite estoque negativo no MVP | Decidir no modulo Configuracoes se esse parametro passa a governar vendas |
| Collection Postman | Manutencao continua | `docs/postman/area-verde-collection.json` | A collection foi revisada como fluxo atual, mas deve acompanhar novos relatorios | Adicionar somente endpoints reais quando o modulo 8 existir |

## Baixa prioridade

| Item | Tipo | Local | Descricao | Recomendacao |
|---|---|---|---|---|
| Diagramas globais grandes | Manutenibilidade | `docs/diagrams/*.md` | Os diagramas globais ficaram abrangentes depois de Clientes e Fiado | Manter diagramas por modulo como fonte de detalhe |
| Integracoes externas | Fora de escopo | Pagamentos / Fiscal / Impressao | Pix, TEF, cartao real, nota fiscal e impressao nao fazem parte do MVP atual | Reavaliar apos release MVP |
| Frontend operacional | Futuro | Roadmap | Ainda nao ha aplicacao visual para atendimento | Iniciar depois da API MVP consolidada |

## Itens corrigidos neste PR documental

| Item | Situacao anterior | Correcao |
|---|---|---|
| Diagrama de classes sem `Cliente` | Desatualizado apos o modulo Clientes | `Cliente` e relacionamentos foram adicionados |
| Campos atuais de `Comanda` incompletos | Faltavam `caixaOrigemId`, `clienteId`, `nomeClienteSnapshot` e `pendenteEm` | Campos incluidos no diagrama global |
| Caso de uso antigo "Bloquear FIADO no MVP" | Texto conflitava com modulo Fiado implementado | Substituido por "FIADO vira pendencia" e "Bloquear FIADO como pagamento recebido" |
