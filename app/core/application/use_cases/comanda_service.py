from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from core.application.use_cases.cliente_service import ClienteService
from core.application.use_cases.estoque_service import EstoqueService
from core.domain.enums import OrigemMovimentoEstoque, StatusComanda
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Cliente, Comanda, ItemComanda, Produto
from core.interfaces.adapters.repositories.i_caixa_repository import ICaixaRepository
from core.interfaces.adapters.repositories.i_cliente_repository import (
    IClienteRepository,
)
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)
from core.interfaces.adapters.repositories.i_produto_repository import (
    IProdutoRepository,
)


class ComandaService:
    def __init__(
        self,
        comanda_repository: IComandaRepository,
        produto_repository: IProdutoRepository,
        estoque_service: EstoqueService,
        cliente_repository: IClienteRepository,
        caixa_repository: ICaixaRepository,
    ):
        self.comanda_repository = comanda_repository
        self.produto_repository = produto_repository
        self.estoque_service = estoque_service
        self.cliente_repository = cliente_repository
        self.caixa_repository = caixa_repository

    def create(
        self,
        nome_cliente: Optional[str] = None,
        observacao: Optional[str] = None,
        cliente_id: Optional[int] = None,
    ) -> Comanda:
        now = datetime.now()
        caixa = self.caixa_repository.get_aberto()
        if caixa is None:
            raise ApplicationError(
                "caixa_aberto_nao_encontrado",
                "Nenhum caixa aberto encontrado",
                400,
            )
        cliente = (
            self._get_cliente_ativo(cliente_id) if cliente_id is not None else None
        )
        nome_operacional = self._resolve_nome_cliente(nome_cliente, cliente)
        comanda = Comanda(
            caixa_origem_id=caixa.id,
            cliente_id=cliente.id if cliente is not None else None,
            nome_cliente=nome_operacional,
            nome_cliente_snapshot=(
                ClienteService.nome_operacional(cliente)
                if cliente is not None
                else None
            ),
            status=StatusComanda.ABERTA,
            total=Decimal("0.00"),
            aberta_em=now,
            observacao=observacao,
            criado_em=now,
            atualizado_em=now,
        )

        try:
            self.comanda_repository.create(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return comanda

    def vincular_cliente(self, comanda_id: int, cliente_id: int) -> Comanda:
        try:
            comanda = self._get_comanda_aberta(comanda_id)
            cliente = self._get_cliente_ativo(cliente_id)
            comanda.cliente_id = cliente.id
            comanda.nome_cliente_snapshot = ClienteService.nome_operacional(cliente)
            comanda.atualizado_em = datetime.now()
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def listar(
        self,
        status: Optional[StatusComanda] = None,
        nome: Optional[str] = None,
        data: Optional[date] = None,
    ) -> list[Comanda]:
        return self.comanda_repository.list(status=status, nome=nome, data=data)

    def list_abertas(self) -> list[Comanda]:
        return self.listar(status=StatusComanda.ABERTA)

    def get_by_id(self, comanda_id: int) -> Comanda:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if comanda is None:
            raise NotFoundError(
                code="comanda_nao_encontrada",
                message="Comanda não encontrada",
            )
        return comanda

    def adicionar_item(
        self,
        comanda_id: int,
        produto_id: int,
        quantidade: Decimal,
    ) -> Comanda:
        self._ensure_quantidade_positiva(quantidade)

        try:
            comanda = self._get_comanda_aberta(comanda_id)
            produto = self._get_produto_ativo(produto_id)
            item = self.comanda_repository.get_item_by_comanda_produto(
                comanda_id=comanda_id,
                produto_id=produto_id,
            )

            if item is None:
                item = self._criar_item(comanda=comanda, produto=produto)

            self._aumentar_item(item=item, produto=produto, quantidade=quantidade)
            self._recalcular_total(comanda)
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def incrementar_item(
        self,
        comanda_id: int,
        item_id: int,
        quantidade: Decimal,
    ) -> Comanda:
        self._ensure_quantidade_positiva(quantidade)

        try:
            comanda = self._get_comanda_aberta(comanda_id)
            item = self._get_item_da_comanda(comanda_id, item_id)
            produto = self._get_produto_ativo(item.produto_id)
            self._aumentar_item(item=item, produto=produto, quantidade=quantidade)
            self._recalcular_total(comanda)
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def diminuir_item(
        self,
        comanda_id: int,
        item_id: int,
        quantidade: Decimal,
    ) -> Comanda:
        self._ensure_quantidade_positiva(quantidade)

        try:
            comanda = self._get_comanda_aberta(comanda_id)
            item = self._get_item_da_comanda(comanda_id, item_id)
            produto = self._get_produto_para_estoque(item.produto_id)

            if quantidade >= item.quantidade:
                self._remover_item(comanda=comanda, item=item, produto=produto)
            else:
                self._diminuir_item(item=item, produto=produto, quantidade=quantidade)

            self._recalcular_total(comanda)
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def remover_item(self, comanda_id: int, item_id: int) -> Comanda:
        try:
            comanda = self._get_comanda_aberta(comanda_id)
            item = self._get_item_da_comanda(comanda_id, item_id)
            produto = self._get_produto_para_estoque(item.produto_id)
            self._remover_item(comanda=comanda, item=item, produto=produto)
            self._recalcular_total(comanda)
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def cancelar(self, comanda_id: int, motivo: Optional[str] = None) -> Comanda:
        try:
            comanda = self._get_comanda_aberta(comanda_id)
            for item in list(comanda.itens):
                produto = self._get_produto_para_estoque(item.produto_id)
                if produto.controla_estoque and item.quantidade_baixada_estoque > 0:
                    self.estoque_service.devolver_por_cancelamento(
                        produto=produto,
                        quantidade_devolvida=item.quantidade_baixada_estoque,
                        referencia_id=item.id,
                        origem=OrigemMovimentoEstoque.CANCELAMENTO,
                        observacao="Cancelamento de comanda",
                    )

            now = datetime.now()
            comanda.status = StatusComanda.CANCELADA
            comanda.cancelada_em = now
            comanda.observacao = motivo if motivo is not None else comanda.observacao
            comanda.atualizado_em = now
            self._recalcular_total(comanda)
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self.get_by_id(comanda_id)

    def _criar_item(self, comanda: Comanda, produto: Produto) -> ItemComanda:
        comanda_id = self._get_comanda_id(comanda)
        produto_id = self._get_produto_id(produto)
        now = datetime.now()
        item = ItemComanda(
            comanda_id=comanda_id,
            produto_id=produto_id,
            nome_produto_snapshot=produto.nome,
            preco_unitario_snapshot=produto.preco_venda,
            quantidade=Decimal("0"),
            quantidade_baixada_estoque=Decimal("0"),
            total_item=Decimal("0.00"),
            criado_em=now,
            atualizado_em=now,
        )
        self.comanda_repository.save_item(item)
        comanda.itens.append(item)
        return item

    def _aumentar_item(
        self,
        item: ItemComanda,
        produto: Produto,
        quantidade: Decimal,
    ) -> None:
        quantidade_baixada = self._calcular_quantidade_baixada(produto, quantidade)
        item.quantidade += quantidade
        item.quantidade_baixada_estoque += quantidade_baixada
        self._atualizar_total_item(item)

        if produto.controla_estoque and quantidade_baixada > 0:
            self.estoque_service.baixar_por_venda(
                produto=produto,
                quantidade_baixada=quantidade_baixada,
                referencia_id=item.id,
                observacao="Baixa por comanda",
            )

    def _diminuir_item(
        self,
        item: ItemComanda,
        produto: Produto,
        quantidade: Decimal,
    ) -> None:
        quantidade_devolvida = self._calcular_quantidade_baixada(produto, quantidade)
        item.quantidade -= quantidade
        item.quantidade_baixada_estoque -= quantidade_devolvida
        self._atualizar_total_item(item)

        if produto.controla_estoque and quantidade_devolvida > 0:
            self.estoque_service.devolver_por_cancelamento(
                produto=produto,
                quantidade_devolvida=quantidade_devolvida,
                referencia_id=item.id,
                origem=OrigemMovimentoEstoque.COMANDA,
                observacao="Devolução por redução de item da comanda",
            )

    def _remover_item(
        self,
        comanda: Comanda,
        item: ItemComanda,
        produto: Produto,
    ) -> None:
        if produto.controla_estoque and item.quantidade_baixada_estoque > 0:
            self.estoque_service.devolver_por_cancelamento(
                produto=produto,
                quantidade_devolvida=item.quantidade_baixada_estoque,
                referencia_id=item.id,
                origem=OrigemMovimentoEstoque.COMANDA,
                observacao="Devolução por remoção de item da comanda",
            )
        item.total_item = Decimal("0.00")
        if item in comanda.itens:
            comanda.itens.remove(item)
        self.comanda_repository.delete_item(item)

    def _recalcular_total(self, comanda: Comanda) -> None:
        comanda.total = sum(
            (item.total_item for item in comanda.itens if item.id is not None),
            Decimal("0.00"),
        )
        comanda.atualizado_em = datetime.now()

    @staticmethod
    def _atualizar_total_item(item: ItemComanda) -> None:
        item.total_item = item.quantidade * item.preco_unitario_snapshot
        item.atualizado_em = datetime.now()

    @staticmethod
    def _calcular_quantidade_baixada(
        produto: Produto,
        quantidade: Decimal,
    ) -> Decimal:
        if not produto.controla_estoque:
            return Decimal("0")
        return produto.quantidade_baixa_por_venda * quantidade

    def _get_comanda_aberta(self, comanda_id: int) -> Comanda:
        comanda = self.get_by_id(comanda_id)
        if comanda.status != StatusComanda.ABERTA:
            raise ApplicationError(
                code="comanda_nao_aberta",
                message="Comanda não está aberta",
                status_code=400,
            )
        return comanda

    def _get_produto_ativo(self, produto_id: Optional[int]) -> Produto:
        produto = self._get_produto_para_estoque(produto_id)
        if not produto.ativo:
            raise ApplicationError(
                code="produto_inativo",
                message="Produto inativo",
                status_code=400,
            )
        return produto

    def _get_cliente_ativo(self, cliente_id: int) -> Cliente:
        cliente = self.cliente_repository.get_by_id(cliente_id)
        if cliente is None:
            raise NotFoundError(
                code="cliente_nao_encontrado",
                message="Cliente não encontrado",
            )
        ClienteService.ensure_ativo(cliente)
        return cliente

    @staticmethod
    def _resolve_nome_cliente(
        nome_cliente: Optional[str],
        cliente: Optional[Cliente],
    ) -> str:
        if nome_cliente is not None:
            nome = nome_cliente.strip()
            if nome:
                return nome

        if cliente is not None:
            return ClienteService.nome_operacional(cliente)

        raise ApplicationError("dados_invalidos", "Nome obrigatório", 400)

    def _get_produto_para_estoque(self, produto_id: Optional[int]) -> Produto:
        if produto_id is None:
            raise NotFoundError(
                code="produto_nao_encontrado",
                message="Produto não encontrado",
            )

        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(
                code="produto_nao_encontrado",
                message="Produto não encontrado",
            )
        return produto

    def _get_item_da_comanda(self, comanda_id: int, item_id: int) -> ItemComanda:
        item = self.comanda_repository.get_item_by_id(item_id)
        if item is None:
            raise NotFoundError(
                code="item_comanda_nao_encontrado",
                message="Item da comanda não encontrado",
            )

        if item.comanda_id != comanda_id:
            raise ApplicationError(
                code="item_nao_pertence_comanda",
                message="Item não pertence à comanda",
                status_code=400,
            )

        return item

    @staticmethod
    def _ensure_quantidade_positiva(quantidade: Decimal) -> None:
        if quantidade <= Decimal("0"):
            raise ApplicationError(
                code="quantidade_invalida",
                message="Quantidade inválida",
                status_code=400,
            )

    @staticmethod
    def _get_comanda_id(comanda: Comanda) -> int:
        if comanda.id is None:
            raise ApplicationError(
                code="dados_invalidos",
                message="Comanda inválida",
                status_code=400,
            )
        return comanda.id

    @staticmethod
    def _get_produto_id(produto: Produto) -> int:
        if produto.id is None:
            raise ApplicationError(
                code="dados_invalidos",
                message="Produto inválido",
                status_code=400,
            )
        return produto.id
