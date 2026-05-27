# Padrão de Erros

## Formato

Erros de aplicação devem seguir o formato:

```json
{
  "code": "codigo_do_erro",
  "message": "Mensagem legível"
}
```

Internamente, as exceptions de domínio carregam:

- `code`
- `message`
- `status_code`

## Exemplos

| Código | Status | Uso |
|---|---:|---|
| `produto_nao_encontrado` | 404 | Produto inexistente |
| `produto_inativo` | 400 | Produto não pode ser usado |
| `comanda_nao_encontrada` | 404 | Comanda inexistente |
| `comanda_nao_aberta` | 400 | Operação exige comanda aberta |
| `comanda_sem_consumo` | 400 | Fechamento exige consumo lançado |
| `valor_pago_invalido` | 400 | Valor pago diferente do total da comanda |
| `fiado_nao_implementado` | 400 | FIADO bloqueado no MVP |
| `quantidade_invalida` | 400 | Quantidade menor ou igual a zero |
| `dados_invalidos` | 400/422 | Entrada inválida |
| `nome_duplicado` | 409 | Conflito de nome ativo |

## Regras

- Não retornar stack trace ao cliente.
- Não expor detalhes internos de banco.
- Preferir códigos estáveis em snake_case.
- Mensagens devem ser simples e compreensíveis.
