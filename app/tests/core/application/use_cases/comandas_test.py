from decimal import Decimal

import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, select

from adapter.dtos.comanda_dto import (
    AjusteComandaResponse,
    AplicarAjusteComandaRequest,
    ComandaDetalheResponse,
)
from adapter.repositories.comanda_repository import ComandaRepository
from api import create_app
from core.application.use_cases.ajuste_comanda_service import AjusteComandaService
from core.domain.enums import FormaPagamento, TipoAjusteComanda, TipoMovimentoEstoque
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import (
    AjusteComanda,
    Comanda,
    ItemComanda,
    MovimentoEstoque,
    Pagamento,
    Produto,
)


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    client = TestClient(app)
    response = client.post("/api/caixas/abrir", json={"valorInicial": 100})
    assert response.status_code == 201
    return client


def build_client_sem_caixa(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def create_categoria(client: TestClient, nome: str = "Cervejas") -> dict:
    response = client.post("/api/categorias", json={"nome": nome})
    assert response.status_code == 201
    return response.json()


def create_produto(
    client: TestClient,
    categoria_id: int,
    nome: str = "Cerveja lata",
    preco_venda: float = 7.0,
    controla_estoque: bool = True,
    unidade_estoque: str = "UNIDADE",
    quantidade_estoque: float = 24,
    quantidade_baixa_por_venda: float = 1,
    estoque_minimo: float = 6,
    tipo_produto: str = "SIMPLES",
) -> dict:
    payload = {
        "nome": nome,
        "categoriaId": categoria_id,
        "precoVenda": preco_venda,
        "tipoProduto": tipo_produto,
        "controlaEstoque": controla_estoque,
    }
    if controla_estoque:
        payload |= {
            "unidadeEstoque": unidade_estoque,
            "quantidadeEstoque": quantidade_estoque,
            "quantidadeBaixaPorVenda": quantidade_baixa_por_venda,
            "estoqueMinimo": estoque_minimo,
        }

    response = client.post("/api/produtos", json=payload)
    assert response.status_code == 201
    return response.json()


def add_componente(
    client: TestClient,
    produto_pai_id: int,
    produto_componente_id: int,
    quantidade_baixa: float = 50,
) -> dict:
    response = client.post(
        f"/api/produtos/{produto_pai_id}/composicao/componentes",
        json={
            "produtoComponenteId": produto_componente_id,
            "quantidadeBaixa": quantidade_baixa,
        },
    )
    assert response.status_code == 201
    return response.json()


def get_produto(test_engine, produto_id: int) -> Produto:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        return produto


def count_movimentos(test_engine, produto_id: int) -> int:
    with Session(test_engine) as session:
        statement = select(MovimentoEstoque).where(
            MovimentoEstoque.produto_id == produto_id
        )
        return len(session.exec(statement).all())


def list_movimentos(test_engine, produto_id: int) -> list[MovimentoEstoque]:
    with Session(test_engine) as session:
        statement = (
            select(MovimentoEstoque)
            .where(MovimentoEstoque.produto_id == produto_id)
            .order_by(text("id"))
        )
        return list(session.exec(statement).all())


def set_produto_ativo(test_engine, produto_id: int, ativo: bool) -> None:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        produto.ativo = ativo
        session.add(produto)
        session.commit()


def set_produto_controla_estoque(
    test_engine,
    produto_id: int,
    controla_estoque: bool,
) -> None:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        produto.controla_estoque = controla_estoque
        session.add(produto)
        session.commit()


def test_tipo_ajuste_comanda_deve_possuir_acrescimo_e_desconto():
    # Arrange / Act
    valores = {membro.value for membro in TipoAjusteComanda}

    # Assert
    assert valores == {"ACRESCIMO", "DESCONTO"}


def test_cria_comanda_valida_e_permite_nome_repetido(test_engine):
    client = build_client(test_engine)

    primeira = client.post(
        "/api/comandas",
        json={"nomeCliente": "João", "observacao": "Cliente voltou mais tarde"},
    )
    segunda = client.post("/api/comandas", json={"nomeCliente": "João"})

    assert primeira.status_code == 201
    assert segunda.status_code == 201
    body = primeira.json()
    assert body["nomeCliente"] == "João"
    assert body["status"] == "ABERTA"
    assert body["total"] == 0.0
    assert body["observacao"] == "Cliente voltou mais tarde"
    assert body["itens"] == []
    assert body["abertaEm"] is not None
    assert body["fechadaEm"] is None
    assert body["canceladaEm"] is None

    list_response = client.get("/api/comandas?nome=joão&status=ABERTA")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2


def test_deve_rejeitar_criar_comanda_sem_caixa_aberto(test_engine):
    client = build_client_sem_caixa(test_engine)

    response = client.post("/api/comandas", json={"nomeCliente": "João"})

    assert response.status_code == 400
    assert response.json()["code"] == "caixa_aberto_nao_encontrado"


def test_cria_comanda_rejeita_nome_vazio_ou_nulo(test_engine):
    client = build_client(test_engine)

    vazio = client.post("/api/comandas", json={"nomeCliente": "   "})
    nulo = client.post("/api/comandas", json={"nomeCliente": None})

    assert vazio.status_code == 422
    assert vazio.json()["code"] == "dados_invalidos"
    assert nulo.status_code == 422
    assert nulo.json()["code"] == "dados_invalidos"


def test_lista_consulta_e_filtra_comandas(test_engine):
    client = build_client(test_engine)
    joao = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    maria = client.post("/api/comandas", json={"nomeCliente": "Maria"}).json()
    client.patch(f"/api/comandas/{maria['id']}/cancelar")

    abertas = client.get("/api/comandas/abertas")
    assert abertas.status_code == 200
    assert [item["id"] for item in abertas.json()] == [joao["id"]]

    detalhe = client.get(f"/api/comandas/{joao['id']}")
    assert detalhe.status_code == 200
    assert detalhe.json()["id"] == joao["id"]

    status_response = client.get("/api/comandas?status=CANCELADA")
    assert status_response.status_code == 200
    assert [item["id"] for item in status_response.json()] == [maria["id"]]

    data = joao["abertaEm"][:10]
    data_response = client.get(f"/api/comandas?data={data}")
    assert data_response.status_code == 200
    assert {item["id"] for item in data_response.json()} == {joao["id"], maria["id"]}

    inexistente = client.get("/api/comandas/999")
    assert inexistente.status_code == 404
    assert inexistente.json()["code"] == "comanda_nao_encontrada"


def test_adiciona_produtos_recalcula_total_snapshot_e_movimenta_estoque(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    cerveja = create_produto(client, categoria["id"])
    dose = create_produto(
        client,
        categoria["id"],
        nome="Dose de pinga",
        preco_venda=5,
        unidade_estoque="ML",
        quantidade_estoque=1000,
        quantidade_baixa_por_venda=50,
        estoque_minimo=200,
    )
    taxa = create_produto(
        client,
        categoria["id"],
        nome="Taxa de serviço",
        preco_venda=2,
        controla_estoque=False,
    )
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    cerveja_response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": cerveja["id"], "quantidade": 3},
    )
    assert cerveja_response.status_code == 200
    body = cerveja_response.json()
    item_cerveja = body["itens"][0]
    assert body["total"] == 21.0
    assert item_cerveja["nomeProduto"] == "Cerveja lata"
    assert item_cerveja["precoUnitario"] == 7.0
    assert item_cerveja["quantidadeBaixadaEstoque"] == 3.0
    assert get_produto(test_engine, cerveja["id"]).quantidade_estoque == Decimal(
        "21.000"
    )

    ml_response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": dose["id"], "quantidade": 2},
    )
    assert ml_response.status_code == 200
    item_dose = [
        item for item in ml_response.json()["itens"] if item["produtoId"] == dose["id"]
    ][0]
    assert item_dose["quantidadeBaixadaEstoque"] == 100.0
    assert get_produto(test_engine, dose["id"]).quantidade_estoque == Decimal("900.000")

    sem_estoque_response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": taxa["id"], "quantidade": 2},
    )
    assert sem_estoque_response.status_code == 200
    assert count_movimentos(test_engine, taxa["id"]) == 0

    client.put(
        f"/api/produtos/{cerveja['id']}",
        json={
            "nome": "Cerveja long neck",
            "categoriaId": categoria["id"],
            "precoVenda": 9.5,
            "controlaEstoque": True,
            "unidadeEstoque": "UNIDADE",
            "quantidadeEstoque": 21,
            "quantidadeBaixaPorVenda": 1,
            "estoqueMinimo": 6,
        },
    )
    detalhe = client.get(f"/api/comandas/{comanda['id']}").json()
    snapshot = [
        item for item in detalhe["itens"] if item["produtoId"] == cerveja["id"]
    ][0]
    assert snapshot["nomeProduto"] == "Cerveja lata"
    assert snapshot["precoUnitario"] == 7.0

    movimentos = list_movimentos(test_engine, cerveja["id"])
    assert movimentos[0].tipo == TipoMovimentoEstoque.SAIDA_VENDA
    assert movimentos[0].origem == "COMANDA"
    assert movimentos[0].referencia_id == item_cerveja["id"]


def test_adiciona_mesmo_produto_aumenta_item_preservando_snapshot(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"])
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    primeira = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 1},
    ).json()
    segunda = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    ).json()

    assert len(segunda["itens"]) == 1
    assert segunda["itens"][0]["id"] == primeira["itens"][0]["id"]
    assert segunda["itens"][0]["quantidade"] == 3.0
    assert segunda["total"] == 21.0


def test_adicionar_item_valida_produto_quantidade_e_status(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    ativo = create_produto(client, categoria["id"])
    inativo = create_produto(client, categoria["id"], nome="Inativo")
    client.patch(f"/api/produtos/{inativo['id']}/inativar")
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    inexistente = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": 999, "quantidade": 1},
    )
    assert inexistente.status_code == 404
    assert inexistente.json()["code"] == "produto_nao_encontrado"

    produto_inativo = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": inativo["id"], "quantidade": 1},
    )
    assert produto_inativo.status_code == 400
    assert produto_inativo.json()["code"] == "produto_inativo"

    for quantidade in (0, -1):
        invalida = client.post(
            f"/api/comandas/{comanda['id']}/itens",
            json={"produtoId": ativo["id"], "quantidade": quantidade},
        )
        assert invalida.status_code == 400
        assert invalida.json()["code"] == "quantidade_invalida"

    client.patch(f"/api/comandas/{comanda['id']}/cancelar")
    cancelada = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": ativo["id"], "quantidade": 1},
    )
    assert cancelada.status_code == 400
    assert cancelada.json()["code"] == "comanda_nao_aberta"


def test_permite_estoque_negativo_na_venda(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=1)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 3},
    )

    assert response.status_code == 200
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "-2.000"
    )


def test_incrementa_e_diminui_item_com_baixa_e_devolucao(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    item = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    ).json()["itens"][0]

    incremento = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/incrementar",
        json={"quantidade": 1},
    )
    assert incremento.status_code == 200
    assert incremento.json()["itens"][0]["quantidade"] == 3.0
    assert incremento.json()["itens"][0]["totalItem"] == 21.0
    assert incremento.json()["total"] == 21.0
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "7.000"
    )

    decremento = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/diminuir",
        json={"quantidade": 1},
    )
    assert decremento.status_code == 200
    assert decremento.json()["itens"][0]["quantidade"] == 2.0
    assert decremento.json()["itens"][0]["totalItem"] == 14.0
    assert decremento.json()["total"] == 14.0
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "8.000"
    )

    movimentos = list_movimentos(test_engine, produto["id"])
    assert [movimento.tipo for movimento in movimentos] == [
        TipoMovimentoEstoque.SAIDA_VENDA,
        TipoMovimentoEstoque.SAIDA_VENDA,
        TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO,
    ]


def test_diminuir_ate_zero_remove_item(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    item = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    ).json()["itens"][0]

    response = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/diminuir",
        json={"quantidade": 2},
    )

    assert response.status_code == 200
    assert response.json()["itens"] == []
    assert response.json()["total"] == 0.0
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "10.000"
    )


def test_remove_item_devolve_estoque_recalcula_e_valida_pertencimento(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    outra = client.post("/api/comandas", json={"nomeCliente": "Maria"}).json()
    item = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    ).json()["itens"][0]

    errada = client.delete(f"/api/comandas/{outra['id']}/itens/{item['id']}")
    assert errada.status_code == 400
    assert errada.json()["code"] == "item_nao_pertence_comanda"

    response = client.delete(f"/api/comandas/{comanda['id']}/itens/{item['id']}")
    assert response.status_code == 200
    assert response.json()["itens"] == []
    assert response.json()["total"] == 0.0
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "10.000"
    )
    assert list_movimentos(test_engine, produto["id"])[-1].tipo == (
        TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO
    )


def test_cancela_comanda_devolve_estoque_preserva_historico(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    cerveja = create_produto(client, categoria["id"], quantidade_estoque=10)
    taxa = create_produto(
        client,
        categoria["id"],
        nome="Taxa de serviço",
        preco_venda=2,
        controla_estoque=False,
    )
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": cerveja["id"], "quantidade": 3},
    )
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": taxa["id"], "quantidade": 1},
    )

    response = client.patch(
        f"/api/comandas/{comanda['id']}/cancelar",
        json={"motivo": "Lançamento errado"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CANCELADA"
    assert body["canceladaEm"] is not None
    assert body["observacao"] == "Lançamento errado"
    assert body["total"] == 23.0
    assert len(body["itens"]) == 2
    assert get_produto(test_engine, cerveja["id"]).quantidade_estoque == Decimal(
        "10.000"
    )

    movimentos = list_movimentos(test_engine, cerveja["id"])
    assert movimentos[-1].tipo == TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO
    assert movimentos[-1].origem == "CANCELAMENTO"

    novamente = client.patch(f"/api/comandas/{comanda['id']}/cancelar")
    assert novamente.status_code == 400
    assert novamente.json()["code"] == "comanda_nao_aberta"

    with Session(test_engine) as session:
        assert session.get(Comanda, comanda["id"]) is not None
        itens = session.exec(
            select(ItemComanda).where(ItemComanda.comanda_id == comanda["id"])
        ).all()
        assert len(itens) == 2


def test_adiciona_produto_composto_baixa_componentes_e_movimentos(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga_a = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
        quantidade_baixa_por_venda=50,
    )
    pinga_b = create_produto(
        client,
        categoria["id"],
        nome="Pinga B",
        unidade_estoque="ML",
        quantidade_estoque=500,
        quantidade_baixa_por_venda=50,
    )
    add_componente(client, composto["id"], pinga_a["id"], quantidade_baixa=50)
    add_componente(client, composto["id"], pinga_b["id"], quantidade_baixa=25)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )

    assert response.status_code == 200
    body = response.json()
    item = body["itens"][0]
    assert item["produtoId"] == composto["id"]
    assert item["nomeProduto"] == "Dose Mista A+B"
    assert item["precoUnitario"] == 12.0
    assert item["quantidadeBaixadaEstoque"] == 75.0
    assert body["total"] == 12.0
    assert get_produto(test_engine, composto["id"]).quantidade_estoque == Decimal(
        "0.000"
    )
    assert get_produto(test_engine, pinga_a["id"]).quantidade_estoque == Decimal(
        "950.000"
    )
    assert get_produto(test_engine, pinga_b["id"]).quantidade_estoque == Decimal(
        "475.000"
    )

    movimentos_a = list_movimentos(test_engine, pinga_a["id"])
    movimentos_b = list_movimentos(test_engine, pinga_b["id"])
    assert len(movimentos_a) == 1
    assert len(movimentos_b) == 1
    assert movimentos_a[0].tipo == TipoMovimentoEstoque.SAIDA_VENDA
    assert movimentos_b[0].tipo == TipoMovimentoEstoque.SAIDA_VENDA
    assert movimentos_a[0].referencia_id == item["id"]
    assert movimentos_b[0].referencia_id == item["id"]
    assert movimentos_a[0].observacao == "Baixa por produto composto: Dose Mista A+B"


def test_adiciona_duas_unidades_de_composto_baixa_proporcional(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga_a = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    pinga_b = create_produto(
        client,
        categoria["id"],
        nome="Pinga B",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], pinga_a["id"], quantidade_baixa=50)
    add_componente(client, composto["id"], pinga_b["id"], quantidade_baixa=50)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 2},
    )

    assert response.status_code == 200
    assert response.json()["itens"][0]["quantidade"] == 2.0
    assert response.json()["itens"][0]["quantidadeBaixadaEstoque"] == 200.0
    assert response.json()["total"] == 24.0
    assert get_produto(test_engine, pinga_a["id"]).quantidade_estoque == Decimal(
        "900.000"
    )
    assert get_produto(test_engine, pinga_b["id"]).quantidade_estoque == Decimal(
        "900.000"
    )


def test_incrementa_e_diminui_composto_movimenta_componentes(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], pinga["id"], quantidade_baixa=50)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    item = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 2},
    ).json()["itens"][0]

    incremento = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/incrementar",
        json={"quantidade": 1},
    )
    assert incremento.status_code == 200
    assert incremento.json()["itens"][0]["quantidade"] == 3.0
    assert incremento.json()["itens"][0]["quantidadeBaixadaEstoque"] == 150.0
    assert get_produto(test_engine, pinga["id"]).quantidade_estoque == Decimal(
        "850.000"
    )

    decremento = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/diminuir",
        json={"quantidade": 1},
    )
    assert decremento.status_code == 200
    assert decremento.json()["itens"][0]["quantidade"] == 2.0
    assert decremento.json()["itens"][0]["quantidadeBaixadaEstoque"] == 100.0
    assert get_produto(test_engine, pinga["id"]).quantidade_estoque == Decimal(
        "900.000"
    )

    tipos_movimento = [
        movimento.tipo for movimento in list_movimentos(test_engine, pinga["id"])
    ]
    assert tipos_movimento == [
        TipoMovimentoEstoque.SAIDA_VENDA,
        TipoMovimentoEstoque.SAIDA_VENDA,
        TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO,
    ]


def test_remove_item_composto_devolve_componentes(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], pinga["id"], quantidade_baixa=50)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    item = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 2},
    ).json()["itens"][0]

    response = client.delete(f"/api/comandas/{comanda['id']}/itens/{item['id']}")

    assert response.status_code == 200
    assert response.json()["itens"] == []
    assert response.json()["total"] == 0.0
    assert get_produto(test_engine, pinga["id"]).quantidade_estoque == Decimal(
        "1000.000"
    )
    assert list_movimentos(test_engine, pinga["id"])[-1].tipo == (
        TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO
    )


def test_cancela_comanda_com_composto_devolve_componentes(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], pinga["id"], quantidade_baixa=50)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 2},
    )

    response = client.patch(f"/api/comandas/{comanda['id']}/cancelar")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELADA"
    assert response.json()["total"] == 24.0
    assert get_produto(test_engine, pinga["id"]).quantidade_estoque == Decimal(
        "1000.000"
    )
    assert list_movimentos(test_engine, pinga["id"])[-1].origem == "CANCELAMENTO"


def test_rejeita_venda_composto_sem_composicao_ou_com_componente_invalido(
    test_engine,
):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    sem_composicao = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )
    assert sem_composicao.status_code == 400
    assert sem_composicao.json()["code"] == "produto_composto_sem_composicao"

    componente = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], componente["id"], quantidade_baixa=50)
    set_produto_ativo(test_engine, componente["id"], False)

    componente_inativo = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )
    assert componente_inativo.status_code == 400
    assert componente_inativo.json()["code"] == "produto_componente_inativo"

    set_produto_ativo(test_engine, componente["id"], True)
    set_produto_controla_estoque(test_engine, componente["id"], False)

    sem_estoque = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )
    assert sem_estoque.status_code == 400
    assert sem_estoque.json()["code"] == "produto_componente_sem_controle_estoque"


def test_falha_em_componente_nao_persiste_venda_parcial(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista A+B",
        preco_venda=12,
        controla_estoque=False,
        tipo_produto="COMPOSTO",
    )
    pinga_a = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    pinga_b = create_produto(
        client,
        categoria["id"],
        nome="Pinga B",
        unidade_estoque="ML",
        quantidade_estoque=1000,
    )
    add_componente(client, composto["id"], pinga_a["id"], quantidade_baixa=50)
    add_componente(client, composto["id"], pinga_b["id"], quantidade_baixa=50)
    set_produto_ativo(test_engine, pinga_b["id"], False)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "produto_componente_inativo"
    assert get_produto(test_engine, pinga_a["id"]).quantidade_estoque == Decimal(
        "1000.000"
    )
    assert count_movimentos(test_engine, pinga_a["id"]) == 0

    detalhe = client.get(f"/api/comandas/{comanda['id']}")
    assert detalhe.status_code == 200
    assert detalhe.json()["itens"] == []
    assert detalhe.json()["total"] == 0.0


def build_ajuste_service(test_engine) -> AjusteComandaService:
    session = Session(test_engine)
    repository = ComandaRepository(session)
    return AjusteComandaService(comanda_repository=repository)


def preparar_produto_ajuste(client: TestClient) -> dict:
    categoria = create_categoria(client, "Ajustes")
    return create_produto(
        client, categoria["id"], nome="Agua", preco_venda=10, controla_estoque=False
    )


def criar_comanda_com_consumo_ajuste(
    client: TestClient, produto: dict, quantidade: float = 2
) -> dict:
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()
    resposta = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": quantidade},
    )
    return resposta.json()


def registrar_pagamento_parcial(test_engine, comanda_id: int, valor: Decimal) -> None:
    with Session(test_engine) as session:
        pagamento = Pagamento(
            comanda_id=comanda_id,
            forma_pagamento=FormaPagamento.DINHEIRO,
            valor=valor,
        )
        session.add(pagamento)
        session.commit()


def test_comanda_repository_save_ajuste_persiste_ajuste(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)

    with Session(test_engine) as session:
        repository = ComandaRepository(session)
        ajuste = AjusteComanda(
            comanda_id=comanda["id"],
            tipo=TipoAjusteComanda.DESCONTO,
            valor=Decimal("5.00"),
            descricao="cortesia",
        )
        salvo = repository.save_ajuste(ajuste)
        session.commit()

        assert salvo.id is not None
        persistido = session.get(AjusteComanda, salvo.id)
        assert persistido is not None
        assert persistido.comanda_id == comanda["id"]
        assert persistido.tipo == TipoAjusteComanda.DESCONTO
        assert persistido.valor == Decimal("5.00")
        assert persistido.descricao == "cortesia"


def test_ajuste_comanda_service_acrescimo_soma_ao_total(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    atualizada = service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.ACRESCIMO,
        valor=Decimal("5.00"),
        descricao="taxa de serviço",
    )

    assert AjusteComandaService.total_ajustado(atualizada) == Decimal("25.00")


def test_ajuste_comanda_service_desconto_subtrai_do_total(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    atualizada = service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("10.00"),
        descricao="cortesia",
    )

    assert AjusteComandaService.total_ajustado(atualizada) == Decimal("10.00")


def test_ajuste_comanda_service_multiplos_ajustes_acumulam(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("10.00"),
        descricao="cortesia",
    )
    atualizada = service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.ACRESCIMO,
        valor=Decimal("5.00"),
        descricao="taxa de serviço",
    )

    ajustes = service.listar_ajustes(comanda["id"])
    assert AjusteComandaService.total_ajustado(atualizada) == Decimal("15.00")
    assert len(ajustes) == 2
    assert {ajuste.descricao for ajuste in ajustes} == {"cortesia", "taxa de serviço"}


def test_ajuste_comanda_service_rejeita_desconto_sem_descricao(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    with pytest.raises(ApplicationError) as excinfo:
        service.aplicar_ajuste(
            comanda_id=comanda["id"],
            tipo=TipoAjusteComanda.DESCONTO,
            valor=Decimal("10.00"),
            descricao="   ",
        )

    assert excinfo.value.code == "ajuste_descricao_obrigatoria"


def test_ajuste_comanda_service_rejeita_desconto_maior_que_total(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    with pytest.raises(ApplicationError) as excinfo:
        service.aplicar_ajuste(
            comanda_id=comanda["id"],
            tipo=TipoAjusteComanda.DESCONTO,
            valor=Decimal("30.00"),
            descricao="erro de lançamento",
        )

    assert excinfo.value.code == "ajuste_valor_invalido"


def test_ajuste_comanda_service_rejeita_valor_nao_positivo(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)

    with pytest.raises(ApplicationError) as excinfo:
        service.aplicar_ajuste(
            comanda_id=comanda["id"],
            tipo=TipoAjusteComanda.ACRESCIMO,
            valor=Decimal("0"),
            descricao="taxa de serviço",
        )

    assert excinfo.value.code == "ajuste_valor_invalido"


def test_ajuste_comanda_service_rejeita_comanda_fechada_ou_cancelada(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    fechada = criar_comanda_com_consumo_ajuste(client, produto)
    client.post(
        f"/api/comandas/{fechada['id']}/fechar",
        json={"formaPagamento": "PIX", "valorPago": fechada["total"]},
    )
    cancelada = client.post("/api/comandas", json={"nomeCliente": "Maria"}).json()
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")
    service = build_ajuste_service(test_engine)

    for comanda_id in (fechada["id"], cancelada["id"]):
        with pytest.raises(ApplicationError) as excinfo:
            service.aplicar_ajuste(
                comanda_id=comanda_id,
                tipo=TipoAjusteComanda.DESCONTO,
                valor=Decimal("1.00"),
                descricao="erro de lançamento",
            )
        assert excinfo.value.code == "comanda_nao_aberta"


def test_ajuste_comanda_service_recalcula_saldo_com_pagamento_parcial(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    registrar_pagamento_parcial(test_engine, comanda["id"], Decimal("12.00"))
    service = build_ajuste_service(test_engine)

    atualizada = service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("5.00"),
        descricao="erro de lançamento",
    )

    assert AjusteComandaService.total_ajustado(atualizada) == Decimal("15.00")
    assert AjusteComandaService.saldo_restante(atualizada) == Decimal("3.00")


def test_ajuste_comanda_service_desconto_apos_pagamento_gera_saldo_credor(test_engine):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    registrar_pagamento_parcial(test_engine, comanda["id"], Decimal("12.00"))
    service = build_ajuste_service(test_engine)

    atualizada = service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("15.00"),
        descricao="erro de lançamento",
    )

    assert AjusteComandaService.saldo_restante(atualizada) == Decimal("-7.00")


def test_ajuste_comanda_service_rejeita_comanda_inexistente(test_engine):
    service = build_ajuste_service(test_engine)

    with pytest.raises(NotFoundError) as excinfo:
        service.aplicar_ajuste(
            comanda_id=999,
            tipo=TipoAjusteComanda.DESCONTO,
            valor=Decimal("1.00"),
            descricao="erro",
        )

    assert excinfo.value.code == "comanda_nao_encontrada"


def test_comanda_parcialmente_paga_nao_aceita_novos_itens_nem_alterar_itens(
    test_engine,
):
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    item = comanda["itens"][0]
    client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": "DINHEIRO", "valorPago": 12.00},
    )

    adicionar = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 1},
    )
    incrementar = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/incrementar",
        json={"quantidade": 1},
    )
    diminuir = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/diminuir",
        json={"quantidade": 1},
    )
    remover = client.delete(f"/api/comandas/{comanda['id']}/itens/{item['id']}")

    for response in (adicionar, incrementar, diminuir, remover):
        assert response.status_code == 400
        assert response.json()["code"] == "comanda_nao_aceita_novos_itens"


def test_aplicar_ajuste_comanda_request_aceita_tipo_valor_e_descricao():
    # Arrange / Act
    request = AplicarAjusteComandaRequest(
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("5.00"),
        descricao="cortesia",
    )

    # Assert
    assert request.tipo == TipoAjusteComanda.DESCONTO
    assert request.valor == Decimal("5.00")
    assert request.descricao == "cortesia"


def test_ajuste_comanda_response_from_model_serializa_campos_em_camel_case():
    # Arrange
    ajuste = AjusteComanda(
        id=1,
        comanda_id=10,
        tipo=TipoAjusteComanda.ACRESCIMO,
        valor=Decimal("7.50"),
        descricao="taxa de serviço",
    )

    # Act
    response = AjusteComandaResponse.from_model(ajuste)

    # Assert
    body = response.model_dump(by_alias=True, mode="json")
    assert body["id"] == 1
    assert body["tipo"] == "ACRESCIMO"
    assert body["valor"] == 7.5
    assert body["descricao"] == "taxa de serviço"
    assert "criadoEm" in body


def test_consultar_comanda_expoe_total_ajustado_saldo_restante_e_ajustes(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    service = build_ajuste_service(test_engine)
    service.aplicar_ajuste(
        comanda_id=comanda["id"],
        tipo=TipoAjusteComanda.DESCONTO,
        valor=Decimal("5.00"),
        descricao="cortesia",
    )

    # Act
    resumo = client.get("/api/comandas")
    detalhe = client.get(f"/api/comandas/{comanda['id']}")

    # Assert
    assert resumo.status_code == 200
    resumo_body = next(item for item in resumo.json() if item["id"] == comanda["id"])
    assert resumo_body["totalAjustado"] == 15.0
    assert resumo_body["saldoRestante"] == 15.0
    assert len(resumo_body["ajustes"]) == 1

    assert detalhe.status_code == 200
    detalhe_body = detalhe.json()
    assert detalhe_body["totalAjustado"] == 15.0
    assert detalhe_body["saldoRestante"] == 15.0
    assert len(detalhe_body["ajustes"]) == 1
    assert detalhe_body["ajustes"][0]["descricao"] == "cortesia"
    assert detalhe_body["ajustes"][0]["tipo"] == "DESCONTO"
    assert ComandaDetalheResponse(**detalhe_body).total_ajustado == 15.0


def test_post_ajustes_aplica_ajuste_e_retorna_comanda_atualizada(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)

    # Act
    response = client.post(
        f"/api/comandas/{comanda['id']}/ajustes",
        json={"tipo": "DESCONTO", "valor": "5.00", "descricao": "cortesia"},
    )

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["totalAjustado"] == 15.0
    assert body["saldoRestante"] == 15.0
    assert len(body["ajustes"]) == 1


def test_get_ajustes_lista_ajustes_da_comanda(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    client.post(
        f"/api/comandas/{comanda['id']}/ajustes",
        json={"tipo": "ACRESCIMO", "valor": "5.00", "descricao": "taxa de serviço"},
    )

    # Act
    response = client.get(f"/api/comandas/{comanda['id']}/ajustes")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tipo"] == "ACRESCIMO"
    assert body[0]["descricao"] == "taxa de serviço"


def test_post_ajustes_rejeita_descricao_vazia(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)

    # Act
    response = client.post(
        f"/api/comandas/{comanda['id']}/ajustes",
        json={"tipo": "DESCONTO", "valor": "5.00", "descricao": "   "},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["code"] == "ajuste_descricao_obrigatoria"


def test_post_ajustes_rejeita_valor_invalido(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)

    # Act
    response = client.post(
        f"/api/comandas/{comanda['id']}/ajustes",
        json={"tipo": "DESCONTO", "valor": "30.00", "descricao": "erro"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["code"] == "ajuste_valor_invalido"


def test_post_ajustes_rejeita_comanda_nao_aberta(test_engine):
    # Arrange
    client = build_client(test_engine)
    produto = preparar_produto_ajuste(client)
    comanda = criar_comanda_com_consumo_ajuste(client, produto)
    client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )

    # Act
    response = client.post(
        f"/api/comandas/{comanda['id']}/ajustes",
        json={"tipo": "DESCONTO", "valor": "1.00", "descricao": "erro"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"


def test_ajustes_rejeitam_comanda_inexistente(test_engine):
    # Arrange
    client = build_client(test_engine)

    # Act
    post_response = client.post(
        "/api/comandas/999/ajustes",
        json={"tipo": "DESCONTO", "valor": "1.00", "descricao": "erro"},
    )
    get_response = client.get("/api/comandas/999/ajustes")

    # Assert
    assert post_response.status_code == 404
    assert post_response.json()["code"] == "comanda_nao_encontrada"
    assert get_response.status_code == 404
    assert get_response.json()["code"] == "comanda_nao_encontrada"
