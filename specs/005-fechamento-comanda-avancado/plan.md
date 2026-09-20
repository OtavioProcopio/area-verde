# Plano de implementação — Fechamento avançado de comanda: pagamento parcial e acréscimo/desconto

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Representação do saldo restante e do total ajustado (RF-10, RF-13, RNF-01) | Valores **derivados em tempo de leitura**, nunca persistidos: `total_ajustado = comanda.total + Σ(ajustes, acréscimo soma/desconto subtrai)` e `saldo_restante = total_ajustado - Σ(pagamentos.valor)`, calculados por métodos estáticos novos em `AjusteComandaService` | Colunas `total_ajustado`/`saldo_restante` persistidas em `Comanda`, recalculadas a cada gravação | RNF-01 exige "0 inconsistências... nunca de um valor duplicado sujeito a divergência" — persistir duplicaria a fonte da verdade (pagamentos + ajustes já persistidos) e criaria risco de desalinhamento se um dos dois for gravado sem o outro |
| Onde vive o cálculo derivado | Métodos estáticos `AjusteComandaService.total_ajustado(comanda)` / `.saldo_restante(comanda)`, reaproveitados por `PagamentoService`, `FiadoService`, `ComandaService` e pelos DTOs de resposta | Método/`@property` em `Comanda` (`core/domain/models.py`) | Todo o restante do domínio em `models.py` é dado puro (SQLModel), sem comportamento — nenhuma entidade hoje tem método de negócio; a convenção já estabelecida do repositório (`ClienteService.ensure_ativo`, `ClienteService.nome_operacional`) é método estático em `*_service.py` reaproveitado entre serviços, que é o mesmo padrão que este plano segue |
| Registro de acréscimo/desconto (RF-09) | Nova entidade `AjusteComanda` (tabela `ajuste_comanda`: `id`, `comanda_id`, `tipo`, `valor`, `descricao`, `criado_em`), persistida via `IComandaRepository.save_ajuste` (mesmo padrão hoje usado para `ItemComanda.save_item`/`get_item_by_id`/`delete_item` dentro do próprio repositório de comanda, sem repositório dedicado) | Repositório e interface (`IAjusteComandaRepository`) dedicados, à parte | `ItemComanda` já é uma entidade filha de `Comanda` gerenciada inteiramente por `IComandaRepository`/`ComandaRepository` (ver `save_item`, `get_item_by_id`, `delete_item`); `AjusteComanda` tem a mesma relação de posse (1 comanda → N ajustes, sem ciclo de vida próprio fora da comanda) — introduzir uma camada de repositório nova para uma entidade estritamente filha duplicaria a abstração sem ganho (Simplicidade defensável) |
| Novo status de comanda (RF-03) | Novo valor `PARCIALMENTE_PAGA` em `StatusComanda`, atribuído sempre que `0 < saldo_restante < total_ajustado` após um pagamento | Reaproveitar `PENDENTE` (hoje só usado por fiado) para representar também pagamento parcial não-fiado | `PENDENTE` já tem semântica fixa e testada (fiado, aparece em `GET /api/fiados`, tem `vencimento_em`); confundir com "parcialmente paga sem fiado" quebraria as listagens de pendência existentes (`list_pendencias` filtra por `status == PENDENTE`) — RF-05 exige que só depois de **explicitamente** marcar como fiado a comanda vire `PENDENTE` |
| Transição de status ao registrar pagamento (RF-01, RF-02, RF-03, RF-04) | `PagamentoService.fechar_comanda` valida `0 < valor_pago <= saldo_restante`, persiste o `Pagamento`, então recalcula: `saldo_restante == 0` → `FECHADA` (+`fechada_em`); `saldo_restante > 0` → `PARCIALMENTE_PAGA` | Continuar exigindo `valor_pago == comanda.total` (comportamento atual) | É exatamente a lacuna do problema descrito na spec — rejeitado hoje sem alternativa |
| Bloqueio de novos itens em comanda com pagamento parcial (RF-14) | `ComandaService` passa a checar, antes do status: se `comanda.pagamentos` não está vazio **e** `comanda.status == PARCIALMENTE_PAGA`, rejeita com `comanda_nao_aceita_novos_itens` (código novo, distinto de `comanda_nao_aberta`); do contrário mantém a checagem já existente `status != ABERTA` → `comanda_nao_aberta` | Um único código de erro (`comanda_nao_aberta`) cobrindo também o caso de pagamento parcial | O critério de aceite da spec pede uma mensagem de erro **especificamente** "comanda não aceita novos itens", distinta de "comanda não está aberta" (usada para `FECHADA`/`CANCELADA`/`PENDENTE`); como o primeiro pagamento sempre tira a comanda do status `ABERTA` (vira `PARCIALMENTE_PAGA` ou `FECHADA`), os dois casos nunca colidem — uma comanda `FECHADA` por pagamento integral continua caindo em `comanda_nao_aberta`, preservando o teste de regressão já existente (`test_regressao_nao_adicionar_item_comanda_fechada`) |
| Saldo restante de pagamento parcial virando fiado (RF-05) | `FiadoService.marcar_fiado` passa a aceitar `comanda.status in {ABERTA, PARCIALMENTE_PAGA}` (em vez de só `ABERTA`); nenhuma alteração em `comanda.total` — o saldo devido do fiado continua sendo `AjusteComandaService.saldo_restante(comanda)`, que já reflete os pagamentos parciais feitos antes de virar fiado | Zerar/transferir `comanda.total` para um novo campo "valor do fiado" | `comanda.total` é o total original dos itens (fora de escopo alterar seu cálculo); o saldo devido de fiado já é 100% derivável de `total_ajustado - pagamentos`, sem precisar de campo novo — mesmo raciocínio do RNF-01 |
| Quitação parcial de fiado (RF-06) | `FiadoService.quitar` passa a validar `0 < valor_pago <= saldo_restante(comanda)` (em vez de `valor_pago == comanda.total`); após o pagamento, `saldo_restante == 0` → `FECHADA` (+`fechada_em`), senão permanece `PENDENTE` | Criar um novo método `quitar_parcial` separado de `quitar` | Mesmo método, mesma assinatura pública, só a regra de validação muda — não há caso de uso que precise dos dois convivendo com contratos diferentes; menos superfície de API é mais simples |
| Acréscimo/desconto: onde entra no fluxo (RF-07) | Novo `AjusteComandaService.aplicar_ajuste(comanda_id, tipo, valor, descricao)`, chamável a qualquer momento enquanto `comanda.status not in {FECHADA, CANCELADA}` (RF-12, RF-15 — inclui explicitamente `PENDENTE`, já que quitação de fiado também é uma forma de "fechamento" citada em RF-15) | Aceitar ajuste só em `ABERTA`/`PARCIALMENTE_PAGA`, exigindo desmarcar fiado antes | RF-15 diz "a qualquer momento até seu fechamento/quitação"; quitação é o fechamento do fluxo de fiado — excluir `PENDENTE` contrariaria a própria redação da RF |
| Validação de valor do ajuste (RF-08, RF-11) | `descricao` não pode ser vazia/whitespace (`ajuste_descricao_obrigatoria`); `valor > 0` e `total_ajustado + delta(ajuste) >= 0` (`ajuste_valor_invalido`) — cobre tanto "sem descrição" quanto "desconto maior que o total" com códigos de erro dedicados e coerentes com o padrão `code`/`message`/`status_code` de `ApplicationError` já usado em todo o domínio | Reaproveitar `dados_invalidos` genérico | Os cenários de aceite da spec descrevem dois erros semanticamente distintos ("erro de descrição obrigatória" vs. "erro de valor de ajuste inválido"); códigos únicos por causa raiz já são o padrão de todo o domínio (`comanda_sem_consumo`, `valor_pago_invalido`, etc.) |
| Saldo credor (RF-16) | Nenhuma trava adicional: `saldo_restante` pode retornar negativo; a resposta da API expõe o valor como está (`Decimal` negativo), sem processamento automático | Zerar/clampar saldo em 0 quando negativo | RF-16 explicitamente exige refletir o saldo credor, não escondê-lo; tratamento (troco/abatimento/estorno) é fora de escopo |
| Exposição do saldo/total ajustado na API (RF-13) | Novos campos `totalAjustado` e `saldoRestante` em `ComandaResumoResponse`, `ComandaDetalheResponse`, `FecharComandaResponse`, `PendenciaResumoResponse`/`PendenciaDetalheResponse` e `QuitarFiadoResponse`; novo `AjusteComandaResponse` (lista) em `ComandaDetalheResponse`/`PendenciaDetalheResponse` para a auditoria pedida em RF-09 | Endpoint dedicado só para saldo/ajustes | A spec já entrega o total/saldo "ao consultar uma comanda" (RF-13) — os DTOs de consulta já existentes são o ponto certo; um endpoint novo só para isso duplicaria consulta sem necessidade |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| — | — | — | — |

Nenhum padrão GoF novo entra nesta feature: os novos métodos seguem o mesmo formato de método
de serviço com `try/except` + `commit`/`rollback` já usado em `ComandaService`, `PagamentoService`
e `FiadoService`.

**Considerado e recusado — State**: modelar `StatusComanda` (`ABERTA` → `PARCIALMENTE_PAGA` →
`FECHADA`, com desvio para `PENDENTE`) como uma máquina de estados com uma classe por estado foi
considerado, porque agora há uma transição condicional a mais. Recusado porque as transições
continuam sendo 2–3 `if`s lineares dentro de um único método (`fechar_comanda`/`quitar`), sem
comportamento que varie por estado além do próprio valor do enum — introduzir uma hierarquia de
classes para isso violaria Simplicidade defensável (KISS) sem resolver um problema presente.

**Considerado e recusado — Strategy**: uma estratégia por `TipoAjusteComanda` (`ACRESCIMO` vs.
`DESCONTO`) para calcular o delta do ajuste foi considerada. Recusado porque a variação inteira
é `+valor` ou `-valor` — um único `if`/`match` de duas branches dentro de
`AjusteComandaService.total_ajustado` é mais simples e igualmente testável; Strategy só se paga
quando o número de variantes cresce ou a lógica por variante é substancial, nenhum dos dois é o
caso aqui.

## Arquivos a criar ou alterar

> Nota sobre caminhos (mesmo desvio documentado nos planos anteriores desta feature —
> `specs/001-fiado-avulso-retroativo/plan.md` e `specs/003-reorganizar-testes-backend/plan.md`):
> interfaces vivem em `app/core/interfaces/<mesmo caminho de adapters/infra>` (não em
> `app/interfaces/`), e os testes de `core/application/use_cases` são arquivos únicos por módulo
> de negócio em `app/tests/core/application/use_cases/<modulo>_test.py`, usando
> `fastapi.testclient.TestClient` contra sqlite em memória (`app/conftest.py`), sem mock de
> repositório — convenção real de 100% da suíte atual, fixada por `specs/003-...`. Esta feature
> segue a mesma convenção; `app/tests/bdd/` (citado no `spec.md`) é uma árvore nova, mas usa a
> mesma ferramenta (pytest + `TestClient`), sem introduzir framework BDD novo — ver "Dependências
> externas" e "Riscos".

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| core/domain | `app/core/domain/enums/status_comanda.py` | alterar — novo valor `PARCIALMENTE_PAGA` | `app/tests/core/application/use_cases/pagamentos_test.py` |
| core/domain | `app/core/domain/enums/tipo_ajuste_comanda.py` | criar — `TipoAjusteComanda.ACRESCIMO` / `.DESCONTO` | `app/tests/core/application/use_cases/comandas_test.py` |
| core/domain | `app/core/domain/enums/__init__.py` | alterar — exporta `TipoAjusteComanda` | — (reexport) |
| core/domain | `app/core/domain/models.py` | alterar — nova entidade `AjusteComanda` (tabela `ajuste_comanda`) e `Comanda.ajustes: List["AjusteComanda"]` | `app/tests/bootstrap_test.py` (estender, mesmo padrão usado para índices/tabelas novas em `specs/002-produto-nome-duplicado/plan.md`) |
| core/interfaces | `app/core/interfaces/adapters/repositories/i_comanda_repository.py` | alterar — novo método de protocolo `save_ajuste(ajuste: AjusteComanda) -> AjusteComanda` | — (protocolo, sem lógica) |
| adapters/repositories | `app/adapter/repositories/comanda_repository.py` | alterar — implementa `save_ajuste` (mesmo padrão de `save_item`) | `app/tests/core/application/use_cases/comandas_test.py` |
| core/application | `app/core/application/use_cases/ajuste_comanda_service.py` | criar — `AjusteComandaService` com `total_ajustado`, `saldo_restante` (estáticos) e `aplicar_ajuste`, `listar_ajustes` | `app/tests/core/application/use_cases/comandas_test.py` |
| core/application | `app/core/application/use_cases/pagamento_service.py` | alterar — `fechar_comanda` valida contra `saldo_restante`, permite `valor_pago < saldo`, define `PARCIALMENTE_PAGA`/`FECHADA` | `app/tests/core/application/use_cases/pagamentos_test.py` |
| core/application | `app/core/application/use_cases/fiado_service.py` | alterar — `marcar_fiado` aceita `PARCIALMENTE_PAGA`; `quitar` valida contra `saldo_restante` e permite quitação parcial mantendo `PENDENTE` | `app/tests/core/application/use_cases/fiado_test.py` |
| core/application | `app/core/application/use_cases/comanda_service.py` | alterar — `_ensure_aceita_itens` (novo) substitui a checagem de status usada por `adicionar_item`, `incrementar_item`, `diminuir_item`, `remover_item` | `app/tests/core/application/use_cases/comandas_test.py` |
| adapters/dtos | `app/adapter/dtos/comanda_dto.py` | alterar — novo `AjusteComandaResponse`, `AplicarAjusteComandaRequest`; `totalAjustado`/`saldoRestante`/`ajustes` em `ComandaResumoResponse`/`ComandaDetalheResponse` | `app/tests/core/application/use_cases/comandas_test.py` |
| adapters/dtos | `app/adapter/dtos/pagamento_dto.py` | alterar — `totalAjustado`/`saldoRestante` em `FecharComandaResponse` | `app/tests/core/application/use_cases/pagamentos_test.py` |
| adapters/dtos | `app/adapter/dtos/fiado_dto.py` | alterar — `totalAjustado`/`saldoRestante` em `PendenciaResumoResponse`/`PendenciaDetalheResponse`/`QuitarFiadoResponse` | `app/tests/core/application/use_cases/fiado_test.py` |
| adapters/controllers | `app/adapter/controllers/comanda_controller.py` | alterar — `POST /api/comandas/{comanda_id}/ajustes` e `GET /api/comandas/{comanda_id}/ajustes` | `app/tests/core/application/use_cases/comandas_test.py` |
| adapters/controllers | `app/adapter/controllers/dependencies.py` | alterar — `build_ajuste_comanda_service` | — (fábrica, sem lógica própria) |
| testes | `app/tests/bdd/fechamento_comanda_avancado_test.py` | criar — um `test_` por cenário Gherkin do `spec.md`, docstring com o texto DADO/QUANDO/ENTÃO/MAS **sem tradução**, corpo via `TestClient` | é o próprio teste |
| migrations | `app/migrations/versions/<nova>_ajuste_comanda_status_parcial.py` | criar — tabela `ajuste_comanda` + amplia o enum de `status` em `comanda` para incluir `PARCIALMENTE_PAGA` | `app/tests/bootstrap_test.py` (estender) |
| docs | `docs/modules/comandas.md`, `docs/modules/pagamentos.md`, `docs/modules/fiado.md` | alterar — novo status, novos endpoints, novos campos de resposta, novos códigos de erro | — |
| docs | `docs/matrix/endpoints-by-module.md` | alterar — 2 linhas novas (`POST`/`GET` `/api/comandas/{id}/ajustes`) | — |
| docs | `docs/architecture/errors.md` | alterar — novos códigos `comanda_nao_aceita_novos_itens`, `ajuste_descricao_obrigatoria`, `ajuste_valor_invalido` | — |
| docs | `docs/architecture/database.md` | alterar — nova entidade `AjusteComanda`, nova revisão na tabela "Migrations atuais do MVP" | — |
| docs | `docs/postman/area-verde-collection.json` | alterar — novas requisições, se a manutenção manual continuar em dia | — |

Nenhum arquivo em `infra/` é tocado: não há variável de ambiente, serviço de compose ou
dependência de infraestrutura nova.

## Contrato entre camadas

**Pagamento parcial** (`PagamentoService.fechar_comanda`, chamado por
`POST /api/comandas/{id}/fechar`, DTO inalterado):
1. Busca a comanda (`comanda_nao_encontrada` se ausente); rejeita `FIADO` como forma (já existe).
2. Aceita `status in {ABERTA, PARCIALMENTE_PAGA}` (novo — hoje só `ABERTA`); caso contrário
   `comanda_nao_aberta`.
3. Calcula `saldo = AjusteComandaService.saldo_restante(comanda)`; rejeita `valor_pago <= 0` ou
   `valor_pago > saldo` com `valor_pago_invalido` (mesmo código já existente, nova condição).
4. Cria o `Pagamento` e aplica no caixa (inalterado).
5. Recalcula `saldo` após o pagamento: `== 0` → `status = FECHADA`, `fechada_em = now`;
   `> 0` → `status = PARCIALMENTE_PAGA`.
6. Persiste, `commit`, `refresh`, retorna `FechamentoComandaResult` (inalterado no formato).

**Fiado parcial** (`FiadoService.marcar_fiado`/`quitar`, `POST /api/comandas/{id}/fiado` e
`POST /api/fiados/{id}/quitar`, DTOs inalterados):
- `marcar_fiado`: mesma lógica atual, só troca `_ensure_aberta` por uma checagem que aceita
  `ABERTA` ou `PARCIALMENTE_PAGA`. O valor devido do fiado nunca é copiado para um campo novo —
  continua sendo `saldo_restante(comanda)` na leitura.
- `quitar`: troca `valor_pago != comanda.total` por `valor_pago <= 0 or valor_pago >
  saldo_restante(comanda)` (mesmo código `valor_pago_invalido`); após o pagamento, `saldo == 0`
  → `FECHADA` + `fechada_em`; `saldo > 0` → mantém `PENDENTE`.

**Acréscimo/desconto** (`AjusteComandaService.aplicar_ajuste`, novo
`POST /api/comandas/{id}/ajustes`):
1. Busca a comanda (`comanda_nao_encontrada`); rejeita `status in {FECHADA, CANCELADA}` com
   `comanda_nao_aberta`.
2. Rejeita `descricao` vazia/whitespace com `ajuste_descricao_obrigatoria`.
3. Rejeita `valor <= 0` com `ajuste_valor_invalido`.
4. Calcula `delta = valor if tipo == ACRESCIMO else -valor`; rejeita
   `total_ajustado(comanda) + delta < 0` com `ajuste_valor_invalido` (RF-11).
5. Persiste `AjusteComanda(comanda_id, tipo, valor, descricao)` via
   `comanda_repository.save_ajuste`; **não** altera `comanda.status` nem `comanda.total` — o
   `total_ajustado`/`saldo_restante` mudam só porque agora há um ajuste a mais na relação
   `comanda.ajustes`, lidos na próxima consulta (RF-13, RF-15, RF-16).
6. `commit`, `refresh`, retorna a comanda atualizada.

**Bloqueio de item em comanda com pagamento** (`ComandaService._ensure_aceita_itens`, chamado no
início de `adicionar_item`/`incrementar_item`/`diminuir_item`/`remover_item` em vez da checagem
antiga):
1. `status == PARCIALMENTE_PAGA` → `comanda_nao_aceita_novos_itens`.
2. `status != ABERTA` (após o passo 1, cobre `FECHADA`/`CANCELADA`/`PENDENTE`) →
   `comanda_nao_aberta`.

Erros continuam sempre `ApplicationError`/`NotFoundError`, tratados pelo handler global já
existente — nenhum tratamento novo de exceção.

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| — | — | Nenhuma dependência nova. `app/tests/bdd/` reaproveita `pytest` + `fastapi.testclient.TestClient`, já usados em toda a suíte — nenhum framework BDD (`pytest-bdd`, `behave`) é adicionado, porque o repositório não usa `.feature`/Gherkin parametrizado hoje e introduzir um agora seria antecipação de ferramenta sem um segundo caso de uso que a justifique (Simplicidade defensável) | Banco sqlite em memória via `app/conftest.py` (convenção já existente) |

## Impacto no contrato de operação

Nenhum alvo de `Makefile` novo. `make test` (`pytest . -v -m "not integration"`) já descobre
qualquer `*_test.py` novo sob `app/`, incluindo `app/tests/bdd/fechamento_comanda_avancado_test.py`
— mesma constatação já documentada em `specs/003-reorganizar-testes-backend/plan.md` sobre
`testpaths = .`. O alvo `make bdd` citado na constituição não existe neste repositório (mesmo
desvio já registrado em memória de projeto/`specs/001-.../plan.md` para os demais alvos
divergentes) — os cenários BDD desta feature rodam dentro de `make test`/`make validate`, como
qualquer outro teste da suíte.

Migração de banco **é necessária**: nova tabela `ajuste_comanda` e ampliação do enum de
`status` em `comanda` para incluir `PARCIALMENTE_PAGA`. Comando (dentro de `app/`, conforme
`docs/architecture/database.md`):

```bash
alembic revision -m "ajuste_comanda_status_parcial"
```

seguido de edição manual do arquivo gerado com `upgrade`/`downgrade` explícitos
(`op.create_table("ajuste_comanda", ...)`, índices em `comanda_id` e `criado_em`, e — como
`StatusComanda` é mapeado com `SAEnum(..., native_enum=False, length=20)`, ou seja, uma coluna
`String` com `CheckConstraint` implícito do SQLAlchemy só em nível de aplicação, não de enum
nativo do Postgres — nenhuma migração de tipo `ALTER TYPE` é necessária; o novo valor
`PARCIALMENTE_PAGA` já cabe no `length=20` existente e não exige alteração de schema além da
tabela nova). Aplicação via `make migrate` (alvo já existente, roda `alembic upgrade head` no
serviço `api`), sem alvo novo.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Algum consumidor (frontend) tratar `PARCIALMENTE_PAGA` como valor desconhecido e quebrar a UI de listagem de comandas | Média | RF-13 já expõe `saldoRestante`/`totalAjustado` explicitamente para o frontend decidir a UI; o desbloqueio do placeholder em `useComandasState.ts`/`Comandas.tsx` está dentro do escopo da spec — validar com o time de frontend antes do merge |
| `_ensure_aceita_itens` divergir do teste de regressão existente (`test_regressao_nao_adicionar_item_comanda_fechada`) por causa da mudança de ordem das checagens | Baixa (já verificado por leitura: pagamento integral vai direto `ABERTA → FECHADA`, nunca passa por `PARCIALMENTE_PAGA`) | Rodar a suíte completa (`make test`) logo após a alteração de `comanda_service.py`, antes de prosseguir para os novos testes |
| Ajuste aplicado concorrentemente a um pagamento na mesma comanda (dois requests quase simultâneos) gerar saldo inconsistente | Baixa (MVP de operador único por balcão, sem fila de concorrência hoje em nenhum outro fluxo do sistema) | Mesmo nível de proteção que o restante do domínio: transação por request via `Session`/`commit`/`rollback`; tratamento de concorrência otimista fica fora de escopo desta feature, como em todos os outros serviços atuais |
| Migração de enum de status esbarrar em algum valor de coluna `status` do tipo nativo do Postgres (`CREATE TYPE`) em vez de `String` | Baixa (confirmado em `models.py`: `SAEnum(StatusComanda, native_enum=False, length=20)`) | Conferir `alembic upgrade head` localmente contra o schema atual antes de abrir a PR, como pede a Migration Policy |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Nenhum alvo de `Makefile` novo; testes e migração rodam pelos alvos já existentes (`make test`, `make validate`, `make migrate`). **Desvio documentado**: `make bdd` citado na constituição não existe no repositório real — os cenários Gherkin desta feature entram em `app/tests/bdd/` mas rodam via `make test`/`pytest`, mesma constatação de `specs/001-.../plan.md` |
| Arquitetura limpa | `core/application` (`AjusteComandaService`, `PagamentoService`, `FiadoService`, `ComandaService`) não importa `adapters` nem `infra`; `adapters/controllers` e `adapters/dtos` são os únicos pontos que conhecem os novos casos de uso. **Desvio documentado**: interfaces vivem em `app/core/interfaces/adapters/...`, não em `app/interfaces/` da raiz — convenção pré-existente, mantida por consistência (ver nota em "Arquivos a criar ou alterar") |
| Testes provam a entrega | Todo RF-01 a RF-16 tem pelo menos um teste em `app/tests/core/application/use_cases/{pagamentos,fiado,comandas}_test.py` e um cenário espelhado em `app/tests/bdd/fechamento_comanda_avancado_test.py`; cobertura mínima 90% nos arquivos alterados (`ajuste_comanda_service.py`, `pagamento_service.py`, `fiado_service.py`, `comanda_service.py`). **Desvio documentado**: os testes exercitam a API via `TestClient` contra sqlite em memória, não mock por dependência injetada — mesma convenção de 100% da suíte atual, fixada por `specs/003-reorganizar-testes-backend/plan.md` |
| Simplicidade defensável | Nenhum padrão GoF novo (State e Strategy considerados e recusados, ver seção acima); saldo/total derivados em vez de persistidos evita duplicar fonte de verdade (RNF-01); `AjusteComanda` reaproveita o mesmo modelo de posse de `ItemComanda` dentro de `IComandaRepository`, sem repositório novo |
| Autoria | Nenhum commit, PR, migration ou documentação gerada por este plano atribui autoria a ferramenta de IA |
| Idioma | `spec.md`, este `plan.md`, mensagens de erro e documentação em português; identificadores de código em português técnico consistente com o domínio já existente (`aplicar_ajuste`, `saldo_restante`, seguindo `marcar_fiado`, `quitar`, `adicionar_item`); cenários BDD em `app/tests/bdd/` reproduzem DADO/QUANDO/ENTÃO/MAS do `spec.md` sem tradução |
| Migrations Alembic (específico do projeto) | Migration nova e obrigatória (`ajuste_comanda_status_parcial`): cria a tabela `ajuste_comanda` e nada mais — não remove nem altera coluna/índice de nenhum outro módulo; `upgrade`/`downgrade` coerentes; aplicada via `alembic revision` (`docs/architecture/database.md`) + `make migrate`, sem editar migration já mergeada |
