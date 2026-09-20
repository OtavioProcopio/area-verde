# Checklist — Validar nome duplicado no cadastro de produto / Dados

> Avalia a **qualidade da especificação** quanto ao risco de integridade de dados (novo índice
> único sobre dado existente), não do código. `[x]` significa "requisito aprovado por revisor
> humano". O agente não se autoaprova.

## Integridade da unicidade

- [ ] A spec deixa claro que a unicidade vale só entre produtos **ativos** — inativo não bloqueia reuso do nome
- [ ] A spec deixa claro o escopo da unicidade (global, não por categoria) e a decisão está registrada em Esclarecimentos
- [ ] A spec deixa claro que a comparação ignora maiúsculas/minúsculas e espaços nas pontas

## Dado pré-existente

- [ ] Fora de escopo deixa explícito que corrigir/unificar duplicados já existentes na base não faz parte desta feature
- [ ] A spec não presume que a base está livre de duplicados hoje — a própria issue relata que já ocorreram

## Consistência com o padrão já adotado

- [ ] A spec segue o mesmo comportamento já em produção para `CategoriaProduto` (nome duplicado entre ativos rejeitado, índice único como salvaguarda), sem introduzir uma regra divergente para produto
