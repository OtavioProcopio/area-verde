from decimal import Decimal
from typing import Generator

import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import text

from api import create_app


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


@pytest.fixture
def client(test_engine) -> Generator[TestClient, None, None]:
    client = build_client(test_engine)
    yield client
    with test_engine.connect() as conn:
        conn.execute(text("DELETE FROM pagamento;"))
        conn.execute(text("DELETE FROM movimento_caixa;"))
        conn.execute(text("DELETE FROM caixa;"))
        conn.execute(text("DELETE FROM item_comanda;"))
        conn.execute(text("DELETE FROM comanda;"))
        conn.execute(text("DELETE FROM movimento_estoque;"))
        conn.execute(text("DELETE FROM produto;"))
        conn.execute(text("DELETE FROM categoria_produto;"))
        conn.commit()


def _money(value) -> Decimal:
    return Decimal(str(value))


def _abrir_caixa(client: TestClient, valor_inicial=100, observacao="Abertura") -> dict:
    response = client.post(
        "/api/caixas/abrir",
        json={"valorInicial": valor_inicial, "observacao": observacao},
    )
    assert response.status_code == 201
    return response.json()


def _create_comanda_com_consumo(client: TestClient, nome_produto="Agua") -> dict:
    comanda_res = client.post("/api/comandas", json={"nomeCliente": "Cliente Caixa"})
    comanda = comanda_res.json()

    cat_res = client.post("/api/categorias", json={"nome": f"Bebidas {nome_produto}"})
    prod_res = client.post(
        "/api/produtos",
        json={
            "categoriaId": cat_res.json()["id"],
            "nome": nome_produto,
            "precoVenda": 5.0,
            "controlaEstoque": False,
        },
    )
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": prod_res.json()["id"], "quantidade": 2},
    )
    return client.get(f"/api/comandas/{comanda['id']}").json()


def _fechar_comanda(client: TestClient, comanda: dict, forma_pagamento: str) -> dict:
    response = client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": forma_pagamento, "valorPago": comanda["total"]},
    )
    assert response.status_code == 200
    return response.json()


def test_abre_caixa_com_valor_inicial_e_movimento_abertura(client: TestClient):
    caixa = _abrir_caixa(client, valor_inicial=100, observacao="Abertura do turno")

    assert caixa["status"] == "ABERTO"
    assert _money(caixa["valorInicial"]) == Decimal("100.00")
    assert _money(caixa["dinheiroEsperado"]) == Decimal("100.00")
    assert caixa["dinheiroInformado"] is None
    assert caixa["diferenca"] is None
    assert caixa["abertoEm"] is not None
    assert caixa["fechadoEm"] is None
    assert len(caixa["movimentos"]) == 1
    assert caixa["movimentos"][0]["tipo"] == "ABERTURA"
    assert caixa["movimentos"][0]["observacao"] == "Abertura do turno"


def test_rejeita_valor_inicial_negativo(client: TestClient):
    response = client.post("/api/caixas/abrir", json={"valorInicial": -1})

    assert response.status_code == 422


def test_rejeita_abrir_segundo_caixa_aberto(client: TestClient):
    _abrir_caixa(client)

    response = client.post("/api/caixas/abrir", json={"valorInicial": 10})

    assert response.status_code == 400
    assert response.json()["code"] == "caixa_ja_aberto"


def test_consulta_caixa_aberto(client: TestClient):
    caixa = _abrir_caixa(client)

    response = client.get("/api/caixas/aberto")

    assert response.status_code == 200
    assert response.json()["id"] == caixa["id"]


def test_consulta_caixa_aberto_retorna_404_quando_nao_existe(client: TestClient):
    response = client.get("/api/caixas/aberto")

    assert response.status_code == 404
    assert response.json()["code"] == "caixa_aberto_nao_encontrado"


def test_lista_caixas_e_filtra_por_status_e_data(client: TestClient):
    caixa_aberto = _abrir_caixa(client, valor_inicial=50)
    data_caixa = caixa_aberto["data"]
    client.post(
        f"/api/caixas/{caixa_aberto['id']}/fechar",
        json={"dinheiroInformado": 50},
    )
    _abrir_caixa(client, valor_inicial=20)

    todos = client.get("/api/caixas")
    abertos = client.get("/api/caixas?status=ABERTO")
    fechados = client.get("/api/caixas?status=FECHADO")
    por_data = client.get(f"/api/caixas?data={data_caixa}")

    assert todos.status_code == 200
    assert len(todos.json()) == 2
    assert len(abertos.json()) == 1
    assert abertos.json()[0]["status"] == "ABERTO"
    assert len(fechados.json()) == 1
    assert fechados.json()[0]["status"] == "FECHADO"
    assert len(por_data.json()) == 2


def test_consulta_caixa_por_id_e_retorna_404_para_inexistente(client: TestClient):
    caixa = _abrir_caixa(client)

    existente = client.get(f"/api/caixas/{caixa['id']}")
    inexistente = client.get("/api/caixas/999")

    assert existente.status_code == 200
    assert existente.json()["id"] == caixa["id"]
    assert inexistente.status_code == 404
    assert inexistente.json()["code"] == "caixa_nao_encontrado"


def test_registra_reforco_soma_dinheiro_esperado_e_cria_movimento(client: TestClient):
    caixa = _abrir_caixa(client, valor_inicial=100)

    response = client.post(
        f"/api/caixas/{caixa['id']}/reforcos",
        json={"valor": 50, "observacao": "Troco adicional"},
    )

    assert response.status_code == 200
    data = response.json()
    assert _money(data["dinheiroEsperado"]) == Decimal("150.00")
    assert data["movimentos"][-1]["tipo"] == "REFORCO"
    assert _money(data["movimentos"][-1]["valor"]) == Decimal("50.00")


def test_rejeita_reforco_zero_negativo_e_caixa_fechado(client: TestClient):
    caixa = _abrir_caixa(client)
    client.post(f"/api/caixas/{caixa['id']}/fechar", json={"dinheiroInformado": 100})

    zero = client.post(f"/api/caixas/{caixa['id']}/reforcos", json={"valor": 0})
    negativo = client.post(f"/api/caixas/{caixa['id']}/reforcos", json={"valor": -1})
    fechado = client.post(f"/api/caixas/{caixa['id']}/reforcos", json={"valor": 1})

    assert zero.status_code == 422
    assert negativo.status_code == 422
    assert fechado.status_code == 400
    assert fechado.json()["code"] == "caixa_fechado"


def test_registra_sangria_subtrai_dinheiro_esperado_e_cria_movimento(
    client: TestClient,
):
    caixa = _abrir_caixa(client, valor_inicial=100)

    response = client.post(
        f"/api/caixas/{caixa['id']}/sangrias",
        json={"valor": 30, "observacao": "Retirada parcial"},
    )

    assert response.status_code == 200
    data = response.json()
    assert _money(data["dinheiroEsperado"]) == Decimal("70.00")
    assert data["movimentos"][-1]["tipo"] == "SANGRIA"


def test_rejeita_sangria_zero_negativa_maior_que_esperado_e_caixa_fechado(
    client: TestClient,
):
    caixa = _abrir_caixa(client, valor_inicial=100)

    zero = client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": 0})
    negativo = client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": -1})
    maior = client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": 101})
    client.post(f"/api/caixas/{caixa['id']}/fechar", json={"dinheiroInformado": 100})
    fechado = client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": 1})

    assert zero.status_code == 422
    assert negativo.status_code == 422
    assert maior.status_code == 400
    assert maior.json()["code"] == "sangria_invalida"
    assert fechado.status_code == 400
    assert fechado.json()["code"] == "caixa_fechado"


def test_fecha_caixa_calcula_diferencas_e_bloqueia_fechamento_duplicado(
    client: TestClient,
):
    caixa_zero = _abrir_caixa(client, valor_inicial=100)
    zero = client.post(
        f"/api/caixas/{caixa_zero['id']}/fechar",
        json={"dinheiroInformado": 100},
    )
    assert zero.status_code == 200
    assert zero.json()["status"] == "FECHADO"
    assert zero.json()["fechadoEm"] is not None
    assert _money(zero.json()["diferenca"]) == Decimal("0.00")

    caixa_positivo = _abrir_caixa(client, valor_inicial=100)
    positivo = client.post(
        f"/api/caixas/{caixa_positivo['id']}/fechar",
        json={"dinheiroInformado": 120},
    )
    assert _money(positivo.json()["diferenca"]) == Decimal("20.00")

    caixa_negativo = _abrir_caixa(client, valor_inicial=100)
    negativo = client.post(
        f"/api/caixas/{caixa_negativo['id']}/fechar",
        json={"dinheiroInformado": 80},
    )
    duplicado = client.post(
        f"/api/caixas/{caixa_negativo['id']}/fechar",
        json={"dinheiroInformado": 80},
    )

    assert _money(negativo.json()["diferenca"]) == Decimal("-20.00")
    assert duplicado.status_code == 400
    assert duplicado.json()["code"] == "caixa_fechado"


def test_rejeita_dinheiro_informado_negativo(client: TestClient):
    caixa = _abrir_caixa(client)

    response = client.post(
        f"/api/caixas/{caixa['id']}/fechar",
        json={"dinheiroInformado": -1},
    )

    assert response.status_code == 422


def test_pagamento_exige_caixa_aberto(client: TestClient):
    comanda = _create_comanda_com_consumo(client)

    response = client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "caixa_aberto_nao_encontrado"


def test_pagamento_dinheiro_vincula_caixa_e_soma_dinheiro_esperado(
    client: TestClient,
):
    caixa = _abrir_caixa(client, valor_inicial=100)
    comanda = _create_comanda_com_consumo(client)

    fechamento = _fechar_comanda(client, comanda, "DINHEIRO")
    detalhe = client.get(f"/api/caixas/{caixa['id']}").json()

    assert fechamento["pagamentos"][0]["caixaId"] == caixa["id"]
    assert _money(detalhe["dinheiroEsperado"]) == Decimal("110.00")
    assert len(detalhe["pagamentos"]) == 1
    assert detalhe["pagamentos"][0]["formaPagamento"] == "DINHEIRO"


def test_pagamento_pix_e_cartao_vinculam_caixa_sem_somar_dinheiro(
    client: TestClient,
):
    caixa = _abrir_caixa(client, valor_inicial=100)
    comanda_pix = _create_comanda_com_consumo(client, nome_produto="Agua Pix")
    comanda_cartao = _create_comanda_com_consumo(client, nome_produto="Agua Cartao")

    _fechar_comanda(client, comanda_pix, "PIX")
    _fechar_comanda(client, comanda_cartao, "CARTAO")
    detalhe = client.get(f"/api/caixas/{caixa['id']}").json()

    assert _money(detalhe["dinheiroEsperado"]) == Decimal("100.00")
    assert len(detalhe["pagamentos"]) == 2
    assert {pagamento["formaPagamento"] for pagamento in detalhe["pagamentos"]} == {
        "PIX",
        "CARTAO",
    }


def test_regressao_pagamento_nao_baixa_estoque_novamente(client: TestClient):
    _abrir_caixa(client)
    comanda = client.post("/api/comandas", json={"nomeCliente": "Estoque"}).json()
    categoria = client.post("/api/categorias", json={"nome": "Controlados"}).json()
    produto = client.post(
        "/api/produtos",
        json={
            "categoriaId": categoria["id"],
            "nome": "Cerveja",
            "precoVenda": 10,
            "controlaEstoque": True,
            "unidadeEstoque": "UNIDADE",
            "quantidadeEstoque": 10,
            "quantidadeBaixaPorVenda": 1,
            "estoqueMinimo": 1,
        },
    ).json()
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    )
    antes = client.get(f"/api/produtos/{produto['id']}").json()

    client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": "DINHEIRO", "valorPago": 20},
    )
    depois = client.get(f"/api/produtos/{produto['id']}").json()

    assert _money(antes["quantidadeEstoque"]) == Decimal("8.000")
    assert depois["quantidadeEstoque"] == antes["quantidadeEstoque"]


def test_regressao_comanda_fechada_continua_bloqueando_alteracoes(
    client: TestClient,
):
    _abrir_caixa(client)
    comanda = _create_comanda_com_consumo(client)
    item = comanda["itens"][0]
    _fechar_comanda(client, comanda, "PIX")

    response = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/incrementar",
        json={"quantidade": 1},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"


def test_regressao_caixa_fechado_nao_aceita_movimentacoes(client: TestClient):
    caixa = _abrir_caixa(client)
    client.post(f"/api/caixas/{caixa['id']}/fechar", json={"dinheiroInformado": 100})

    reforco = client.post(f"/api/caixas/{caixa['id']}/reforcos", json={"valor": 10})
    sangria = client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": 10})

    assert reforco.status_code == 400
    assert sangria.status_code == 400
    assert reforco.json()["code"] == "caixa_fechado"
    assert sangria.json()["code"] == "caixa_fechado"
