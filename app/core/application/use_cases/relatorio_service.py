from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from core.domain.enums import (
    FormaPagamento,
    StatusCaixa,
    StatusComanda,
    TipoMovimentoCaixa,
    UnidadeEstoque,
)
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Caixa, Comanda, Pagamento, Produto
from core.interfaces.adapters.repositories.i_relatorio_repository import (
    IRelatorioRepository,
)

ZERO_MONEY = Decimal("0.00")
REAL_PAYMENT_FORMS = {
    FormaPagamento.DINHEIRO,
    FormaPagamento.PIX,
    FormaPagamento.CARTAO,
}
SALE_STATUSES = {StatusComanda.FECHADA, StatusComanda.PENDENTE}


@dataclass(frozen=True)
class CaixaRelatorio:
    id: int
    data: date
    status: StatusCaixa
    valor_inicial: Decimal
    dinheiro_esperado: Decimal
    dinheiro_informado: Optional[Decimal]
    diferenca: Optional[Decimal]
    aberto_em: datetime
    fechado_em: Optional[datetime]


@dataclass(frozen=True)
class PagamentosResumo:
    dinheiro: Decimal = ZERO_MONEY
    pix: Decimal = ZERO_MONEY
    cartao: Decimal = ZERO_MONEY
    total_recebido: Decimal = ZERO_MONEY


@dataclass(frozen=True)
class ComandasResumo:
    total: int = 0
    abertas: int = 0
    fechadas: int = 0
    pendentes: int = 0
    canceladas: int = 0
    valor_fechado: Decimal = ZERO_MONEY
    valor_pendente: Decimal = ZERO_MONEY
    valor_cancelado: Decimal = ZERO_MONEY


@dataclass(frozen=True)
class VendasResumo:
    total_vendido: Decimal = ZERO_MONEY
    total_recebido: Decimal = ZERO_MONEY
    total_fiado_gerado: Decimal = ZERO_MONEY
    total_pendente_atual: Decimal = ZERO_MONEY


@dataclass(frozen=True)
class FiadosResumo:
    gerados_no_dia: Decimal = ZERO_MONEY
    quitados_no_dia: Decimal = ZERO_MONEY
    pendentes_atuais: Decimal = ZERO_MONEY
    vencidos_atuais: Decimal = ZERO_MONEY
    total_pendente: Decimal = ZERO_MONEY
    total_vencido: Decimal = ZERO_MONEY
    total_quitado_periodo: Decimal = ZERO_MONEY
    quantidade_pendencias: int = 0
    quantidade_vencidas: int = 0


@dataclass(frozen=True)
class EstoqueResumo:
    produtos_controlados: int = 0
    produtos_com_estoque_baixo: int = 0
    produtos_com_estoque_negativo: int = 0


@dataclass(frozen=True)
class ProdutoMaisVendido:
    produto_id: Optional[int]
    nome_produto: str
    quantidade_vendida: Decimal
    valor_total: Decimal
    quantidade_comandas: int


@dataclass
class ProdutoVendaAgregado:
    produto_id: Optional[int]
    nome_produto: str
    quantidade_vendida: Decimal = ZERO_MONEY
    valor_total: Decimal = ZERO_MONEY
    comandas: set[Optional[int]] = field(default_factory=set)


@dataclass(frozen=True)
class ItemEstoqueRelatorio:
    produto_id: int
    nome: str
    quantidade_estoque: Decimal
    estoque_minimo: Decimal
    unidade_estoque: UnidadeEstoque


@dataclass(frozen=True)
class PendenciaRelatorio:
    comanda_id: int
    cliente_id: Optional[int]
    nome_exibicao: str
    total: Decimal
    pendente_em: Optional[datetime]
    vencimento_em: Optional[date]
    vencida: bool


@dataclass(frozen=True)
class ComandaPorStatus:
    status: StatusComanda
    quantidade: int
    valor_total: Decimal


@dataclass(frozen=True)
class MovimentosCaixaResumo:
    reforcos: Decimal = ZERO_MONEY
    sangrias: Decimal = ZERO_MONEY


@dataclass(frozen=True)
class RelatorioDiario:
    data: date
    caixa: Optional[CaixaRelatorio]
    vendas: VendasResumo
    pagamentos: PagamentosResumo
    comandas: ComandasResumo
    fiados: FiadosResumo
    estoque: EstoqueResumo


@dataclass(frozen=True)
class RelatorioCaixa:
    caixa: CaixaRelatorio
    pagamentos: PagamentosResumo
    movimentos: MovimentosCaixaResumo
    comandas: ComandasResumo
    fiados: FiadosResumo
    produtos_mais_vendidos: list[ProdutoMaisVendido] = field(default_factory=list)


@dataclass(frozen=True)
class RelatorioFiados:
    resumo: FiadosResumo
    pendencias: list[PendenciaRelatorio] = field(default_factory=list)


@dataclass(frozen=True)
class RelatorioEstoque:
    resumo: EstoqueResumo
    baixo: list[ItemEstoqueRelatorio] = field(default_factory=list)
    negativo: list[ItemEstoqueRelatorio] = field(default_factory=list)


@dataclass(frozen=True)
class RelatorioComandas:
    resumo: ComandasResumo
    por_status: list[ComandaPorStatus] = field(default_factory=list)


class RelatorioService:
    def __init__(self, relatorio_repository: IRelatorioRepository):
        self.relatorio_repository = relatorio_repository

    def relatorio_diario(self, data: Optional[date] = None) -> RelatorioDiario:
        data_relatorio = data or date.today()
        inicio, fim = self._periodo_dia(data_relatorio)
        caixa = self.relatorio_repository.get_caixa_by_data(data_relatorio)
        comandas_dia = self.relatorio_repository.list_comandas(
            data_inicio=data_relatorio,
            data_fim=data_relatorio,
        )
        comandas_fiado_dia = self._filtrar_pendencia_periodo(
            self.relatorio_repository.list_comandas(),
            data_relatorio,
            data_relatorio,
        )
        pagamentos_dia = self.relatorio_repository.list_pagamentos(inicio, fim)
        pendentes_atuais = self.relatorio_repository.list_comandas(
            status=StatusComanda.PENDENTE
        )
        produtos = self.relatorio_repository.list_produtos_controlados()

        pagamentos = self._resumir_pagamentos(pagamentos_dia)
        fiados = self._resumir_fiados(
            comandas=comandas_fiado_dia,
            pagamentos=pagamentos_dia,
            pendentes_atuais=pendentes_atuais,
            hoje=data_relatorio,
        )
        return RelatorioDiario(
            data=data_relatorio,
            caixa=self._caixa_response(caixa) if caixa is not None else None,
            vendas=VendasResumo(
                total_vendido=self._total_vendido(comandas_dia),
                total_recebido=pagamentos.total_recebido,
                total_fiado_gerado=fiados.gerados_no_dia,
                total_pendente_atual=fiados.pendentes_atuais,
            ),
            pagamentos=pagamentos,
            comandas=self._resumir_comandas(comandas_dia),
            fiados=fiados,
            estoque=self._resumir_estoque(produtos),
        )

    def relatorio_caixa(self, caixa_id: int) -> RelatorioCaixa:
        caixa = self.relatorio_repository.get_caixa_by_id(caixa_id)
        if caixa is None:
            raise NotFoundError("caixa_nao_encontrado", "Caixa não encontrado")

        comandas = self.relatorio_repository.list_comandas(caixa_origem_id=caixa_id)
        pagamentos = self.relatorio_repository.list_pagamentos(caixa_id=caixa_id)
        return RelatorioCaixa(
            caixa=self._caixa_response(caixa),
            pagamentos=self._resumir_pagamentos(pagamentos),
            movimentos=MovimentosCaixaResumo(
                reforcos=sum(
                    (
                        movimento.valor
                        for movimento in caixa.movimentos
                        if movimento.tipo == TipoMovimentoCaixa.REFORCO
                    ),
                    ZERO_MONEY,
                ),
                sangrias=sum(
                    (
                        movimento.valor
                        for movimento in caixa.movimentos
                        if movimento.tipo == TipoMovimentoCaixa.SANGRIA
                    ),
                    ZERO_MONEY,
                ),
            ),
            comandas=self._resumir_comandas(comandas),
            fiados=FiadosResumo(
                gerados_no_dia=self._total_fiado_gerado(comandas),
                quitados_no_dia=self._total_fiado_quitado(pagamentos),
            ),
            produtos_mais_vendidos=self._produtos_mais_vendidos(comandas, 10),
        )

    def produtos_mais_vendidos(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        limite: int = 10,
    ) -> list[ProdutoMaisVendido]:
        self._ensure_periodo_valido(data_inicio, data_fim)
        if limite <= 0 or limite > 100:
            raise ApplicationError(
                "parametro_invalido",
                "Limite deve estar entre 1 e 100",
                400,
            )
        comandas = self.relatorio_repository.list_comandas(
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
        return self._produtos_mais_vendidos(comandas, limite)

    def relatorio_fiados(
        self,
        status: str = "todos",
        cliente_id: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> RelatorioFiados:
        self._ensure_periodo_valido(data_inicio, data_fim)
        if status not in {"pendentes", "vencidos", "quitados", "todos"}:
            raise ApplicationError("parametro_invalido", "Status inválido", 400)

        hoje = date.today()
        comandas_periodo = self._filtrar_pendencia_periodo(
            self.relatorio_repository.list_comandas(),
            data_inicio,
            data_fim,
        )
        pagamentos_periodo = self._pagamentos_periodo(data_inicio, data_fim)
        pendentes = [
            comanda
            for comanda in self.relatorio_repository.list_comandas(
                status=StatusComanda.PENDENTE
            )
            if self._match_cliente(comanda, cliente_id)
        ]
        pendencias_filtradas = [
            comanda
            for comanda in pendentes
            if self._match_periodo_pendencia(comanda, data_inicio, data_fim)
            and (
                status in {"pendentes", "todos"}
                or (
                    status == "vencidos"
                    and comanda.vencimento_em is not None
                    and comanda.vencimento_em < hoje
                )
            )
        ]
        if status == "vencidos":
            pendencias_filtradas = [
                comanda
                for comanda in pendencias_filtradas
                if comanda.vencimento_em is not None and comanda.vencimento_em < hoje
            ]
        if status == "quitados":
            pendencias_filtradas = []

        resumo = self._resumir_fiados(
            comandas=[
                comanda
                for comanda in comandas_periodo
                if self._match_cliente(comanda, cliente_id)
            ],
            pagamentos=[
                pagamento
                for pagamento in pagamentos_periodo
                if pagamento.comanda is not None
                and self._match_cliente(pagamento.comanda, cliente_id)
            ],
            pendentes_atuais=pendentes,
            hoje=hoje,
        )
        return RelatorioFiados(
            resumo=resumo,
            pendencias=[
                self._pendencia_response(comanda, hoje)
                for comanda in pendencias_filtradas
            ],
        )

    def relatorio_estoque(self, tipo: str = "todos") -> RelatorioEstoque:
        if tipo not in {"baixo", "negativo", "todos"}:
            raise ApplicationError("parametro_invalido", "Tipo inválido", 400)
        produtos = self.relatorio_repository.list_produtos_controlados()
        baixo = [produto for produto in produtos if self._is_estoque_baixo(produto)]
        negativo = [produto for produto in produtos if produto.quantidade_estoque < 0]
        return RelatorioEstoque(
            resumo=self._resumir_estoque(produtos),
            baixo=(
                []
                if tipo == "negativo"
                else [self._estoque_item(item) for item in baixo]
            ),
            negativo=(
                []
                if tipo == "baixo"
                else [self._estoque_item(item) for item in negativo]
            ),
        )

    def relatorio_comandas(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[StatusComanda] = None,
    ) -> RelatorioComandas:
        self._ensure_periodo_valido(data_inicio, data_fim)
        comandas = self.relatorio_repository.list_comandas(
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
        )
        resumo = self._resumir_comandas(comandas)
        por_status = []
        for status_comanda in StatusComanda:
            filtradas = [
                comanda for comanda in comandas if comanda.status == status_comanda
            ]
            if filtradas:
                por_status.append(
                    ComandaPorStatus(
                        status=status_comanda,
                        quantidade=len(filtradas),
                        valor_total=sum(
                            (comanda.total for comanda in filtradas), ZERO_MONEY
                        ),
                    )
                )
        return RelatorioComandas(resumo=resumo, por_status=por_status)

    def _pagamentos_periodo(
        self,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> list[Pagamento]:
        inicio = datetime.combine(data_inicio, time.min) if data_inicio else None
        fim = datetime.combine(data_fim, time.max) if data_fim else None
        return self.relatorio_repository.list_pagamentos(inicio, fim)

    @staticmethod
    def _periodo_dia(data_relatorio: date) -> tuple[datetime, datetime]:
        return (
            datetime.combine(data_relatorio, time.min),
            datetime.combine(data_relatorio, time.max),
        )

    @staticmethod
    def _ensure_periodo_valido(
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> None:
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ApplicationError(
                "periodo_invalido",
                "Data inicial não pode ser maior que data final",
                400,
            )

    @staticmethod
    def _caixa_response(caixa: Caixa) -> CaixaRelatorio:
        if caixa.id is None:
            raise ApplicationError("dados_invalidos", "Caixa inválido", 400)
        return CaixaRelatorio(
            id=caixa.id,
            data=caixa.data,
            status=caixa.status,
            valor_inicial=caixa.valor_inicial,
            dinheiro_esperado=caixa.dinheiro_esperado,
            dinheiro_informado=caixa.dinheiro_informado,
            diferenca=caixa.diferenca,
            aberto_em=caixa.aberto_em,
            fechado_em=caixa.fechado_em,
        )

    @staticmethod
    def _resumir_pagamentos(pagamentos: list[Pagamento]) -> PagamentosResumo:
        dinheiro = sum(
            (
                pagamento.valor
                for pagamento in pagamentos
                if pagamento.forma_pagamento == FormaPagamento.DINHEIRO
            ),
            ZERO_MONEY,
        )
        pix = sum(
            (
                pagamento.valor
                for pagamento in pagamentos
                if pagamento.forma_pagamento == FormaPagamento.PIX
            ),
            ZERO_MONEY,
        )
        cartao = sum(
            (
                pagamento.valor
                for pagamento in pagamentos
                if pagamento.forma_pagamento == FormaPagamento.CARTAO
            ),
            ZERO_MONEY,
        )
        return PagamentosResumo(
            dinheiro=dinheiro,
            pix=pix,
            cartao=cartao,
            total_recebido=dinheiro + pix + cartao,
        )

    @staticmethod
    def _resumir_comandas(comandas: list[Comanda]) -> ComandasResumo:
        abertas = [item for item in comandas if item.status == StatusComanda.ABERTA]
        fechadas = [item for item in comandas if item.status == StatusComanda.FECHADA]
        pendentes = [item for item in comandas if item.status == StatusComanda.PENDENTE]
        canceladas = [
            item for item in comandas if item.status == StatusComanda.CANCELADA
        ]
        return ComandasResumo(
            total=len(comandas),
            abertas=len(abertas),
            fechadas=len(fechadas),
            pendentes=len(pendentes),
            canceladas=len(canceladas),
            valor_fechado=sum((item.total for item in fechadas), ZERO_MONEY),
            valor_pendente=sum((item.total for item in pendentes), ZERO_MONEY),
            valor_cancelado=sum((item.total for item in canceladas), ZERO_MONEY),
        )

    @staticmethod
    def _total_vendido(comandas: list[Comanda]) -> Decimal:
        return sum(
            (comanda.total for comanda in comandas if comanda.status in SALE_STATUSES),
            ZERO_MONEY,
        )

    @staticmethod
    def _total_fiado_gerado(comandas: list[Comanda]) -> Decimal:
        return sum(
            (
                comanda.total
                for comanda in comandas
                if comanda.status == StatusComanda.PENDENTE
                and comanda.pendente_em is not None
            ),
            ZERO_MONEY,
        )

    @staticmethod
    def _total_fiado_quitado(pagamentos: list[Pagamento]) -> Decimal:
        return sum(
            (
                pagamento.valor
                for pagamento in pagamentos
                if pagamento.forma_pagamento in REAL_PAYMENT_FORMS
                and pagamento.comanda is not None
                and pagamento.comanda.pendente_em is not None
            ),
            ZERO_MONEY,
        )

    def _resumir_fiados(
        self,
        comandas: list[Comanda],
        pagamentos: list[Pagamento],
        pendentes_atuais: list[Comanda],
        hoje: date,
    ) -> FiadosResumo:
        vencidas = [
            comanda
            for comanda in pendentes_atuais
            if comanda.vencimento_em is not None and comanda.vencimento_em < hoje
        ]
        total_pendente = sum(
            (comanda.total for comanda in pendentes_atuais), ZERO_MONEY
        )
        total_vencido = sum((comanda.total for comanda in vencidas), ZERO_MONEY)
        quitado = self._total_fiado_quitado(pagamentos)
        return FiadosResumo(
            gerados_no_dia=self._total_fiado_gerado(comandas),
            quitados_no_dia=quitado,
            pendentes_atuais=total_pendente,
            vencidos_atuais=total_vencido,
            total_pendente=total_pendente,
            total_vencido=total_vencido,
            total_quitado_periodo=quitado,
            quantidade_pendencias=len(pendentes_atuais),
            quantidade_vencidas=len(vencidas),
        )

    @staticmethod
    def _resumir_estoque(produtos: list[Produto]) -> EstoqueResumo:
        baixo = [
            produto
            for produto in produtos
            if RelatorioService._is_estoque_baixo(produto)
        ]
        negativo = [produto for produto in produtos if produto.quantidade_estoque < 0]
        return EstoqueResumo(
            produtos_controlados=len(produtos),
            produtos_com_estoque_baixo=len(baixo),
            produtos_com_estoque_negativo=len(negativo),
        )

    @staticmethod
    def _is_estoque_baixo(produto: Produto) -> bool:
        return (
            produto.quantidade_estoque <= produto.estoque_minimo
            and produto.quantidade_estoque >= 0
        )

    @staticmethod
    def _estoque_item(produto: Produto) -> ItemEstoqueRelatorio:
        if produto.id is None:
            raise ApplicationError("dados_invalidos", "Produto inválido", 400)
        return ItemEstoqueRelatorio(
            produto_id=produto.id,
            nome=produto.nome,
            quantidade_estoque=produto.quantidade_estoque,
            estoque_minimo=produto.estoque_minimo,
            unidade_estoque=produto.unidade_estoque,
        )

    @staticmethod
    def _pendencia_response(comanda: Comanda, hoje: date) -> PendenciaRelatorio:
        if comanda.id is None:
            raise ApplicationError("dados_invalidos", "Comanda inválida", 400)
        nome_exibicao = comanda.nome_cliente
        if comanda.cliente is not None:
            nome_exibicao = comanda.cliente.apelido or comanda.cliente.nome
        return PendenciaRelatorio(
            comanda_id=comanda.id,
            cliente_id=comanda.cliente_id,
            nome_exibicao=nome_exibicao,
            total=comanda.total,
            pendente_em=comanda.pendente_em,
            vencimento_em=comanda.vencimento_em,
            vencida=(
                comanda.vencimento_em is not None and comanda.vencimento_em < hoje
            ),
        )

    @staticmethod
    def _match_cliente(comanda: Comanda, cliente_id: Optional[int]) -> bool:
        return cliente_id is None or comanda.cliente_id == cliente_id

    @staticmethod
    def _match_periodo_pendencia(
        comanda: Comanda,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> bool:
        referencia = comanda.pendente_em or comanda.aberta_em
        if data_inicio is not None and referencia.date() < data_inicio:
            return False
        if data_fim is not None and referencia.date() > data_fim:
            return False
        return True

    @staticmethod
    def _filtrar_pendencia_periodo(
        comandas: list[Comanda],
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> list[Comanda]:
        return [
            comanda
            for comanda in comandas
            if RelatorioService._match_periodo_pendencia(
                comanda,
                data_inicio,
                data_fim,
            )
        ]

    @staticmethod
    def _produtos_mais_vendidos(
        comandas: list[Comanda],
        limite: int,
    ) -> list[ProdutoMaisVendido]:
        agregados: dict[tuple[Optional[int], str], ProdutoVendaAgregado] = {}
        for comanda in comandas:
            if comanda.status not in SALE_STATUSES:
                continue
            for item in comanda.itens:
                chave = (
                    item.produto_id,
                    item.nome_produto_snapshot if item.produto_id is None else "",
                )
                atual = agregados.setdefault(
                    chave,
                    ProdutoVendaAgregado(
                        produto_id=item.produto_id,
                        nome_produto=item.nome_produto_snapshot,
                    ),
                )
                atual.quantidade_vendida += item.quantidade
                atual.valor_total += item.total_item
                atual.comandas.add(comanda.id)

        produtos = [
            ProdutoMaisVendido(
                produto_id=valor.produto_id,
                nome_produto=valor.nome_produto,
                quantidade_vendida=valor.quantidade_vendida,
                valor_total=valor.valor_total,
                quantidade_comandas=len(valor.comandas),
            )
            for valor in agregados.values()
        ]
        return sorted(
            produtos,
            key=lambda item: (item.quantidade_vendida, item.valor_total),
            reverse=True,
        )[:limite]
