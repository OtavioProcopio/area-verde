# Plano de implementação — Fiado avulso retroativo

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Representação da pendência avulsa | Reaproveitar a entidade `Comanda` existente, criada diretamente em status `PENDENTE`, sem `itens`, com `total` atribuído a partir do valor informado | Criar uma entidade nova (`FiadoAvulso`) paralela à `Comanda` | RF-07 e RF-08 exigem que a pendência avulsa apareça nas mesmas listagens (`GET /api/fiados`, `GET /api/fiados/vencidos`, `GET /api/clientes/{id}/pendencias`) e use o mesmo fluxo de quitação e de relatórios. Todos esses fluxos já consultam `Comanda` via `IComandaRepository.list_pendencias`; reaproveitar a entidade entrega os RFs sem tocar em nenhum desses outros pontos (listagem, relatórios, quitação), o que uma entidade nova exigiria duplicar ou unificar em cada consulta — contra Simplicidade defensável (YAGNI/KISS) |
| Campo que guarda a data de origem da dívida | `Comanda.pendente_em`, informado manualmente (aceita data passada) em vez de sempre `datetime.now()` | Criar campo novo `data_origem` | É exatamente o campo que a issue #38 aponta como o problema (`comanda.pendente_em = datetime.now()` sempre "agora"); `pendente_em` já significa "quando a comanda virou pendente", que é a mesma semântica de "quando a dívida começou" para o lançamento avulso. Também usado como `aberta_em`, para manter a ordenação e os filtros por data (`data_inicio`/`data_fim`) coerentes com a origem histórica, e não com o instante do lançamento no sistema |
| Exigência de caixa aberto | Não verificar caixa aberto no novo caso de uso (`caixa_origem_id` fica `None`) | Exigir caixa aberto, como em `marcar_fiado` | Decidido em `/bu:clarify` (RF-11): o lançamento avulso é só registro histórico, não movimenta caixa nem dinheiro |
| Endpoint novo | `POST /api/fiados/avulso`, no mesmo `fiado_controller.py` e mesmo router dos demais endpoints de fiado | `POST /api/clientes/{cliente_id}/fiados-avulsos` no `cliente_controller.py` | Mantém todo o ciclo de vida do fiado (marcar, listar, consultar, quitar, avulso) em um único controller e módulo, espelhando `docs/modules/fiado.md`; o cliente é só um dos dados do corpo da requisição, igual já ocorre em `MarcarFiadoRequest.clienteId` |
| Validação de valor e data de origem | Validações dedicadas em `FiadoService` (`data_origem_invalida`, `valor_devido_invalido`), reaproveitando `_resolve_vencimento` e `ClienteService.ensure_ativo` já existentes | Reaproveitar `_ensure_com_consumo` | `_ensure_com_consumo` exige itens e depende de `comanda.itens`, que a pendência avulsa não tem (Fora de escopo da spec: "vincular a itens de produto/consumo") |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| — | — | — | — |

Nenhum padrão GoF novo entra aqui: o caso de uso é um método a mais em `FiadoService`, seguindo
o mesmo formato dos métodos já existentes (`marcar_fiado`, `quitar`) — introduzir Strategy,
Factory ou similar para uma única forma de criação não resolve problema presente e viola
Simplicidade defensável (Princípio 4).

**Considerado e recusado**: Factory Method para a criação da `Comanda` avulsa — descartado
porque só existe uma forma de criação (não há variação de subtipo a encapsular); o construtor
direto de `Comanda`, como já é feito em `ComandaService.create`, é mais simples e consistente
com o restante do código.

## Arquivos a criar ou alterar

> Nota sobre caminhos: este repositório é anterior à adoção deste método e já tem convenção
> própria, observada em 100% do código existente (`docs/architecture/layers.md` descreve as
> responsabilidades de cada camada, sem fixar os caminhos de pasta): interfaces vivem em
> `app/core/interfaces/<mesmo caminho de adapters/infra>` (não em
> `app/interfaces/` na raiz), e os testes são arquivos únicos por módulo de negócio em
> `app/<modulo>_test.py` (não em `app/tests/unit/<caminho espelhado>`), usando
> `fastapi.testclient.TestClient` contra um banco sqlite em memória (`app/conftest.py`), sem
> mock de repositório. Para não fragmentar o padrão do repositório em duas convenções
> conflitantes dentro do mesmo módulo, esta feature segue a convenção já estabelecida em vez da
> literal do template da constituição. Ver observação também na tabela de Conformidade.

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| core/application | `app/core/application/use_cases/fiado_service.py` | alterar — novo método `lancar_avulso` | `app/fiado_test.py` |
| adapters/dtos | `app/adapter/dtos/fiado_dto.py` | alterar — novo `LancarFiadoAvulsoRequest` | `app/fiado_test.py` |
| adapters/controllers | `app/adapter/controllers/fiado_controller.py` | alterar — novo endpoint `POST /api/fiados/avulso` | `app/fiado_test.py` |
| docs | `docs/modules/fiado.md` | alterar — endpoint, request/response, regra de negócio, validação nova | — (documentação) |
| docs | `docs/matrix/endpoints-by-module.md` | alterar — nova linha do endpoint | — (documentação) |
| docs | `docs/architecture/errors.md` | alterar — novos códigos `data_origem_invalida` e `valor_devido_invalido` | — (documentação) |
| docs | `docs/postman/area-verde-collection.json` | alterar — nova requisição, se a manutenção manual da collection continuar em dia | — |

Nenhum arquivo novo em `core/domain` ou `core/interfaces`: o método novo reaproveita
`IComandaRepository`, `IClienteRepository` e `IConfiguracaoSistemaRepository`, já injetados em
`FiadoService`, sem depender de `caixa_service` para este caso de uso específico.

## Contrato entre camadas

`fiado_controller.lancar_avulso` recebe `LancarFiadoAvulsoRequest` (JSON camelCase), valida
formato via Pydantic (ex.: `valor` > 0 no schema) e chama
`FiadoService.lancar_avulso(cliente_id, valor, data_origem, vencimento_em=None, observacao=None)`.

`FiadoService.lancar_avulso`:
1. Busca o cliente por `cliente_id` (`cliente_nao_encontrado` se ausente) e garante que está
   ativo (`ClienteService.ensure_ativo` → `cliente_inativo`).
2. Valida `valor > 0` (`valor_devido_invalido` caso contrário).
3. Valida `data_origem <= hoje` (`data_origem_invalida` caso contrário).
4. Resolve o vencimento com `_resolve_vencimento(vencimento_em)`, já existente (mesma regra do
   fiado por comanda: futuro obrigatório ou padrão do sistema).
5. Monta uma `Comanda` nova: `status=PENDENTE`, `caixa_origem_id=None`, `cliente_id`,
   `nome_cliente`/`nome_cliente_snapshot=ClienteService.nome_operacional(cliente)`,
   `total=valor`, `aberta_em=pendente_em=datetime.combine(data_origem, time.min)`,
   `vencimento_em`, `observacao`.
6. Persiste via `comanda_repository.create` + `commit` + `refresh`, com `rollback` em exceção
   (mesmo padrão de `marcar_fiado`/`quitar`).
7. Retorna a `Comanda` criada; o controller serializa com `PendenciaDetalheResponse.from_model`
   (mesmo DTO de resposta já usado por `marcar_comanda_como_fiado`), com `itens: []`.

Erro é sempre `ApplicationError`/`NotFoundError` (`core/domain/exceptions`), tratado no mesmo
handler global de exceptions que já existe para os demais endpoints — nenhum tratamento novo.

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| — | — | Nenhuma dependência nova; reaproveita `IComandaRepository`, `IClienteRepository`, `IConfiguracaoSistemaRepository` já usadas em `FiadoService` | Banco sqlite em memória via `app/conftest.py` (convenção já existente do repositório) |

## Impacto no contrato de operação

Nenhum. Não há alvo novo de `Makefile` nem serviço novo de compose — a feature é código de
aplicação dentro do serviço já existente, coberta pelos alvos `test`/`test-coverage` já
existentes.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Confundir pendência avulsa com fiado de comanda em relatórios que assumem `itens` não vazio | Baixa | `itens` sempre existe como lista (vazia para avulso); `ItemComandaResponse` já lida com lista vazia; nenhum relatório usado hoje (`docs/matrix`) filtra por presença de itens, apenas por `status`/`vencimento_em`/`total` |
| `nome_cliente` (campo obrigatório da tabela) ficar inconsistente se o cliente for renomeado depois | Baixa | Mesmo comportamento do fiado por comanda hoje (snapshot no momento do lançamento); não é regressão, é padrão já aceito |
| Usuário confundir "data de origem" com "data do lançamento no sistema" | Média | Resposta da API expõe `pendenteEm` com a data de origem informada (não a data do lançamento), igual ao campo já retornado hoje para o fiado por comanda — nenhuma resposta nova a aprender |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Nenhum alvo de `Makefile` novo; testes rodam por `make test`/`make test-coverage`, já existentes, sem invocar `pytest` diretamente |
| Arquitetura limpa | `core/application` (novo método de `FiadoService`) não importa `adapters` nem `infra`; `adapters/controllers` e `adapters/dtos` são os únicos pontos que conhecem o novo método do caso de uso. **Desvio documentado**: a estrutura real do repositório usa `app/core/interfaces/adapters/...` em vez de `app/interfaces/...` da raiz — convenção pré-existente ao método, mantida por consistência (ver nota em "Arquivos a criar ou alterar") |
| Testes provam a entrega | Todo cenário de aceite da spec vira um `test_deve_<resultado>_quando_<condição>` em `app/fiado_test.py`; cobertura mínima de 90% no arquivo modificado (`fiado_service.py`). **Desvio documentado**: os testes exercitam a API via `TestClient` contra sqlite em memória (convenção de todo o módulo `fiado_test.py` e de todos os demais `*_test.py` do repositório), em vez de mock unitário por dependência injetada — reescrever a suíte existente para o padrão de mock é refatoração fora do escopo desta issue e quebraria a consistência com os 12 outros arquivos de teste do mesmo formato |
| Simplicidade defensável | Reaproveita `Comanda`, `_resolve_vencimento`, `ClienteService.ensure_ativo` e `ClienteService.nome_operacional` já existentes; nenhum padrão GoF novo (ver seção acima); nenhuma entidade, tabela ou migration nova |
| Autoria | Nenhum commit, PR ou documentação gerada por este plano atribui autoria a ferramenta de IA |
| Idioma | `spec.md`, este `plan.md`, mensagens de erro e documentação em português; identificadores de código em inglês/português técnico consistente com o restante do código (`lancar_avulso`, `data_origem`, seguindo o padrão já em português do domínio: `marcar_fiado`, `quitar`) |
| Migrations Alembic (específico do projeto) | Nenhuma migration nova: `Comanda.caixa_origem_id` já é opcional (`nullable=True`) e todos os demais campos usados (`total`, `pendente_em`, `vencimento_em`, `observacao`) já existem na tabela `comanda` |
