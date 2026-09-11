# Documentation Policy

## Regra principal

Toda feature que muda comportamento do sistema deve atualizar documentação.

## Arquivos que devem ser revisados

- `README.md`
- `docs/README.md`
- `docs/roadmap.md`
- `docs/overview.md`
- `docs/modules/<modulo>.md`
- `docs/postman/README.md`, se endpoints mudarem.
- Collection Postman, se houver manutenção manual dela.

## Status de módulos

Não documentar módulo como implementado se:

- não há endpoint;
- não há teste;
- não está registrado no `app/api.py`;
- não passou no CI;
- não foi mergeado na `develop`.

Quando não houver certeza, descreva como planejado, pendente ou em validação. Não
declare uma funcionalidade como disponível por inferência.

## Checklist

- [ ] README reflete estado atual.
- [ ] Roadmap reflete próximo módulo.
- [ ] Documento do módulo foi atualizado.
- [ ] Endpoints novos foram documentados.
- [ ] Limitações foram documentadas.
- [ ] O que ainda não está incluso foi documentado.

## Referências

- [Portal de documentação](../README.md)
- [Roadmap](../roadmap.md)
