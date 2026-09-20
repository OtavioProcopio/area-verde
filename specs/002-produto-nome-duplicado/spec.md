# Especificação — Validar nome duplicado no cadastro de produto

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

O cadastro de produto não valida nome duplicado antes de salvar — diferente do cadastro de
categoria, que já bloqueia nome repetido entre categorias ativas. Durante teste real de uso,
produtos foram cadastrados duplicados. Produto duplicado polui a lista de venda, atrapalha
relatórios e estoque, e pode levar o operador a escolher o produto errado no balcão.

## Objetivo

Ao tentar cadastrar ou editar um produto com um nome que já pertence a outro produto ativo (no
escopo definido nos requisitos), o sistema rejeita a operação, com uma mensagem clara. Produto
inativo não bloqueia reuso do nome, do mesmo jeito que já funciona para categoria.

## Fora de escopo

- Unificar ou mesclar produtos já duplicados hoje na base (correção de dados existentes).
- Validação de nome duplicado para categoria ou qualquer outra entidade — já existe e não muda.
- Sugestão automática de nome ou correção automática (ex.: "Água (2)").
- Mudar a busca por nome (`GET /api/produtos?nome=`), que continua um filtro parcial.

## Personas e cenários de uso

- **Operador cadastrando produto**: ao tentar salvar um produto novo com nome igual a um já
  existente (ativo), recebe um erro claro em vez de criar um duplicado silenciosamente.
- **Operador editando produto**: ao renomear um produto para um nome já usado por outro produto
  ativo, recebe o mesmo erro; renomear para o próprio nome atual continua funcionando.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O sistema deve rejeitar o cadastro de um produto novo cujo nome coincide com o de outro produto já ativo, no escopo de unicidade definido em RF-05. | obrigatório |
| RF-02 | O sistema deve rejeitar a edição de um produto para um nome que coincide com o de outro produto já ativo (excluindo o próprio produto sendo editado), no mesmo escopo de RF-05. | obrigatório |
| RF-03 | A comparação de nome duplicado deve ignorar diferença de maiúsculas/minúsculas e espaços nas pontas, do mesmo jeito que já ocorre para categoria. | obrigatório |
| RF-04 | Produto inativo não conta para a verificação de duplicidade — seu nome pode ser reutilizado por outro produto. | obrigatório |
| RF-05 | A unicidade de nome é global: nenhum produto ativo pode repetir nome de outro produto ativo, não importa a categoria — mesmo escopo já usado para categoria de produto. | obrigatório |
| RF-06 | O cadastro de produto composto (via `/api/produtos/compostos`) também deve respeitar a mesma validação de nome duplicado do produto simples. | obrigatório |
| RF-07 | Além da validação da aplicação, deve existir uma salvaguarda de unicidade a nível de banco de dados, para o mesmo escopo de RF-05, seguindo o padrão já usado em categoria de produto. | obrigatório |

## Requisitos não funcionais

Nenhum requisito não funcional novo além dos já cobertos pela constituição do projeto
(cobertura mínima de 90% por arquivo modificado).

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Validar nome duplicado no cadastro de produto

  Cenário: Rejeitar cadastro de produto com nome já usado por produto ativo
    Dado um produto ativo cadastrado com um nome
    Quando o operador tenta cadastrar um novo produto com o mesmo nome (no escopo de unicidade)
    Então o sistema rejeita o cadastro
    Mas nenhum produto novo é criado

  Cenário: Ignorar maiúsculas/minúsculas e espaços na comparação
    Dado um produto ativo cadastrado com um nome
    Quando o operador tenta cadastrar um produto com o mesmo nome em outra caixa ou com espaços extras nas pontas
    Então o sistema rejeita o cadastro do mesmo jeito

  Cenário: Permitir reaproveitar nome de produto inativo
    Dado um produto inativo cadastrado com um nome
    Quando o operador cadastra um novo produto ativo com esse mesmo nome
    Então o cadastro é aceito

  Cenário: Rejeitar edição que duplica nome de outro produto ativo
    Dado dois produtos ativos com nomes diferentes
    Quando o operador edita um deles para usar o nome do outro
    Então o sistema rejeita a edição
    Mas o nome original do produto editado permanece

  Cenário: Permitir editar produto mantendo o próprio nome
    Dado um produto ativo cadastrado
    Quando o operador edita esse produto sem mudar o nome
    Então a edição é aceita normalmente

  Cenário: Rejeitar produto composto com nome duplicado
    Dado um produto ativo cadastrado com um nome
    Quando o operador tenta cadastrar um produto composto com o mesmo nome
    Então o sistema rejeita o cadastro do produto composto
    Mas nenhum produto nem composição são criados
```

## Ambiguidades

Nenhuma pendente — ver tabela `Esclarecimentos` ao final.

## Métricas de sucesso

- Nenhum novo produto duplicado é criado a partir da entrega desta feature em diante.
- O erro de nome duplicado aparece de forma clara para quem cadastra, sem exigir consulta manual
  à lista de produtos para descobrir a duplicidade.

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| Unicidade de nome é global ou por categoria? | Global — mesmo escopo já usado para categoria de produto. | 2026-09-19 |
