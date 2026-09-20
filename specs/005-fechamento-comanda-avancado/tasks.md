# Tarefas — Fechamento avançado de comanda: pagamento parcial e acréscimo/desconto

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.

## Fase 1 — Domínio

- [x] T001 [P] Teste de `app/core/domain/enums/status_comanda.py` estendendo `app/tests/core/application/use_cases/pagamentos_test.py` para cobrir o novo valor `PARCIALMENTE_PAGA`
- [x] T002 Adicionar `PARCIALMENTE_PAGA` em `app/core/domain/enums/status_comanda.py`
- [x] T003 [P] Teste de `app/core/domain/enums/tipo_ajuste_comanda.py` estendendo `app/tests/core/application/use_cases/comandas_test.py` para cobrir `ACRESCIMO`/`DESCONTO`
- [x] T004 Criar `app/core/domain/enums/tipo_ajuste_comanda.py` com `TipoAjusteComanda.ACRESCIMO`/`.DESCONTO`
- [x] T005 Atualizar `app/core/domain/enums/__init__.py` para reexportar `TipoAjusteComanda`
- [x] T006 [P] Teste de `app/core/domain/models.py` estendendo `app/tests/bootstrap_test.py` para cobrir a nova tabela `ajuste_comanda` e a relação `Comanda.ajustes`
- [x] T007 Adicionar entidade `AjusteComanda` (tabela `ajuste_comanda`: `id`, `comanda_id`, `tipo`, `valor`, `descricao`, `criado_em`) e `Comanda.ajustes: List["AjusteComanda"]` em `app/core/domain/models.py`
- [x] T008 Criar migração Alembic `app/migrations/versions/<nova>_ajuste_comanda_status_parcial.py` (`op.create_table("ajuste_comanda", ...)` com índices em `comanda_id` e `criado_em`; nenhuma alteração de tipo de coluna é necessária para `PARCIALMENTE_PAGA`, já que `status` é `String(20)`)

## Fase 2 — Aplicação

- [x] T009 Teste de `IComandaRepository.save_ajuste` em `app/tests/core/application/use_cases/comandas_test.py`
- [x] T010 Adicionar método de protocolo `save_ajuste(ajuste: AjusteComanda) -> AjusteComanda` em `app/core/interfaces/adapters/repositories/i_comanda_repository.py`
- [x] T011 Teste de `AjusteComandaService.total_ajustado`/`.saldo_restante`/`.aplicar_ajuste`/`.listar_ajustes` em `app/tests/core/application/use_cases/comandas_test.py` — cobrindo: acréscimo soma, desconto subtrai, múltiplos ajustes acumulam, desconto sem descrição rejeitado (`ajuste_descricao_obrigatoria`), desconto maior que o total rejeitado (`ajuste_valor_invalido`), ajuste em comanda `FECHADA`/`CANCELADA` rejeitado (`comanda_nao_aberta`), ajuste com pagamento parcial já registrado recalcula saldo, ajuste que gera saldo credor (negativo) é aceito
- [x] T012 Criar `app/core/application/use_cases/ajuste_comanda_service.py` com `AjusteComandaService` (`total_ajustado`, `saldo_restante` estáticos; `aplicar_ajuste`, `listar_ajustes`)
- [x] T013 [P] Teste de `PagamentoService.fechar_comanda` em `app/tests/core/application/use_cases/pagamentos_test.py` — cobrindo: pagamento parcial deixa `PARCIALMENTE_PAGA` com saldo correto, segundo pagamento completa e fecha, pagamento que ultrapassa saldo restante é rejeitado (`valor_pago_invalido`), pagamento respeita total ajustado por desconto já aplicado
- [x] T014 Alterar `app/core/application/use_cases/pagamento_service.py` (`fechar_comanda`): aceitar `status in {ABERTA, PARCIALMENTE_PAGA}`, validar `0 < valor_pago <= saldo_restante`, definir `PARCIALMENTE_PAGA` ou `FECHADA` conforme o saldo após o pagamento
- [x] T015 [P] Teste de `FiadoService.marcar_fiado`/`.quitar` em `app/tests/core/application/use_cases/fiado_test.py` — cobrindo: marcar como fiado o saldo restante de uma comanda `PARCIALMENTE_PAGA`, quitação parcial mantém `PENDENTE` com saldo recalculado, quitação total fecha e sai da listagem de pendências em aberto
- [x] T016 Alterar `app/core/application/use_cases/fiado_service.py`: `marcar_fiado` aceita `status in {ABERTA, PARCIALMENTE_PAGA}`; `quitar` valida `0 < valor_pago <= saldo_restante(comanda)` e mantém `PENDENTE` ou fecha conforme o saldo
- [x] T017 Teste de `ComandaService._ensure_aceita_itens` em `app/tests/core/application/use_cases/comandas_test.py` — cobrindo: item novo em comanda `PARCIALMENTE_PAGA` rejeitado (`comanda_nao_aceita_novos_itens`), item novo em comanda `FECHADA` continua rejeitado (`comanda_nao_aberta`, regressão de `test_regressao_nao_adicionar_item_comanda_fechada`)
- [x] T018 Alterar `app/core/application/use_cases/comanda_service.py`: introduzir `_ensure_aceita_itens`, usado por `adicionar_item`, `incrementar_item`, `diminuir_item`, `remover_item` no lugar da checagem de status antiga

> Nota: T009, T011 e T017 editam todos `comandas_test.py` — nenhum é `[P]` entre si (mesmo arquivo). T013 e T015 tocam arquivos de teste distintos (`pagamentos_test.py`, `fiado_test.py`) e não colidem com `comandas_test.py`, por isso ficam `[P]` entre si.

## Fase 3 — Adapters e infra

- [x] T019 Teste de `ComandaRepository.save_ajuste` em `app/tests/core/application/use_cases/comandas_test.py` (`test_comanda_repository_save_ajuste_persiste_ajuste`, antecipado na Fase 2 — a Fase 2 precisava de `save_ajuste` real, sem mock, para testar `AjusteComandaService` ponta a ponta)
- [x] T020 Implementar `save_ajuste` em `app/adapter/repositories/comanda_repository.py` (antecipado na Fase 2, mesmo motivo acima)
- [x] T021 Teste de `AjusteComandaResponse`/`AplicarAjusteComandaRequest` e dos novos campos `totalAjustado`/`saldoRestante`/`ajustes` em `ComandaResumoResponse`/`ComandaDetalheResponse`, em `app/tests/core/application/use_cases/comandas_test.py`
- [x] T022 Adicionar `AjusteComandaResponse`, `AplicarAjusteComandaRequest` e os campos `totalAjustado`/`saldoRestante`/`ajustes` em `app/adapter/dtos/comanda_dto.py`
- [x] T023 [P] Teste dos novos campos `totalAjustado`/`saldoRestante` em `FecharComandaResponse`, em `app/tests/core/application/use_cases/pagamentos_test.py`
- [x] T024 Adicionar `totalAjustado`/`saldoRestante` em `FecharComandaResponse` em `app/adapter/dtos/pagamento_dto.py`
- [x] T025 [P] Teste dos novos campos `totalAjustado`/`saldoRestante` em `PendenciaResumoResponse`/`PendenciaDetalheResponse`/`QuitarFiadoResponse`, em `app/tests/core/application/use_cases/fiado_test.py`
- [x] T026 Adicionar `totalAjustado`/`saldoRestante` em `PendenciaResumoResponse`/`PendenciaDetalheResponse`/`QuitarFiadoResponse` em `app/adapter/dtos/fiado_dto.py`
- [x] T027 Teste de `POST`/`GET /api/comandas/{comanda_id}/ajustes` em `app/tests/core/application/use_cases/comandas_test.py`
- [x] T028 Adicionar `POST`/`GET /api/comandas/{comanda_id}/ajustes` em `app/adapter/controllers/comanda_controller.py`
- [x] T029 Adicionar fábrica `build_ajuste_comanda_service` em `app/adapter/controllers/dependencies.py`

> Nota: T019, T021 e T027 editam todos `comandas_test.py` — nenhum é `[P]`. T023 (`pagamentos_test.py`) e T025 (`fiado_test.py`) tocam arquivos distintos entre si e do grupo acima, por isso ficam `[P]`.

## Fase 4 — Integração e BDD

Todos os cenários abaixo vivem no mesmo arquivo novo (`app/tests/bdd/fechamento_comanda_avancado_test.py`),
por isso nenhum é `[P]` entre si (mesma colisão de arquivo). Cada um reproduz, em `# language: pt`,
o texto DADO/QUANDO/ENTÃO/MAS do `spec.md`, sem tradução.

- [x] T030 Cenário "Pagamento parcial de comanda aberta com saldo restante rastreado"
- [x] T031 Cenário "Múltiplos pagamentos até completar o total"
- [x] T032 Cenário "Pagamento que ultrapassa o saldo restante é rejeitado"
- [x] T033 Cenário "Saldo restante de pagamento parcial vira fiado"
- [x] T034 Cenário "Quitação parcial de pendência de fiado"
- [x] T035 Cenário "Quitação total de pendência de fiado encerra a pendência"
- [x] T036 Cenário "Aplicar desconto com descrição ao fechamento"
- [x] T037 Cenário "Aplicar acréscimo com descrição ao fechamento"
- [x] T038 Cenário "Acréscimo ou desconto sem descrição é rejeitado"
- [x] T039 Cenário "Desconto maior que o total é rejeitado"
- [x] T040 Cenário "Acréscimo/desconto não pode ser aplicado a comanda já fechada"
- [x] T041 Cenário "Pagamento respeita total ajustado por desconto"
- [x] T042 Cenário "Comanda com pagamento parcial não aceita novos itens"
- [x] T043 Cenário "Múltiplos acréscimos/descontos se acumulam no total ajustado"
- [x] T044 Cenário "Desconto após pagamento parcial recalcula o saldo restante"
- [x] T045 Cenário "Desconto após pagamento gera saldo credor"
- [x] T046 Atualizar `docs/modules/comandas.md`, `docs/modules/pagamentos.md`, `docs/modules/fiado.md` (novo status, endpoints, campos de resposta, códigos de erro)
- [x] T047 Atualizar `docs/matrix/endpoints-by-module.md` (`POST`/`GET /api/comandas/{id}/ajustes`)
- [x] T048 Atualizar `docs/architecture/errors.md` (`comanda_nao_aceita_novos_itens`, `ajuste_descricao_obrigatoria`, `ajuste_valor_invalido`)
- [x] T049 Atualizar `docs/architecture/database.md` (entidade `AjusteComanda`, nova revisão na tabela de migrations do MVP)
- [x] T050 `make validate` verde

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T013, T014, T030 |
| RF-02 | T013, T014, T031 |
| RF-03 | T002, T014, T016, T030, T031, T033, T035 |
| RF-04 | T013, T014, T032 |
| RF-05 | T015, T016, T033 |
| RF-06 | T015, T016, T034, T035 |
| RF-07 | T011, T012, T036, T037 |
| RF-08 | T011, T012, T038 |
| RF-09 | T006, T007, T009, T010, T019, T020, T036, T037, T043 |
| RF-10 | T011, T012, T041 |
| RF-11 | T011, T012, T039 |
| RF-12 | T011, T012, T040 |
| RF-13 | T021, T022, T023, T024, T025, T026 |
| RF-14 | T017, T018, T042 |
| RF-15 | T011, T012, T044 |
| RF-16 | T011, T012, T045 |
| RNF-01 | T011, T012 (cálculo sempre derivado, nunca duplicado) |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-09-20

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 | realizado | `app/core/application/use_cases/pagamento_service.py:63-68` (`saldo = AjusteComandaService.saldo_restante(comanda)`, aceita `valor_pago < saldo`) |
| RF-02 | realizado | `pagamento_service.py:97-101` (recalcula saldo após cada pagamento; múltiplas chamadas acumulam via `comanda.pagamentos`) |
| RF-03 | realizado | `pagamento_service.py:98-101` e `fiado_service.py:216-221` (`PARCIALMENTE_PAGA`/`FECHADA` conforme saldo) |
| RF-04 | realizado | `pagamento_service.py:64-69` (`valor_pago <= 0 or valor_pago > saldo` → `valor_pago_invalido`) |
| RF-05 | realizado | `fiado_service.py:276-279` (`marcar_fiado` aceita `ABERTA` ou `PARCIALMENTE_PAGA`) |
| RF-06 | realizado | `fiado_service.py:183-184,216-221` (`quitar` valida contra `saldo_restante`, mantém `PENDENTE` ou fecha) |
| RF-07 | realizado | `ajuste_comanda_service.py:37-69` (`aplicar_ajuste`, tipo acréscimo/desconto + descrição) |
| RF-08 | realizado | `ajuste_comanda_service.py:86-92` (`_ensure_descricao_valida` → `ajuste_descricao_obrigatoria`) |
| RF-09 | realizado | `core/domain/models.py` (entidade `AjusteComanda`) + `comanda_repository.py` (`save_ajuste`) + `comanda_dto.py` (`AjusteComandaResponse`, exposto em `GET /api/comandas/{id}/ajustes`) |
| RF-10 | realizado | `ajuste_comanda_service.py:18-29` (`total_ajustado` usado em `saldo_restante` e nas validações de pagamento/quitação) |
| RF-11 | realizado | `ajuste_comanda_service.py:99-102` (`total_ajustado(comanda) + delta < 0` → `ajuste_valor_invalido`) |
| RF-12 | realizado | `ajuste_comanda_service.py:81-83` (`_ensure_pode_ajustar`, bloqueia `FECHADA`/`CANCELADA`) |
| RF-13 | realizado | `comanda_dto.py` (`totalAjustado`/`saldoRestante`/`ajustes` em `ComandaResumoResponse`/`ComandaDetalheResponse`), `pagamento_dto.py` (`FecharComandaResponse`), `fiado_dto.py` (`PendenciaResumoResponse`/`PendenciaDetalheResponse`/`QuitarFiadoResponse`) |
| RF-14 | realizado | `comanda_service.py:457-467` (`_ensure_aceita_itens` → `comanda_nao_aceita_novos_itens` quando `PARCIALMENTE_PAGA`) |
| RF-15 | realizado | `ajuste_comanda_service.py:81-83` (`_ensure_pode_ajustar` só bloqueia `FECHADA`/`CANCELADA`, permite `ABERTA`/`PARCIALMENTE_PAGA`/`PENDENTE`) |
| RF-16 | realizado | `ajuste_comanda_service.py:31-35` (`saldo_restante` não trava em zero, pode retornar negativo) |
| RNF-01 | realizado | `total_ajustado`/`saldo_restante` são funções puras sobre `comanda.ajustes`/`comanda.pagamentos` persistidos, nenhum campo duplicado adicionado a `Comanda` |

`make validate` (dentro de `app/`, `RUN_MIGRATIONS=false`): **verde** — `200 passed, 4 warnings in 60.18s`, cobertura total 96.25% (mínimo 90%). Confirmado por execução direta nesta rodada de convergência, não só por relato das fases anteriores.

Cenários BDD: os 16 critérios de aceite do `spec.md` têm cenário correspondente em `app/tests/bdd/fechamento_comanda_avancado_test.py` (T030–T045), todos incluídos nos 200 testes verdes acima.

Excesso de escopo: nenhum encontrado. Verificado especificamente contra a seção "Fora de escopo" da spec — nenhum estorno/cancelamento de pagamento foi implementado, nenhuma edição/remoção de ajuste após o fechamento, nenhum relatório de auditoria dedicado, nenhum suporte a percentual (só valor fixo, conforme esclarecimento), nenhuma divisão de um único pagamento entre formas de pagamento simultâneas.

Veredito: convergido
Tarefas acrescentadas: nenhuma
