# Tarefas — Fiado avulso retroativo

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.

## Fase 1 — Domínio

Nenhuma tarefa: a feature reaproveita a entidade `Comanda` já existente (ver `plan.md` §
Decisões técnicas), sem entidade, enum, exception ou migration nova.

## Fase 2 — Aplicação

> Todas as tarefas de teste desta fase escrevem no mesmo arquivo (`app/fiado_test.py`, convenção
> já existente do repositório — ver desvio documentado em `plan.md`), por isso nenhuma é `[P]`.

- [x] T001 Escrever teste `test_deve_lancar_fiado_avulso_com_data_de_origem_passada_sem_comanda` em `app/fiado_test.py` — cria cliente, sem comanda nem caixa, lança avulso com valor, data de origem de um mês atrás e observação; espera pendência criada com `pendenteEm` na data informada e `observacao` preservada (RF-01, RF-02, RF-03, RF-09)
- [x] T002 Escrever teste `test_deve_aceitar_vencimento_informado_manualmente_no_fiado_avulso` em `app/fiado_test.py` — lança avulso com `vencimentoEm` explícito no futuro e confirma que é respeitado; lança outro sem `vencimentoEm` e confirma o padrão do sistema (hoje + dias configurados), igual ao fiado por comanda (RF-10)
- [x] T003 Escrever teste `test_deve_lancar_fiado_avulso_sem_caixa_aberto` em `app/fiado_test.py` — garante que nenhum caixa está aberto e confirma que o lançamento é aceito mesmo assim (RF-11)
- [x] T004 Escrever teste `test_deve_rejeitar_fiado_avulso_com_data_de_origem_no_futuro` em `app/fiado_test.py` — espera `400` com `code` `data_origem_invalida` e nenhuma pendência criada (RF-04)
- [x] T005 Escrever teste `test_deve_rejeitar_fiado_avulso_com_valor_devido_invalido` em `app/fiado_test.py` — valor zero e valor negativo, espera `400`/`422` e nenhuma pendência criada (RF-05)
- [x] T006 Escrever teste `test_deve_rejeitar_fiado_avulso_para_cliente_inexistente` em `app/fiado_test.py` — `clienteId` inexistente, espera `404` com `code` `cliente_nao_encontrado` (RF-06)
- [x] T007 Escrever teste `test_deve_rejeitar_fiado_avulso_para_cliente_inativo` em `app/fiado_test.py` — cliente inativado antes do lançamento, espera `400` com `code` `cliente_inativo` (RF-06)
- [x] T008 Escrever teste `test_deve_listar_fiado_avulso_junto_com_pendencias_do_cliente` em `app/fiado_test.py` — após lançar avulso, confirma que aparece em `GET /api/fiados`, `GET /api/fiados/vencidos` (quando vencido) e `GET /api/clientes/{id}/pendencias`, junto de uma pendência originada de comanda do mesmo cliente (RF-07)
- [x] T009 Escrever teste `test_deve_quitar_fiado_avulso_pelo_fluxo_existente_e_somar_no_caixa` em `app/fiado_test.py` — abre caixa, lança avulso, quita via `POST /api/fiados/{id}/quitar` em `DINHEIRO`, confirma `status FECHADA` e `dinheiro_esperado` do caixa somado (RF-08)
- [x] T010 Implementar `FiadoService.lancar_avulso(cliente_id, valor, data_origem, vencimento_em=None, observacao=None)` em `app/core/application/use_cases/fiado_service.py` — valida cliente (existe e ativo), valor (`valor_devido_invalido` se `<= 0`), data de origem (`data_origem_invalida` se no futuro), resolve vencimento com `_resolve_vencimento` já existente, monta `Comanda` com `status=PENDENTE`, `caixa_origem_id=None`, `itens=[]`, `total=valor`, `aberta_em=pendente_em=datetime.combine(data_origem, time.min)`, persiste com `create`/`commit`/`refresh` e `rollback` em exceção (mesmo padrão de `marcar_fiado`)

## Fase 3 — Adapters e infra

- [x] T011 Implementar `LancarFiadoAvulsoRequest` em `app/adapter/dtos/fiado_dto.py` — `clienteId: int`, `valor: Decimal` (`gt=0`), `dataOrigem: date`, `vencimentoEm: Optional[date]`, `observacao: Optional[str]` (`max_length=500`), mesmo padrão de alias camelCase dos DTOs já existentes no arquivo
- [x] T012 Implementar endpoint `POST /api/fiados/avulso` em `app/adapter/controllers/fiado_controller.py`, `status_code=201`, response `PendenciaDetalheResponse`, chamando `FiadoService.lancar_avulso` com os campos de `LancarFiadoAvulsoRequest`
- [x] T013 Rodar os testes de T001-T009 e confirmar que todos passam com T010-T012 implementados

## Fase 4 — Integração e aceite

> Desvio documentado (ver `plan.md` § Conformidade com a constituição): este repositório não
> tem framework BDD instalado (sem alvo `make bdd`, sem `app/tests/bdd/`). Os 7 cenários
> Gherkin de `spec.md` são cobertos um a um pelos testes de T001-T009 (ver Rastreabilidade),
> na mesma convenção `TestClient` já usada por todo o módulo — nenhum cenário fica sem teste
> equivalente.

- [x] T014 Atualizar `docs/modules/fiado.md` — endpoint `POST /api/fiados/avulso` na tabela de endpoints, exemplo de request/response, regras de negócio (sem exigir caixa, sem exigir comanda, mesma regra de vencimento) e novos códigos de validação
- [x] T015 Atualizar `docs/matrix/endpoints-by-module.md` — nova linha do endpoint na seção Fiado / Pendencias
- [x] T016 Atualizar `docs/architecture/errors.md` — novos códigos `data_origem_invalida` e `valor_devido_invalido`
- [x] T017 Atualizar `docs/postman/area-verde-collection.json` com a nova requisição, se a manutenção manual da collection continuar em dia (verificar se as demais rotas de fiado já estão na collection antes de decidir)
- [x] T018 `make validate` verde

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T001, T010, T012 |
| RF-02 | T001, T011 |
| RF-03 | T001, T010 |
| RF-04 | T004, T010 |
| RF-05 | T005, T010, T011 |
| RF-06 | T006, T007, T010 |
| RF-07 | T008 |
| RF-08 | T009 |
| RF-09 | T001, T011 |
| RF-10 | T002, T010 |
| RF-11 | T003, T010 |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-09-19

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 (avulso sem comanda) | realizado | `fiado_service.py:95-137` (`lancar_avulso` não recebe nem exige `comanda_id`); `fiado_controller.py:44-59` (`POST /api/fiados/avulso` sem parâmetro de comanda); teste `fiado_test.py:435` |
| RF-02 (exigir cliente, valor, data de origem) | realizado | `fiado_dto.py:35-42` (`LancarFiadoAvulsoRequest` com `cliente_id`, `valor`, `data_origem` obrigatórios); teste `fiado_test.py:435` |
| RF-03 (aceitar data de origem passada) | realizado | `fiado_service.py:301-307` (`_ensure_data_origem_valida` só bloqueia futuro); teste `fiado_test.py:435` (data 30 dias atrás aceita) |
| RF-04 (rejeitar data de origem futura) | realizado | `fiado_service.py:301-307` (`data_origem_invalida`); teste `fiado_test.py:503` |
| RF-05 (rejeitar valor ≤ 0) | realizado | `fiado_dto.py:37` (`Field(gt=0)`) e `fiado_service.py:294-298` (`valor_devido_invalido`, defesa dupla igual ao padrão já existente de `valor_pago`); teste `fiado_test.py:518` |
| RF-06 (cliente cadastrado e ativo) | realizado | `fiado_service.py:100-104` (`cliente_nao_encontrado`, `ClienteService.ensure_ativo`); testes `fiado_test.py:543` e `fiado_test.py:554` |
| RF-07 (aparece nas listagens existentes) | realizado | Reaproveita `Comanda`/`IComandaRepository.list_pendencias`, sem alterar `listar_pendencias`/`listar_vencidas`; teste `fiado_test.py:567` cobre `GET /api/fiados` e `GET /api/clientes/{id}/pendencias` |
| RF-08 (quitação pelo fluxo já existente) | realizado | Nenhuma alteração em `FiadoService.quitar`; teste `fiado_test.py:594` quita a pendência avulsa pelo endpoint `POST /api/fiados/{id}/quitar` já existente e confirma o caixa somado |
| RF-09 (observação opcional) | realizado | `fiado_dto.py:39` (`observacao` opcional); teste `fiado_test.py:435` |
| RF-10 (vencimento com mesma regra do fiado por comanda) | realizado | `fiado_service.py:111` (reaproveita `_resolve_vencimento` já existente); teste `fiado_test.py:461` (manual e padrão) |
| RF-11 (não exige caixa aberto) | realizado | `fiado_service.py:95-137` não chama `caixa_service`; `caixa_origem_id=None` explícito; teste `fiado_test.py:488` |

**Fora de escopo respeitado**: nenhum código de edição/exclusão de pendência avulsa, pagamento
parcial, juros, parcelamento, limite de crédito, cobrança automática ou importação em lote foi
adicionado; `itens` da pendência avulsa é sempre `[]` (nenhum vínculo com produto/consumo).

**Excesso de escopo**: nenhum. Os arquivos de documentação atualizados
(`docs/modules/fiado.md`, `docs/matrix/endpoints-by-module.md`, `docs/architecture/errors.md`,
`docs/postman/area-verde-collection.json`) não implementam requisito novo — registram o que já
foi implementado, exigido pela `documentation-policy.md` do próprio projeto.

**`make validate`** (dentro de `app/`, com `RUN_MIGRATIONS=false` — variável de ambiente real
sobrepõe o `.env` local que aponta para o host `postgres` do docker compose, mesmo valor que o
CI usa em `.github/workflows/ci.yml`): `148 passed, 3 warnings` — cobertura total **96.11%**
(mínimo exigido: 90%), `fiado_service.py` em 93%. Saída completa mostrada ao usuário nesta
sessão.

**Cenários de aceite** (`spec.md`): os 7 cenários Gherkin mapeiam 1:1 para os testes
`fiado_test.py:435,461,488,503,518,543/554,567,594` — todos passam (ver `make validate` acima).
Desvio já documentado em `plan.md`/`tasks.md`: sem framework BDD no repositório, os cenários
são exercitados via `TestClient`, convenção de 100% dos demais testes do módulo.

Veredito: convergido
Tarefas acrescentadas: nenhuma
