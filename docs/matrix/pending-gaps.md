# Pendencias, Lacunas e Inconsistencias

## Alta prioridade

| Item | Tipo | Local | Descricao | Recomendacao |
|---|---|---|---|---|
| Release MVP backend | Consolidacao | README, matrizes e workflows | O backend ja cobre os modulos do MVP, mas ainda precisa consolidar checklist final de release | Fechar validacoes finais e preparar PR de release |

## Media prioridade

| Item | Tipo | Local | Descricao | Recomendacao |
|---|---|---|---|---|
| Relatorios avancados | Fora de escopo | `docs/modules/relatorios.md` | O modulo atual cobre consultas basicas, sem exportacao ou dashboard | Reavaliar PDF, Excel, CSV e graficos apos o MVP |
| Collection Postman | Manutencao continua | `docs/postman/area-verde-collection.json` | A collection acompanha os relatorios basicos atuais, mas deve seguir novos endpoints | Atualizar somente quando novos endpoints reais existirem |

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
| Relatorio de consumo por componente | Nao existia endpoint dedicado | Implementado em `GET /api/relatorios/estoque-consumido`, baseado em `MovimentoEstoque` |
| Modulo 9 - Produtos compostos | Issues #17 a #21 pendentes | Consolidado com modelagem, endpoints, comanda/estoque, relatorios, docs e Postman |
