# Checklist — Fechamento avançado de comanda: pagamento parcial e acréscimo/desconto / Dados

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] A spec deixa claro que o total original da comanda (itens) não é o mesmo dado que o total ajustado (RF-10, RF-13)
- [ ] A spec exige que todo acréscimo/desconto fique associado a uma descrição persistida, não só a um valor (RF-09)
- [ ] A spec cobre o caso de múltiplas comandas/pagamentos concorrentes na mesma feature (ou declara explicitamente que está fora de escopo)

## Clareza

- [ ] Fica claro se "saldo restante" pode ser negativo apenas por desconto (RF-16) e nunca por excesso de pagamento (RF-04 impede isso) — os dois casos de valor negativo/zero não se confundem
- [ ] Fica claro que o valor pago em cada pagamento individual é imutável depois de registrado (nenhum RF menciona edição de pagamento)

## Consistência

- [ ] RNF-01 (saldo sempre derivado de pagamentos e ajustes persistidos, nunca duplicado) é compatível com RF-13 (expor total original, total ajustado e saldo restante) sem exigir uma coluna redundante
- [ ] Os critérios de aceite sobre quitação parcial de fiado (RF-06) usam a mesma definição de "saldo devido" usada nos critérios de pagamento parcial de comanda aberta (RF-01, RF-02)

## Testabilidade

- [ ] Existe critério de aceite que verifica que o total original da comanda nunca é sobrescrito por um acréscimo/desconto (apenas o total ajustado muda)
- [ ] Existe critério de aceite que force o cálculo de saldo a partir de mais de um pagamento e mais de um ajuste na mesma comanda, verificando a soma corretamente
