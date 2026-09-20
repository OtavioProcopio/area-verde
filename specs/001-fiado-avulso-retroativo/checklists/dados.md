# Checklist — Fiado avulso retroativo / Dados

> Avalia a **qualidade da especificação** quanto ao risco de dados financeiros e de migração
> de histórico, não do código. `[x]` significa "requisito aprovado por revisor humano". O
> agente não se autoaprova.

## Integridade do valor devido

- [ ] A spec deixa claro que o valor devido é obrigatório e não pode ser zero ou negativo (RF-05)
- [ ] A spec não deixa em aberto se o valor aceita casas decimais de centavos (consistente com o restante do sistema monetário)

## Integridade da data de origem

- [ ] A spec deixa claro que a data de origem pode ser qualquer data passada, sem limite mínimo (Esclarecimentos)
- [ ] A spec deixa claro que data de origem no futuro é rejeitada (RF-04), evitando dívida "a vencer antes de existir"
- [ ] A spec não confunde data de origem (quando a dívida começou) com data do lançamento no sistema (quando o operador registrou)

## Consistência com o histórico existente

- [ ] A spec exige que a pendência avulsa apareça nas mesmas listagens e no mesmo total do cliente que as pendências originadas de comanda (RF-07), sem criar uma fonte de verdade paralela
- [ ] A spec exige que a quitação da pendência avulsa produza o mesmo efeito sobre o caixa que a quitação de uma pendência normal (RF-08), sem caminho de pagamento divergente
- [ ] Fora de escopo deixa explícito que não há edição nem exclusão da pendência avulsa após lançada, reduzindo risco de divergência silenciosa do valor migrado
