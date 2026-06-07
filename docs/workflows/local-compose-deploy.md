# Deploy local integrado com Docker Compose

Este fluxo sobe backend, frontend e PostgreSQL juntos para validacao local do
Area Verde. O objetivo e simular um deploy simples de integracao, sem misturar
codigo entre os repositorios e sem tratar este ambiente como producao.

## Escopo

- Repositorio orquestrador: `area-verde-api`
- Backend: `area-verde-api/app`
- Frontend: `../area-verde-frontend/app`
- Compose integrado: `area-verde-api/docker-compose.local.yml`

## Arquitetura do ambiente

- `db`
  Porta publica: `5432`
  Imagem: `postgres:16-alpine`
  Volume persistente: `area_verde_local_postgres_data`
- `api`
  Porta publica: `8001`
  Processo: `uvicorn api:app --host 0.0.0.0 --port 8000`
  Banco interno: `db:5432`
- `frontend`
  Porta publica: `3000`
  Servidor: `nginx:alpine`
  URL da API usada pelo frontend: `/api` (caminho relativo, embutido no
  build). O Nginx do frontend faz proxy reverso de `/api` para o servico
  `api` dentro da rede do compose, entao o navegador sempre chama o mesmo
  host/porta que carregou a pagina (funciona em `localhost`, IP da LAN,
  celular na mesma rede, etc., sem precisar saber o endereco do backend
  de antemao).

## Diagnostico realizado em 2026-06-01

Recursos antigos relacionados ao Area Verde encontrados na maquina:

- Containers em execucao:
  `area-verde-frontend-devcontainer`
  `area-verde-api-devcontainer`
  `area-verde-dev-postgres`
- Container parado:
  `area-verde_devcontainer-devcontainer-1`
- Redes:
  `area-verde-dev-network`
  `area-verde_devcontainer_area-verde-dev-network`
- Volumes:
  `area_verde_dev_postgres_data`
  `area-verde_devcontainer_area_verde_dev_postgres_data`

Impacto identificado:

- `3000` estava ocupado pelo frontend antigo do DevContainer.
- `8001` estava ocupado pelo backend antigo do DevContainer.
- `5432` estava livre no momento do diagnostico.
- Os volumes antigos foram preservados para evitar descarte desnecessario de
  dados locais.

## Limpeza executada antes da nova subida

Foram parados e removidos apenas os recursos antigos do Area Verde que
conflitavam com a nova subida:

```bash
docker stop \
  area-verde-frontend-devcontainer \
  area-verde-api-devcontainer \
  area-verde-dev-postgres

docker rm \
  area-verde-frontend-devcontainer \
  area-verde-api-devcontainer \
  area-verde-dev-postgres \
  area-verde_devcontainer-devcontainer-1

docker network rm \
  area-verde-dev-network \
  area-verde_devcontainer_area-verde-dev-network
```

Resultado:

- Containers removidos:
  `area-verde-frontend-devcontainer`
  `area-verde-api-devcontainer`
  `area-verde-dev-postgres`
  `area-verde_devcontainer-devcontainer-1`
- Redes removidas:
  `area-verde-dev-network`
  `area-verde_devcontainer_area-verde-dev-network`
- Volumes preservados:
  `area_verde_dev_postgres_data`
  `area-verde_devcontainer_area_verde_dev_postgres_data`

## Politica para volumes

Nenhum volume foi removido nesta configuracao.

- `area_verde_local_postgres_data` e o volume novo do stack integrado.
- `area_verde_dev_postgres_data` e
  `area-verde_devcontainer_area_verde_dev_postgres_data` foram mantidos.

Se algum volume PostgreSQL antigo precisar ser removido no futuro para reiniciar
o ambiente do zero, o impacto e total sobre os dados locais daquele banco.
Exemplo:

```bash
docker volume rm area_verde_dev_postgres_data
```

Esse comando apaga definitivamente o banco local armazenado naquele volume.

## Como subir

No backend:

```bash
cd area-verde-api
DOCKER_BUILDKIT=0 docker compose -f docker-compose.local.yml up --build -d
```

Observacao:
esta maquina nao possui o plugin `docker-buildx`, entao o build precisou usar o
builder classico com `DOCKER_BUILDKIT=0`.

## Como validar

```bash
docker compose -f docker-compose.local.yml ps
curl http://localhost:8001/health
curl http://localhost:3000
```

Endpoints esperados:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8001`
- Healthcheck da API: `http://localhost:8001/health`
- PostgreSQL: `localhost:5432`

## Como derrubar

```bash
cd area-verde-api
docker compose -f docker-compose.local.yml down
```

Para derrubar tambem o volume novo criado por este stack:

```bash
docker compose -f docker-compose.local.yml down -v
```

Esse ultimo comando remove `area_verde_local_postgres_data` e descarta os dados
do banco usados pelo ambiente integrado.
