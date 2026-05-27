# Padrão de Erros

## Formato

Erros de aplicação devem seguir o formato:

```json
{
  "code": "codigo_do_erro",
  "message": "Mensagem legível"
}
```

Alguns erros podem incluir `details` quando a ação precisa devolver contexto
operacional resumido, como o bloqueio de fechamento de caixa por comandas
abertas.

Internamente, as exceptions de domínio carregam:

- `code`
- `message`
- `status_code`
- `details` opcional

## Exemplos

| Código | Status | Uso |
|---|---:|---|
| `produto_nao_encontrado` | 404 | Produto inexistente |
| `produto_inativo` | 400 | Produto não pode ser usado |
| `comanda_nao_encontrada` | 404 | Comanda inexistente |
| `comanda_nao_aberta` | 400 | Operação exige comanda aberta |
| `comanda_nao_pendente` | 400 | Operação exige comanda pendente |
| `comanda_sem_consumo` | 400 | Fechamento exige consumo lançado |
| `valor_pago_invalido` | 400 | Valor pago diferente do total da comanda |
| `cliente_nao_encontrado` | 404 | Cliente inexistente |
| `cliente_inativo` | 400 | Cliente não pode ser usado |
| `cliente_obrigatorio_para_fiado` | 400 | Fiado exige cliente cadastrado |
| `cliente_duplicado` | 409 | Já existe cliente ativo com mesmo nome ou telefone normalizado |
| `vencimento_invalido` | 400 | Vencimento anterior à data atual |
| `forma_pagamento_invalida` | 400 | Forma de pagamento bloqueada para o fluxo |
| `fiado_nao_pode_quitar_fiado` | 400 | FIADO não pode quitar pendência |
| `caixa_ja_aberto` | 400 | Abertura duplicada de caixa |
| `caixa_aberto_nao_encontrado` | 400/404 | Operação exige caixa aberto ou consulta não encontrou caixa aberto |
| `caixa_nao_encontrado` | 404 | Caixa inexistente |
| `caixa_fechado` | 400 | Caixa fechado não aceita movimentação |
| `existem_comandas_abertas` | 400 | Fechamento de caixa bloqueado por comandas abertas |
| `sangria_invalida` | 400 | Sangria deixaria dinheiro esperado negativo |
| `quantidade_invalida` | 400 | Quantidade menor ou igual a zero |
| `dados_invalidos` | 400/422 | Entrada inválida |
| `nome_duplicado` | 409 | Conflito de nome ativo |

## Regras

- Não retornar stack trace ao cliente.
- Não expor detalhes internos de banco.
- Preferir códigos estáveis em snake_case.
- Mensagens devem ser simples e compreensíveis.
