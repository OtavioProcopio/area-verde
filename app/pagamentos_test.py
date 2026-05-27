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
        conn.execute(text("DELETE FROM item_comanda;"))
        conn.execute(text("DELETE FROM comanda;"))
        conn.execute(text("DELETE FROM movimento_estoque;"))
        conn.execute(text("DELETE FROM produto;"))
        conn.execute(text("DELETE FROM categoria_produto;"))
        conn.commit()


def _create_comanda(client: TestClient) -> dict:
    response = client.post("/api/comandas", json={"nomeCliente": "Cliente Teste"})
    return response.json()


def _create_comanda_com_consumo(client: TestClient) -> dict:
    comanda = _create_comanda(client)

    cat_res = client.post("/api/categorias", json={"nome": "Bebidas"})
    cat_id = cat_res.json()["id"]

    prod_res = client.post(
        "/api/produtos",
        json={
            "categoriaId": cat_id,
            "nome": "Agua",
            "precoVenda": 5.0,
            "controlaEstoque": False,
        },
    )
    prod_id = prod_res.json()["id"]

    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": prod_id, "quantidade": 2},
    )

    res = client.get(f"/api/comandas/{comanda['id']}")
    return res.json()


def test_fechar_comanda_valida_dinheiro(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    total = comanda["total"]

    payload = {
        "formaPagamento": "DINHEIRO",
        "valorPago": total,
        "observacao": "Pago com dinheiro",
    }

    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FECHADA"
    assert data["fechadaEm"] is not None
    assert len(data["pagamentos"]) == 1
    assert data["pagamentos"][0]["formaPagamento"] == "DINHEIRO"
    assert float(data["pagamentos"][0]["valor"]) == total
    assert data["pagamentos"][0]["observacao"] == "Pago com dinheiro"


def test_fechar_comanda_valida_pix(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"]}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"


def test_fechar_comanda_valida_cartao(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "CARTAO", "valorPago": comanda["total"]}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"


def test_fechar_comanda_inexistente(client: TestClient):
    payload = {"formaPagamento": "PIX", "valorPago": 10.0}
    response = client.post("/api/comandas/999/fechar", json=payload)
    assert response.status_code == 404


def test_fechar_comanda_sem_consumo(client: TestClient):
    comanda = _create_comanda(client)
    payload = {"formaPagamento": "PIX", "valorPago": 10.0}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_sem_consumo"


def test_fechar_comanda_valor_menor(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"] - 1}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "valor_pago_invalido"


def test_fechar_comanda_valor_maior(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"] + 1}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "valor_pago_invalido"


def test_fechar_comanda_fiado_nao_implementado(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "FIADO", "valorPago": comanda["total"]}
    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 400
    assert "fiado_nao_implementado" in response.json()["code"]


def test_listar_pagamentos_sucesso(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {
        "formaPagamento": "PIX",
        "valorPago": comanda["total"],
        "observacao": "Pix confirmado",
    }
    client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)

    response = client.get(f"/api/comandas/{comanda['id']}/pagamentos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["formaPagamento"] == "PIX"
    assert data[0]["observacao"] == "Pix confirmado"


def test_listar_pagamentos_vazia(client: TestClient):
    comanda = _create_comanda(client)
    response = client.get(f"/api/comandas/{comanda['id']}/pagamentos")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_regressao_nao_fechar_comanda_ja_fechada(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"]}
    client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)

    response = client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"


def test_regressao_nao_adicionar_item_comanda_fechada(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"]}
    client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)

    cat_res = client.post("/api/categorias", json={"nome": "Outra"})
    prod_res = client.post(
        "/api/produtos",
        json={
            "categoriaId": cat_res.json()["id"],
            "nome": "Suco",
            "precoVenda": 5.0,
            "controlaEstoque": False,
        },
    )
    item_payload = {"produtoId": prod_res.json()["id"], "quantidade": 1}

    response = client.post(f"/api/comandas/{comanda['id']}/itens", json=item_payload)
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"


def test_regressao_nao_alterar_itens_comanda_fechada(client: TestClient):
    comanda = _create_comanda_com_consumo(client)
    item = comanda["itens"][0]
    payload = {"formaPagamento": "PIX", "valorPago": comanda["total"]}
    client.post(f"/api/comandas/{comanda['id']}/fechar", json=payload)

    incrementar = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/incrementar",
        json={"quantidade": 1},
    )
    diminuir = client.patch(
        f"/api/comandas/{comanda['id']}/itens/{item['id']}/diminuir",
        json={"quantidade": 1},
    )
    remover = client.delete(f"/api/comandas/{comanda['id']}/itens/{item['id']}")

    assert incrementar.status_code == 400
    assert incrementar.json()["code"] == "comanda_nao_aberta"
    assert diminuir.status_code == 400
    assert diminuir.json()["code"] == "comanda_nao_aberta"
    assert remover.status_code == 400
    assert remover.json()["code"] == "comanda_nao_aberta"
