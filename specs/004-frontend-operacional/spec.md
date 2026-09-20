# Especificação — Corrigir documentação que trata o frontend como pendente/futuro

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

`README.md`, `docs/roadmap.md` e `docs/matrix/pending-gaps.md` deste repositório ainda tratam
o frontend como um item futuro/pendente do MVP: o `README.md` lista "Frontend — Operação
visual do bar" na tabela "Pendente"; `docs/roadmap.md` lista "Frontend operacional" nas
seções "Depois"/"Futuro" e na ordem consolidada como item 13 com status "Futuro";
`docs/matrix/pending-gaps.md` tem uma linha "Frontend operacional — Futuro — Ainda não há
aplicação visual para atendimento". Isso é falso hoje: o repositório
[`area-verde-frontend`](https://github.com/OtavioProcopio/area-verde-frontend) existe, está
em desenvolvimento ativo (múltiplas features e correções mergeadas) e em uso real pelo dono
do bar testando o sistema no dia a dia. Quem lê esses três arquivos pra entender o estado do
projeto é enganado sobre um fato básico e verificável.

## Objetivo

`README.md`, `docs/roadmap.md` e `docs/matrix/pending-gaps.md` refletem que o frontend existe,
está implementado e em uso real, com link para o repositório `area-verde-frontend`, sem se
contradizerem entre si sobre esse ponto.

## Fora de escopo

- Qualquer alteração de código (esta é uma feature 100% documental).
- Auditoria completa dos demais ~40 arquivos de `docs/` deste repositório — escopo limitado
  aos três arquivos citados no Problema, que são os que fazem a afirmação incorreta.
- Alterar `docker-compose.local.yml` ou qualquer caminho relativo ao checkout do frontend —
  não é uma inconsistência de conteúdo, é particularidade de nome de pasta local.
- Descrever o frontend em detalhe (arquitetura, stack, módulos) — isso já vive no próprio
  repositório `area-verde-frontend`; aqui só se corrige a informação de status.

## Personas e cenários de uso

- **Quem lê o README pela primeira vez** (novo colaborador, ou o próprio dono do bar revisando
  o estado do projeto): precisa saber, sem precisar checar outro repositório, que o sistema já
  tem uma interface visual em uso, não só uma API.
- **Quem decide prioridade** a partir do roadmap/pending-gaps: não pode planejar como se o
  frontend ainda estivesse por começar.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | `README.md` deve mover a entrada "Frontend" da tabela "Pendente" para uma seção que reflita que está implementado e em uso, com link para o repositório `area-verde-frontend`. | obrigatório |
| RF-02 | `docs/roadmap.md` deve mover "Frontend operacional" das seções "Depois"/"Futuro" e da "Ordem consolidada" para uma categoria que reflita status implementado/em uso, com o mesmo link. | obrigatório |
| RF-03 | `docs/matrix/pending-gaps.md` deve remover ou reescrever a linha que descreve o frontend como "Futuro"/"ainda não há aplicação visual", registrando a correção na seção "Itens corrigidos" já existente no próprio documento. | obrigatório |
| RF-04 | Os três arquivos não podem se contradizer entre si sobre o status do frontend após a correção. | obrigatório |

## Requisitos não funcionais

Nenhum — feature documental, sem critério de desempenho/disponibilidade/segurança aplicável.

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Corrigir documentação que trata o frontend como pendente/futuro

  Cenário: README reflete o frontend como implementado
    Dado o README.md atual, que lista "Frontend" na tabela "Pendente"
    Quando a correção é aplicada
    Então "Frontend" aparece como implementado/em uso, com link para area-verde-frontend
    Mas nenhuma outra linha da tabela "Pendente" é alterada sem necessidade

  Cenário: roadmap reflete o frontend como implementado
    Dado o docs/roadmap.md atual, que lista "Frontend operacional" em "Depois" e como item 13 "Futuro"
    Quando a correção é aplicada
    Então o roadmap não classifica mais o frontend como futuro/pendente
    Mas a ordem consolidada dos demais itens permanece coerente

  Cenário: pending-gaps não afirma mais que o frontend não existe
    Dado o docs/matrix/pending-gaps.md atual, com a linha "Frontend operacional — Futuro"
    Quando a correção é aplicada
    Então essa linha é removida ou corrigida e a mudança é registrada em "Itens corrigidos"
    Mas nenhuma outra linha da matriz é alterada sem necessidade

  Cenário: os três documentos são consistentes entre si
    Dado os três arquivos corrigidos
    Quando lidos em conjunto
    Então nenhum deles ainda trata o frontend como pendente/futuro
```

## Ambiguidades

Nenhuma — o pedido já delimita os três arquivos e a natureza da correção o suficiente para
prosseguir sem checagem adicional.

## Métricas de sucesso

- `grep -rn "Futuro\|Pendente\|Depois" README.md docs/roadmap.md docs/matrix/pending-gaps.md`
  não retorna mais nenhuma linha associando essas palavras ao frontend.
- Qualquer um dos três arquivos, lido isoladamente, informa corretamente que o frontend existe
  e está em uso.
