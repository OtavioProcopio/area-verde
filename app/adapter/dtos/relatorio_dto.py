from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from core.application.use_cases.relatorio_service import (
    CaixaRelatorio,
    ComandaPorStatus,
    ComandasResumo,
    EstoqueConsumidoItem,
    EstoqueResumo,
    FiadosResumo,
    ItemEstoqueRelatorio,
    MovimentosCaixaResumo,
    PagamentosResumo,
    PendenciaRelatorio,
    ProdutoMaisVendido,
    RelatorioCaixa,
    RelatorioComandas,
    RelatorioDiario,
    RelatorioEstoque,
    RelatorioFiados,
    VendasResumo,
)
from core.domain.enums import StatusCaixa, StatusComanda, UnidadeEstoque


class CaixaRelatorioResponse(BaseModel):
    id: int
    data: Optional[date] = None
    status: StatusCaixa
    valor_inicial: Decimal = Field(alias="valorInicial")
    dinheiro_esperado: Decimal = Field(alias="dinheiroEsperado")
    dinheiro_informado: Optional[Decimal] = Field(
        default=None, alias="dinheiroInformado"
    )
    diferenca: Optional[Decimal] = None
    aberto_em: datetime = Field(alias="abertoEm")
    fechado_em: Optional[datetime] = Field(default=None, alias="fechadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(
        cls,
        caixa: CaixaRelatorio,
        incluir_data: bool = False,
    ) -> "CaixaRelatorioResponse":
        return cls(
            id=caixa.id,
            data=caixa.data if incluir_data else None,
            status=caixa.status,
            valorInicial=caixa.valor_inicial,
            dinheiroEsperado=caixa.dinheiro_esperado,
            dinheiroInformado=caixa.dinheiro_informado,
            diferenca=caixa.diferenca,
            abertoEm=caixa.aberto_em,
            fechadoEm=caixa.fechado_em,
        )


class VendasResumoResponse(BaseModel):
    total_vendido: Decimal = Field(alias="totalVendido")
    total_recebido: Decimal = Field(alias="totalRecebido")
    total_fiado_gerado: Decimal = Field(alias="totalFiadoGerado")
    total_pendente_atual: Decimal = Field(alias="totalPendenteAtual")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, resumo: VendasResumo) -> "VendasResumoResponse":
        return cls(
            totalVendido=resumo.total_vendido,
            totalRecebido=resumo.total_recebido,
            totalFiadoGerado=resumo.total_fiado_gerado,
            totalPendenteAtual=resumo.total_pendente_atual,
        )


class PagamentosResumoResponse(BaseModel):
    dinheiro: Decimal
    pix: Decimal
    cartao: Decimal
    total_recebido: Optional[Decimal] = Field(default=None, alias="totalRecebido")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(
        cls,
        resumo: PagamentosResumo,
        incluir_total: bool = False,
    ) -> "PagamentosResumoResponse":
        return cls(
            dinheiro=resumo.dinheiro,
            pix=resumo.pix,
            cartao=resumo.cartao,
            totalRecebido=resumo.total_recebido if incluir_total else None,
        )


class ComandasResumoResponse(BaseModel):
    total: Optional[int] = None
    abertas: int
    fechadas: int
    pendentes: int
    canceladas: int
    valor_fechado: Optional[Decimal] = Field(default=None, alias="valorFechado")
    valor_pendente: Optional[Decimal] = Field(default=None, alias="valorPendente")
    valor_cancelado: Optional[Decimal] = Field(default=None, alias="valorCancelado")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(
        cls,
        resumo: ComandasResumo,
        incluir_valores: bool = False,
        incluir_total: bool = False,
    ) -> "ComandasResumoResponse":
        return cls(
            total=resumo.total if incluir_total else None,
            abertas=resumo.abertas,
            fechadas=resumo.fechadas,
            pendentes=resumo.pendentes,
            canceladas=resumo.canceladas,
            valorFechado=resumo.valor_fechado if incluir_valores else None,
            valorPendente=resumo.valor_pendente if incluir_valores else None,
            valorCancelado=resumo.valor_cancelado if incluir_valores else None,
        )


class FiadosDiarioResponse(BaseModel):
    gerados_no_dia: Decimal = Field(alias="geradosNoDia")
    quitados_no_dia: Decimal = Field(alias="quitadosNoDia")
    pendentes_atuais: Decimal = Field(alias="pendentesAtuais")
    vencidos_atuais: Decimal = Field(alias="vencidosAtuais")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, resumo: FiadosResumo) -> "FiadosDiarioResponse":
        return cls(
            geradosNoDia=resumo.gerados_no_dia,
            quitadosNoDia=resumo.quitados_no_dia,
            pendentesAtuais=resumo.pendentes_atuais,
            vencidosAtuais=resumo.vencidos_atuais,
        )


class FiadosResumoResponse(BaseModel):
    total_pendente: Decimal = Field(alias="totalPendente")
    total_vencido: Decimal = Field(alias="totalVencido")
    total_quitado_periodo: Decimal = Field(alias="totalQuitadoPeriodo")
    quantidade_pendencias: int = Field(alias="quantidadePendencias")
    quantidade_vencidas: int = Field(alias="quantidadeVencidas")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, resumo: FiadosResumo) -> "FiadosResumoResponse":
        return cls(
            totalPendente=resumo.total_pendente,
            totalVencido=resumo.total_vencido,
            totalQuitadoPeriodo=resumo.total_quitado_periodo,
            quantidadePendencias=resumo.quantidade_pendencias,
            quantidadeVencidas=resumo.quantidade_vencidas,
        )


class EstoqueResumoResponse(BaseModel):
    produtos_controlados: Optional[int] = Field(
        default=None, alias="produtosControlados"
    )
    produtos_com_estoque_baixo: int = Field(alias="produtosComEstoqueBaixo")
    produtos_com_estoque_negativo: int = Field(alias="produtosComEstoqueNegativo")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(
        cls,
        resumo: EstoqueResumo,
        incluir_controlados: bool = False,
    ) -> "EstoqueResumoResponse":
        return cls(
            produtosControlados=(
                resumo.produtos_controlados if incluir_controlados else None
            ),
            produtosComEstoqueBaixo=resumo.produtos_com_estoque_baixo,
            produtosComEstoqueNegativo=resumo.produtos_com_estoque_negativo,
        )


class ProdutoMaisVendidoResponse(BaseModel):
    produto_id: Optional[int] = Field(default=None, alias="produtoId")
    nome_produto: str = Field(alias="nomeProduto")
    quantidade_vendida: Decimal = Field(alias="quantidadeVendida")
    valor_total: Decimal = Field(alias="valorTotal")
    quantidade_comandas: Optional[int] = Field(default=None, alias="quantidadeComandas")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(
        cls,
        item: ProdutoMaisVendido,
        incluir_comandas: bool = True,
    ) -> "ProdutoMaisVendidoResponse":
        return cls(
            produtoId=item.produto_id,
            nomeProduto=item.nome_produto,
            quantidadeVendida=item.quantidade_vendida,
            valorTotal=item.valor_total,
            quantidadeComandas=(item.quantidade_comandas if incluir_comandas else None),
        )


class MovimentosCaixaResumoResponse(BaseModel):
    reforcos: Decimal
    sangrias: Decimal

    @classmethod
    def from_result(
        cls, resumo: MovimentosCaixaResumo
    ) -> "MovimentosCaixaResumoResponse":
        return cls(reforcos=resumo.reforcos, sangrias=resumo.sangrias)


class PendenciaRelatorioResponse(BaseModel):
    comanda_id: int = Field(alias="comandaId")
    cliente_id: Optional[int] = Field(default=None, alias="clienteId")
    nome_exibicao: str = Field(alias="nomeExibicao")
    total: Decimal
    pendente_em: Optional[datetime] = Field(default=None, alias="pendenteEm")
    vencimento_em: Optional[date] = Field(default=None, alias="vencimentoEm")
    vencida: bool

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, item: PendenciaRelatorio) -> "PendenciaRelatorioResponse":
        return cls(
            comandaId=item.comanda_id,
            clienteId=item.cliente_id,
            nomeExibicao=item.nome_exibicao,
            total=item.total,
            pendenteEm=item.pendente_em,
            vencimentoEm=item.vencimento_em,
            vencida=item.vencida,
        )


class ItemEstoqueRelatorioResponse(BaseModel):
    produto_id: int = Field(alias="produtoId")
    nome: str
    quantidade_estoque: Decimal = Field(alias="quantidadeEstoque")
    estoque_minimo: Decimal = Field(alias="estoqueMinimo")
    unidade_estoque: UnidadeEstoque = Field(alias="unidadeEstoque")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, item: ItemEstoqueRelatorio) -> "ItemEstoqueRelatorioResponse":
        return cls(
            produtoId=item.produto_id,
            nome=item.nome,
            quantidadeEstoque=item.quantidade_estoque,
            estoqueMinimo=item.estoque_minimo,
            unidadeEstoque=item.unidade_estoque,
        )


class EstoqueConsumidoResponse(BaseModel):
    produto_id: int = Field(alias="produtoId")
    nome: str
    quantidade_consumida: Decimal = Field(alias="quantidadeConsumida")
    unidade_estoque: UnidadeEstoque = Field(alias="unidadeEstoque")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, item: EstoqueConsumidoItem) -> "EstoqueConsumidoResponse":
        return cls(
            produtoId=item.produto_id,
            nome=item.nome,
            quantidadeConsumida=item.quantidade_consumida,
            unidadeEstoque=item.unidade_estoque,
        )


class ComandaPorStatusResponse(BaseModel):
    status: StatusComanda
    quantidade: int
    valor_total: Decimal = Field(alias="valorTotal")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, item: ComandaPorStatus) -> "ComandaPorStatusResponse":
        return cls(
            status=item.status,
            quantidade=item.quantidade,
            valorTotal=item.valor_total,
        )


class RelatorioDiarioResponse(BaseModel):
    data: date
    caixa: Optional[CaixaRelatorioResponse]
    vendas: VendasResumoResponse
    pagamentos: PagamentosResumoResponse
    comandas: ComandasResumoResponse
    fiados: FiadosDiarioResponse
    estoque: EstoqueResumoResponse

    @classmethod
    def from_result(cls, result: RelatorioDiario) -> "RelatorioDiarioResponse":
        return cls(
            data=result.data,
            caixa=(
                CaixaRelatorioResponse.from_result(result.caixa)
                if result.caixa is not None
                else None
            ),
            vendas=VendasResumoResponse.from_result(result.vendas),
            pagamentos=PagamentosResumoResponse.from_result(result.pagamentos),
            comandas=ComandasResumoResponse.from_result(result.comandas),
            fiados=FiadosDiarioResponse.from_result(result.fiados),
            estoque=EstoqueResumoResponse.from_result(result.estoque),
        )


class RelatorioCaixaResponse(BaseModel):
    caixa: CaixaRelatorioResponse
    pagamentos: PagamentosResumoResponse
    movimentos: MovimentosCaixaResumoResponse
    comandas: ComandasResumoResponse
    fiados: FiadosDiarioResponse
    produtos_mais_vendidos: list[ProdutoMaisVendidoResponse] = Field(
        alias="produtosMaisVendidos"
    )

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, result: RelatorioCaixa) -> "RelatorioCaixaResponse":
        return cls(
            caixa=CaixaRelatorioResponse.from_result(result.caixa, incluir_data=True),
            pagamentos=PagamentosResumoResponse.from_result(
                result.pagamentos,
                incluir_total=True,
            ),
            movimentos=MovimentosCaixaResumoResponse.from_result(result.movimentos),
            comandas=ComandasResumoResponse.from_result(
                result.comandas,
                incluir_total=True,
            ),
            fiados=FiadosDiarioResponse.from_result(result.fiados),
            produtosMaisVendidos=[
                ProdutoMaisVendidoResponse.from_result(item, incluir_comandas=False)
                for item in result.produtos_mais_vendidos
            ],
        )


class RelatorioFiadosResponse(BaseModel):
    resumo: FiadosResumoResponse
    pendencias: list[PendenciaRelatorioResponse]

    @classmethod
    def from_result(cls, result: RelatorioFiados) -> "RelatorioFiadosResponse":
        return cls(
            resumo=FiadosResumoResponse.from_result(result.resumo),
            pendencias=[
                PendenciaRelatorioResponse.from_result(item)
                for item in result.pendencias
            ],
        )


class RelatorioEstoqueResponse(BaseModel):
    resumo: EstoqueResumoResponse
    baixo: list[ItemEstoqueRelatorioResponse]
    negativo: list[ItemEstoqueRelatorioResponse]

    @classmethod
    def from_result(cls, result: RelatorioEstoque) -> "RelatorioEstoqueResponse":
        return cls(
            resumo=EstoqueResumoResponse.from_result(
                result.resumo,
                incluir_controlados=True,
            ),
            baixo=[
                ItemEstoqueRelatorioResponse.from_result(item) for item in result.baixo
            ],
            negativo=[
                ItemEstoqueRelatorioResponse.from_result(item)
                for item in result.negativo
            ],
        )


class RelatorioComandasResponse(BaseModel):
    resumo: ComandasResumoResponse
    por_status: list[ComandaPorStatusResponse] = Field(alias="porStatus")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_result(cls, result: RelatorioComandas) -> "RelatorioComandasResponse":
        return cls(
            resumo=ComandasResumoResponse.from_result(
                result.resumo,
                incluir_valores=True,
                incluir_total=True,
            ),
            porStatus=[
                ComandaPorStatusResponse.from_result(item) for item in result.por_status
            ],
        )
