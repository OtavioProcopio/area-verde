# DevContainer Policy

## Regras

- Para alterações Python, testes, lint, type check e validações da aplicação, o DevContainer é o ambiente preferencial.
- Não dependa de configuração oculta da máquina local.
- Não commitar `.env` real.
- Use `.env.example` como referência.
- Valide Docker Compose antes de finalizar mudanças relevantes.
- Não afirmar "validação Docker feita" sem especificar se foi feita no host ou dentro do DevContainer.

## O que deve rodar no DevContainer

```bash
cd app
make validate
make check
make ci
git diff --check
```

## O que pode precisar rodar no host

Alguns DevContainers podem não possuir o binário `docker`.

Nesse caso, os comandos abaixo devem ser executados no host:

```bash
cd app
POSTGRES_PASSWORD=local-dev-only docker compose config
docker build -t area-verde-api-test .
```

## Regra de transparência

Se um comando não foi executado no DevContainer, o agente deve informar:

- qual comando não rodou;
- por que não rodou;
- onde foi executado;
- qual foi o resultado.

## Boas práticas

- Mantenha dependências declaradas em arquivos do projeto.
- Não instale ferramentas necessárias apenas localmente.
- Documente qualquer requisito novo de ambiente.
