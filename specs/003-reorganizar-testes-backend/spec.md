# Especificação — Reorganizar testes do backend para espelhar a arquitetura em camadas

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

Todo o código de produção do backend já segue arquitetura em camadas (`core/domain`,
`core/application/use_cases`, `core/interfaces`, `adapter/controllers`, `adapter/repositories`,
`adapter/dtos`, `infra/*`), mas os testes estão todos soltos direto em `app/`, sem nenhuma
organização que reflita essa arquitetura. Isso dificulta saber o que cada teste cobre e a que
camada pertence, e tende a piorar conforme o projeto cresce.

## Objetivo

Os testes do backend passam a viver numa área dedicada, organizada de um jeito que deixa
evidente que camada/módulo cada teste cobre — sem perder nenhuma cobertura, sem quebrar nenhum
comando de automação já existente (`make test`, `make validate`, CI) e sem mudar o que cada
teste verifica.

## Fora de escopo

- Reescrever testes existentes em um estilo diferente (ex.: trocar teste via API/TestClient por
  teste unitário com mocks de cada dependência). Esta feature reorganiza onde os testes vivem,
  não como eles verificam o comportamento.
- Adicionar teste novo para comportamento ainda não coberto.
- Mudar qual fixture (`test_engine`, `test_session`, `test_container`) cada teste usa.
- Separar testes em unitário vs. integração (não existe essa distinção real hoje — o marcador
  `integration` do pytest existe mas nenhum teste o usa).
- Mudar o conteúdo do `Makefile`, do `docker-compose.yml` ou do CI além do necessário para os
  comandos continuarem funcionando exatamente como hoje.

## Personas e cenários de uso

- **Quem desenvolve no backend**: ao abrir a árvore de testes, encontra o teste de um módulo no
  mesmo "endereço" relativo da camada que ele cobre, sem precisar vasculhar uma lista plana de
  12 arquivos soltos para achar o teste certo.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Os arquivos de teste devem deixar de ficar soltos na raiz de `app/` e passar a viver numa área de testes dedicada, separada do código de produção. | obrigatório |
| RF-02 | Os testes de módulo de negócio (que hoje exercitam o fluxo inteiro via API) vão para uma única área que representa a camada de aplicação (`core/application/use_cases`), um arquivo por módulo, mantendo o teste como está. Os testes que cobrem a composição raiz da aplicação (criação do app, schema, endpoint de saúde), em vez de uma camada específica, ficam na raiz da área de testes, não dentro de uma pasta de camada. | obrigatório |
| RF-03 | Nenhum teste existente pode ser removido, ter sua verificação enfraquecida, ou passar a ser pulado (`skip`) como efeito da reorganização. | obrigatório |
| RF-04 | Todo comando de automação já existente que roda testes (`make test`, `make test-coverage`, `make validate`, o job de CI) deve continuar funcionando sem alteração no comando em si — só configuração de descoberta de teste/cobertura pode mudar, se necessário. | obrigatório |
| RF-05 | Toda documentação que hoje referencia o caminho de um arquivo de teste (`docs/architecture/tests.md`, `docs/matrix/tests-by-module.md`, e as seções "Testes relacionados" de `docs/modules/*.md`) deve ser atualizada para o caminho novo. | obrigatório |

## Requisitos não funcionais

Nenhum requisito não funcional novo além dos já cobertos pela constituição do projeto
(cobertura mínima de 90% por arquivo modificado — neste caso, arquivo movido conta como
modificado apenas se seu conteúdo mudar; um `git mv` puro não precisa reatingir cobertura
individual, já que o comportamento coberto não muda).

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Reorganizar testes do backend para espelhar a arquitetura em camadas

  Cenário: Nenhum teste é perdido na reorganização
    Dado a suíte de testes completa do backend antes da reorganização
    Quando os arquivos de teste são movidos para a nova área de testes
    Então a mesma quantidade de testes (ou mais, nunca menos) continua passando
    Mas nenhuma asserção existente foi removida ou enfraquecida

  Cenário: Automação continua funcionando sem mudança de comando
    Dado o backend reorganizado
    Quando alguém roda `make validate` exatamente como rodava antes
    Então o comando passa, incluindo build, formatação, lint, testes e cobertura

  Cenário: Documentação aponta para o caminho novo
    Dado um módulo cujo teste foi movido
    Quando alguém consulta a documentação desse módulo
    Então o caminho do teste listado é o caminho novo, não o antigo
```

## Ambiguidades

Nenhuma pendente — ver tabela `Esclarecimentos` ao final.

## Métricas de sucesso

- `make validate` passa, com a mesma cobertura total (ou maior) de antes da reorganização.
- Nenhum arquivo de teste continua solto na raiz de `app/`.

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| Até onde espelhar a arquitetura em camadas, já que os testes atuais exercitam o fluxo inteiro via API? | Mover mantendo o teste como está, uma pasta por módulo dentro de `core/application/use_cases`; testes de composição raiz (app, schema, saúde) ficam na raiz da área de testes. | 2026-09-19 |
