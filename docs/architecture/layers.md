# Camadas e Responsabilidades

## Controller

- Recebe requests HTTP.
- Aplica validação básica via DTO.
- Chama service/use case.
- Retorna DTO de response.
- Não contém regra de negócio.
- Não acessa banco diretamente.

## DTO

- Define contrato de entrada e saída.
- Usa aliases camelCase no JSON.
- Valida formato e campos obrigatórios simples.
- Não orquestra regra de negócio.

## Service / Use Case

- Contém regra de negócio.
- Valida domínio.
- Orquestra transações.
- Chama repositories.
- Coordena integração entre módulos.
- Não importa DTOs da camada `adapter`.

## Repository

- Acessa banco de dados.
- Encapsula consultas e persistência.
- Não contém regra de negócio.
- Não decide fluxo de domínio.

## Domain

- Contém entidades, enums e exceptions.
- Representa conceitos centrais do sistema.
- Deve permanecer livre de detalhes HTTP.

## Infra

- Configura banco, settings, container de dependências e ferramentas técnicas.
