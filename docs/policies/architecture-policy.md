# Architecture Policy

## Regras

- Não colocar regra de negócio em controller.
- Não acessar banco direto no controller.
- Não criar DTO dentro do service.
- Não duplicar entidade.
- Não recriar repository existente.
- Não quebrar padrão de pastas.
- Não criar arquitetura paralela.
- Service deve orquestrar regra de negócio.
- Repository deve acessar banco.
- DTO deve formatar entrada e saída.
- Domain deve conter entidades, enums e exceptions.

## Ao implementar módulo

- Leia módulos existentes antes de criar arquivos.
- Siga os nomes e padrões já usados.
- Prefira alteração incremental.
- Crie interfaces quando o padrão local exigir.
- Mantenha transações em camada de aplicação quando houver múltiplas operações.
