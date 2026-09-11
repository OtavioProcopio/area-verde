# Diagrama de Classes Global

Fonte real: `app/core/domain/models.py` e `app/core/domain/enums/`.

```mermaid
classDiagram
    class ConfiguracaoSistema {
        +Long id
        +String senhaAcessoHash
        +Integer diasParaAlertaFiado
        +Boolean permitirEstoqueNegativo
        +String nomeBar
        +String observacao
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class CategoriaProduto {
        +Long id
        +String nome
        +Boolean ativo
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class Produto {
        +Long id
        +Long categoriaId
        +String nome
        +BigDecimal precoVenda
        +TipoProduto tipoProduto
        +Boolean controlaEstoque
        +UnidadeEstoque unidadeEstoque
        +BigDecimal quantidadeEstoque
        +BigDecimal quantidadeBaixaPorVenda
        +BigDecimal estoqueMinimo
        +Boolean ativo
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class ProdutoComposicao {
        +Long id
        +Long produtoPaiId
        +Long produtoComponenteId
        +BigDecimal quantidadeBaixa
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class Cliente {
        +Long id
        +String nome
        +String apelido
        +String telefone
        +String observacao
        +Boolean ativo
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class Comanda {
        +Long id
        +Long caixaOrigemId
        +Long clienteId
        +String nomeCliente
        +String nomeClienteSnapshot
        +StatusComanda status
        +BigDecimal total
        +DateTime abertaEm
        +DateTime fechadaEm
        +DateTime canceladaEm
        +DateTime pendenteEm
        +Date vencimentoEm
        +String observacao
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class ItemComanda {
        +Long id
        +Long comandaId
        +Long produtoId
        +String nomeProdutoSnapshot
        +BigDecimal precoUnitarioSnapshot
        +BigDecimal quantidade
        +BigDecimal quantidadeBaixadaEstoque
        +BigDecimal totalItem
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class Caixa {
        +Long id
        +Date data
        +StatusCaixa status
        +BigDecimal valorInicial
        +BigDecimal dinheiroEsperado
        +BigDecimal dinheiroInformado
        +BigDecimal diferenca
        +DateTime abertoEm
        +DateTime fechadoEm
        +DateTime criadoEm
        +DateTime atualizadoEm
    }

    class Pagamento {
        +Long id
        +Long caixaId
        +Long comandaId
        +FormaPagamento formaPagamento
        +BigDecimal valor
        +String observacao
        +DateTime criadoEm
    }

    class MovimentoCaixa {
        +Long id
        +Long caixaId
        +TipoMovimentoCaixa tipo
        +BigDecimal valor
        +String observacao
        +DateTime criadoEm
    }

    class MovimentoEstoque {
        +Long id
        +Long produtoId
        +TipoMovimentoEstoque tipo
        +BigDecimal quantidade
        +BigDecimal estoqueAntes
        +BigDecimal estoqueDepois
        +OrigemMovimentoEstoque origem
        +Long referenciaId
        +String observacao
        +DateTime criadoEm
    }

    class UnidadeEstoque {
        <<enumeration>>
        UNIDADE
        ML
    }

    class TipoProduto {
        <<enumeration>>
        SIMPLES
        COMPOSTO
    }

    class StatusComanda {
        <<enumeration>>
        ABERTA
        FECHADA
        PENDENTE
        CANCELADA
    }

    class StatusCaixa {
        <<enumeration>>
        ABERTO
        FECHADO
    }

    class FormaPagamento {
        <<enumeration>>
        DINHEIRO
        PIX
        CARTAO
        FIADO
    }

    class TipoMovimentoCaixa {
        <<enumeration>>
        ABERTURA
        SANGRIA
        REFORCO
        AJUSTE
    }

    class TipoMovimentoEstoque {
        <<enumeration>>
        ENTRADA
        SAIDA_VENDA
        DEVOLUCAO_CANCELAMENTO
        AJUSTE
    }

    class OrigemMovimentoEstoque {
        <<enumeration>>
        COMANDA
        ENTRADA_MANUAL
        AJUSTE_MANUAL
        CANCELAMENTO
    }

    CategoriaProduto "1" --> "0..*" Produto : possui
    Cliente "1" --> "0..*" Comanda : possui historico
    Caixa "1" --> "0..*" Comanda : origem operacional
    Comanda "1" --> "0..*" ItemComanda : contem
    Produto "1" --> "0..*" ItemComanda : vendido como
    Produto "1" --> "0..*" MovimentoEstoque : movimenta
    Produto "1" --> "0..*" ProdutoComposicao : composto por
    ProdutoComposicao "0..*" --> "1" Produto : componente
    Caixa "1" --> "0..*" Pagamento : registra
    Comanda "1" --> "0..*" Pagamento : recebe
    Caixa "1" --> "0..*" MovimentoCaixa : possui

    Produto --> UnidadeEstoque : usa
    Produto --> TipoProduto : possui
    Comanda --> StatusComanda : possui
    Caixa --> StatusCaixa : possui
    Pagamento --> FormaPagamento : usa
    MovimentoCaixa --> TipoMovimentoCaixa : possui
    MovimentoEstoque --> TipoMovimentoEstoque : possui
    MovimentoEstoque --> OrigemMovimentoEstoque : possui
```

## Observacoes

- `ConfiguracaoSistema` existe no modelo de dominio, mas o modulo operacional
  de Configuracoes ainda esta pendente.
- `FormaPagamento.FIADO` existe no enum, mas nao representa pagamento recebido:
  fiado vira comanda `PENDENTE` e a quitacao usa `DINHEIRO`, `PIX` ou `CARTAO`.
