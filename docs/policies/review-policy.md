# Review Policy

## Ordem de revisão

1. Confirmar base da PR.
2. Confirmar branch de origem.
3. Confirmar se CI passou.
4. Revisar escopo.
5. Revisar migrations.
6. Revisar arquitetura.
7. Revisar testes.
8. Revisar documentação.
9. Decidir merge ou ajustes.

## Bloqueadores de merge

- PR apontando para base errada.
- CI falhando.
- Feature fora do escopo.
- Regra de negócio no controller.
- Core dependendo de DTO da adapter.
- Migration removendo estrutura de outro módulo sem justificativa.
- Testes ausentes para regra crítica.
- Documentação desatualizada.
- Secret commitado.

## Resultado da revisão

Uma revisão deve deixar explícito se a PR pode seguir para merge, precisa de
ajustes ou deve ser fechada e refeita a partir da base correta.

## Referências

- [Pull Request Policy](pull-request-policy.md)
- [Architecture Policy](architecture-policy.md)
- [Testing Policy](testing-policy.md)
- [Migration Policy](migration-policy.md)
