classDiagram

%% =========================
%% CLASSES PRINCIPAIS
%% =========================

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
    +String nome
    +BigDecimal precoVenda
    +Boolean controlaEstoque
    +UnidadeEstoque unidadeEstoque
    +BigDecimal quantidadeEstoque
    +BigDecimal quantidadeBaixaPorVenda
    +BigDecimal estoqueMinimo
    +Boolean ativo
    +DateTime criadoEm
    +DateTime atualizadoEm
}

class Comanda {
    +Long id
    +String nomeCliente
    +StatusComanda status
    +BigDecimal total
    +DateTime abertaEm
    +DateTime fechadaEm
    +Date vencimentoEm
    +String observacao
    +DateTime criadoEm
    +DateTime atualizadoEm
}

class ItemComanda {
    +Long id
    +String nomeProdutoSnapshot
    +BigDecimal precoUnitarioSnapshot
    +BigDecimal quantidade
    +BigDecimal quantidadeBaixadaEstoque
    +BigDecimal totalItem
    +DateTime criadoEm
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
    +FormaPagamento formaPagamento
    +BigDecimal valor
    +DateTime criadoEm
}

class MovimentoCaixa {
    +Long id
    +TipoMovimentoCaixa tipo
    +BigDecimal valor
    +String observacao
    +DateTime criadoEm
}

class MovimentoEstoque {
    +Long id
    +TipoMovimentoEstoque tipo
    +BigDecimal quantidade
    +BigDecimal estoqueAntes
    +BigDecimal estoqueDepois
    +OrigemMovimentoEstoque origem
    +Long referenciaId
    +String observacao
    +DateTime criadoEm
}

%% =========================
%% ENUMS
%% =========================

class UnidadeEstoque {
    <<enumeration>>
    UNIDADE
    ML
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

%% =========================
%% RELACIONAMENTOS
%% =========================

CategoriaProduto "1" --> "0..*" Produto : possui

Comanda "1" --> "0..*" ItemComanda : contém
Produto "1" --> "0..*" ItemComanda : vendido como

Produto "1" --> "0..*" MovimentoEstoque : movimenta

Caixa "1" --> "0..*" Pagamento : registra
Comanda "1" --> "0..*" Pagamento : recebe

Caixa "1" --> "0..*" MovimentoCaixa : possui

Produto --> UnidadeEstoque : usa
Comanda --> StatusComanda : possui
Caixa --> StatusCaixa : possui
Pagamento --> FormaPagamento : usa
MovimentoCaixa --> TipoMovimentoCaixa : possui
MovimentoEstoque --> TipoMovimentoEstoque : possui
MovimentoEstoque --> OrigemMovimentoEstoque : possui