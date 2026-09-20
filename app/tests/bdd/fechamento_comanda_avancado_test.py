"""Cenários de aceite (BDD) da feature 005-fechamento-comanda-avancado.

Cada função reproduz, na docstring, o texto Gherkin exato de
`specs/005-fechamento-comanda-avancado/spec.md` (sem tradução), e implementa
os passos DADO/QUANDO/ENTÃO/MAS via `fastapi.testclient.TestClient` contra um
banco sqlite em memória — mesma convenção de `app/conftest.py`, já que este
repositório não usa um framework BDD dedicado (`pytest-bdd`/`behave`).
"""

from decimal import Decimal

from dependency_injector import providers
from fastapi.testclient import TestClient

from api import create_app


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    client = TestClient(app)
    response = client.post("/api/caixas/abrir", json={"valorInicial": 100})
    assert response.status_code == 201
    return client


def criar_comanda_com_total(client: TestClient, total: str) -> dict:
    categoria = client.post("/api/categorias", json={"nome": "Bebidas BDD"}).json()
    produto = client.post(
        "/api/produtos",
        json={
            "categoriaId": categoria["id"],
            "nome": "Item BDD",
            "precoVenda": float(total),
            "controlaEstoque": False,
        },
    ).json()
    comanda = client.post("/api/comandas", json={"nomeCliente": "Cliente BDD"}).json()
    client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 1},
    )
    return client.get(f"/api/comandas/{comanda['id']}").json()


def registrar_pagamento(
    client: TestClient, comanda_id: int, valor, forma: str = "DINHEIRO"
):
    return client.post(
        f"/api/comandas/{comanda_id}/fechar",
        json={"formaPagamento": forma, "valorPago": float(valor)},
    )


def criar_cliente(client: TestClient, nome: str = "Cliente Fiado BDD") -> dict:
    response = client.post("/api/clientes", json={"nome": nome})
    assert response.status_code == 201
    return response.json()


def marcar_fiado(client: TestClient, comanda_id: int, cliente_id: int):
    return client.post(
        f"/api/comandas/{comanda_id}/fiado", json={"clienteId": cliente_id}
    )


def quitar_fiado(client: TestClient, comanda_id: int, valor, forma: str = "DINHEIRO"):
    return client.post(
        f"/api/fiados/{comanda_id}/quitar",
        json={"formaPagamento": forma, "valorPago": float(valor)},
    )


def aplicar_ajuste(
    client: TestClient, comanda_id: int, tipo: str, valor, descricao: str
):
    return client.post(
        f"/api/comandas/{comanda_id}/ajustes",
        json={"tipo": tipo, "valor": str(valor), "descricao": descricao},
    )


def test_pagamento_parcial_de_comanda_aberta_com_saldo_restante_rastreado(
    test_engine,
):
    """
    # language: pt
    Cenário: Pagamento parcial de comanda aberta com saldo restante rastreado
      Dado uma comanda aberta com total de 100,00
      Quando um pagamento de 60,00 em dinheiro é registrado para essa comanda
      Então a comanda passa a ter status parcialmente paga
      E o saldo restante da comanda é 40,00
      Mas a comanda não deve ser marcada como fechada
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    response = registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Então / Mas
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARCIALMENTE_PAGA"
    assert Decimal(str(body["saldoRestante"])) == Decimal("40.00")
    assert body["fechadaEm"] is None


def test_multiplos_pagamentos_ate_completar_o_total(test_engine):
    """
    # language: pt
    Cenário: Múltiplos pagamentos até completar o total
      Dado uma comanda aberta com total de 100,00 e um pagamento anterior de
      60,00 já registrado
      Quando um segundo pagamento de 40,00 em PIX é registrado para essa comanda
      Então a comanda passa a ter status fechada
      E o saldo restante da comanda é 0,00
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Quando
    response = registrar_pagamento(client, comanda["id"], "40.00", "PIX")

    # Então
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FECHADA"
    assert Decimal(str(body["saldoRestante"])) == Decimal("0.00")


def test_pagamento_que_ultrapassa_o_saldo_restante_e_rejeitado(test_engine):
    """
    # language: pt
    Cenário: Pagamento que ultrapassa o saldo restante é rejeitado
      Dado uma comanda aberta com total de 100,00 e um pagamento anterior de
      60,00 já registrado
      Quando um pagamento de 50,00 é registrado para essa comanda
      Então o sistema rejeita a operação com erro de valor pago inválido
      Mas nenhum pagamento novo deve ser persistido
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Quando
    response = registrar_pagamento(client, comanda["id"], "50.00", "PIX")

    # Então / Mas
    assert response.status_code == 400
    assert response.json()["code"] == "valor_pago_invalido"
    pagamentos = client.get(f"/api/comandas/{comanda['id']}/pagamentos").json()
    assert len(pagamentos) == 1


def test_saldo_restante_de_pagamento_parcial_vira_fiado(test_engine):
    """
    # language: pt
    Cenário: Saldo restante de pagamento parcial vira fiado
      Dado uma comanda aberta com total de 100,00 e um pagamento anterior de
      60,00 já registrado
      Quando o saldo restante dessa comanda é marcado como fiado para um
      cliente cadastrado
      Então a comanda passa a ter status pendente
      E o valor devido em aberto no módulo de fiado é 40,00
    """
    # Dado
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Quando
    response = marcar_fiado(client, comanda["id"], cliente["id"])

    # Então
    assert response.status_code == 200
    assert response.json()["status"] == "PENDENTE"
    pendencia = client.get(f"/api/fiados/{comanda['id']}").json()
    assert Decimal(str(pendencia["saldoRestante"])) == Decimal("40.00")


def test_quitacao_parcial_de_pendencia_de_fiado(test_engine):
    """
    # language: pt
    Cenário: Quitação parcial de pendência de fiado
      Dado uma comanda pendente de fiado com saldo devido de 40,00
      Quando um pagamento de quitação de 25,00 é registrado para essa pendência
      Então a comanda permanece com status pendente
      E o saldo devido da pendência passa a ser 15,00
    """
    # Dado
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")
    marcar_fiado(client, comanda["id"], cliente["id"])

    # Quando
    response = quitar_fiado(client, comanda["id"], "25.00")

    # Então
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDENTE"
    assert Decimal(str(body["saldoRestante"])) == Decimal("15.00")


def test_quitacao_total_de_pendencia_de_fiado_encerra_a_pendencia(test_engine):
    """
    # language: pt
    Cenário: Quitação total de pendência de fiado encerra a pendência
      Dado uma comanda pendente de fiado com saldo devido de 15,00
      Quando um pagamento de quitação de 15,00 é registrado para essa pendência
      Então a comanda passa a ter status fechada
      E a pendência não aparece mais na listagem de pendências em aberto
    """
    # Dado
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_total(client, "15.00")
    marcar_fiado(client, comanda["id"], cliente["id"])

    # Quando
    response = quitar_fiado(client, comanda["id"], "15.00")

    # Então
    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"
    pendencias_abertas = client.get("/api/fiados").json()
    assert comanda["id"] not in [item["comandaId"] for item in pendencias_abertas]


def test_aplicar_desconto_com_descricao_ao_fechamento(test_engine):
    """
    # language: pt
    Cenário: Aplicar desconto com descrição ao fechamento
      Dado uma comanda aberta com total original de 100,00
      Quando um desconto de 10,00 com descrição "cortesia" é aplicado a essa comanda
      Então o total ajustado da comanda passa a ser 90,00
      E o desconto aplicado fica registrado com a descrição "cortesia"
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    response = aplicar_ajuste(client, comanda["id"], "DESCONTO", "10.00", "cortesia")

    # Então
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["totalAjustado"])) == Decimal("90.00")
    assert len(body["ajustes"]) == 1
    assert body["ajustes"][0]["tipo"] == "DESCONTO"
    assert body["ajustes"][0]["descricao"] == "cortesia"


def test_aplicar_acrescimo_com_descricao_ao_fechamento(test_engine):
    """
    # language: pt
    Cenário: Aplicar acréscimo com descrição ao fechamento
      Dado uma comanda aberta com total original de 100,00
      Quando um acréscimo de 5,00 com descrição "taxa de serviço" é aplicado a
      essa comanda
      Então o total ajustado da comanda passa a ser 105,00
      E o acréscimo aplicado fica registrado com a descrição "taxa de serviço"
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    response = aplicar_ajuste(
        client, comanda["id"], "ACRESCIMO", "5.00", "taxa de serviço"
    )

    # Então
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["totalAjustado"])) == Decimal("105.00")
    assert len(body["ajustes"]) == 1
    assert body["ajustes"][0]["tipo"] == "ACRESCIMO"
    assert body["ajustes"][0]["descricao"] == "taxa de serviço"


def test_acrescimo_ou_desconto_sem_descricao_e_rejeitado(test_engine):
    """
    # language: pt
    Cenário: Acréscimo ou desconto sem descrição é rejeitado
      Dado uma comanda aberta com total original de 100,00
      Quando um desconto de 10,00 é aplicado a essa comanda sem descrição
      Então o sistema rejeita a operação com erro de descrição obrigatória
      Mas o total da comanda não deve ser alterado
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    response = aplicar_ajuste(client, comanda["id"], "DESCONTO", "10.00", "   ")

    # Então / Mas
    assert response.status_code == 400
    assert response.json()["code"] == "ajuste_descricao_obrigatoria"
    detalhe = client.get(f"/api/comandas/{comanda['id']}").json()
    assert Decimal(str(detalhe["totalAjustado"])) == Decimal("100.00")


def test_desconto_maior_que_o_total_e_rejeitado(test_engine):
    """
    # language: pt
    Cenário: Desconto maior que o total é rejeitado
      Dado uma comanda aberta com total original de 100,00
      Quando um desconto de 150,00 com descrição "erro de lançamento" é
      aplicado a essa comanda
      Então o sistema rejeita a operação com erro de valor de ajuste inválido
      Mas o total da comanda não deve ser alterado
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    response = aplicar_ajuste(
        client, comanda["id"], "DESCONTO", "150.00", "erro de lançamento"
    )

    # Então / Mas
    assert response.status_code == 400
    assert response.json()["code"] == "ajuste_valor_invalido"
    detalhe = client.get(f"/api/comandas/{comanda['id']}").json()
    assert Decimal(str(detalhe["totalAjustado"])) == Decimal("100.00")


def test_acrescimo_desconto_nao_pode_ser_aplicado_a_comanda_ja_fechada(test_engine):
    """
    # language: pt
    Cenário: Acréscimo/desconto não pode ser aplicado a comanda já fechada
      Dado uma comanda fechada
      Quando um desconto de 10,00 com descrição "erro de lançamento" é
      aplicado a essa comanda
      Então o sistema rejeita a operação com erro de comanda não está aberta
      Mas o total da comanda não deve ser alterado
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "100.00", "PIX")

    # Quando
    response = aplicar_ajuste(
        client, comanda["id"], "DESCONTO", "10.00", "erro de lançamento"
    )

    # Então / Mas
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"
    detalhe = client.get(f"/api/comandas/{comanda['id']}").json()
    assert Decimal(str(detalhe["totalAjustado"])) == Decimal("100.00")


def test_pagamento_respeita_total_ajustado_por_desconto(test_engine):
    """
    # language: pt
    Cenário: Pagamento respeita total ajustado por desconto
      Dado uma comanda aberta com total original de 100,00 e um desconto de
      10,00 com descrição "cortesia" já aplicado
      Quando um pagamento de 90,00 é registrado para essa comanda
      Então a comanda passa a ter status fechada
      Mas um pagamento de 100,00 para essa mesma comanda deve ser rejeitado por
      ultrapassar o saldo restante
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    aplicar_ajuste(client, comanda["id"], "DESCONTO", "10.00", "cortesia")

    # Quando
    response = registrar_pagamento(client, comanda["id"], "90.00", "PIX")

    # Então / Mas
    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"
    excedente = registrar_pagamento(client, comanda["id"], "100.00", "PIX")
    assert excedente.status_code == 400


def test_comanda_com_pagamento_parcial_nao_aceita_novos_itens(test_engine):
    """
    # language: pt
    Cenário: Comanda com pagamento parcial não aceita novos itens
      Dado uma comanda aberta com total de 100,00 e um pagamento anterior de
      60,00 já registrado
      Quando um novo item é adicionado a essa comanda
      Então o sistema rejeita a operação com erro de comanda não aceita novos itens
      Mas o total da comanda não deve ser alterado
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")
    categoria = client.post("/api/categorias", json={"nome": "Outra BDD"}).json()
    produto = client.post(
        "/api/produtos",
        json={
            "categoriaId": categoria["id"],
            "nome": "Novo item BDD",
            "precoVenda": 5.0,
            "controlaEstoque": False,
        },
    ).json()

    # Quando
    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 1},
    )

    # Então / Mas
    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aceita_novos_itens"
    detalhe = client.get(f"/api/comandas/{comanda['id']}").json()
    assert Decimal(str(detalhe["total"])) == Decimal("100.00")


def test_multiplos_acrescimos_descontos_se_acumulam_no_total_ajustado(test_engine):
    """
    # language: pt
    Cenário: Múltiplos acréscimos/descontos se acumulam no total ajustado
      Dado uma comanda aberta com total original de 100,00
      Quando um desconto de 10,00 com descrição "cortesia" é aplicado a essa comanda
      E um acréscimo de 5,00 com descrição "taxa de serviço" é aplicado a essa
      comanda
      Então o total ajustado da comanda passa a ser 95,00
      E os dois ajustes ficam registrados individualmente com suas descrições
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")

    # Quando
    aplicar_ajuste(client, comanda["id"], "DESCONTO", "10.00", "cortesia")
    response = aplicar_ajuste(
        client, comanda["id"], "ACRESCIMO", "5.00", "taxa de serviço"
    )

    # Então
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["totalAjustado"])) == Decimal("95.00")
    ajustes = client.get(f"/api/comandas/{comanda['id']}/ajustes").json()
    assert len(ajustes) == 2
    assert {ajuste["descricao"] for ajuste in ajustes} == {
        "cortesia",
        "taxa de serviço",
    }


def test_desconto_apos_pagamento_parcial_recalcula_o_saldo_restante(test_engine):
    """
    # language: pt
    Cenário: Desconto após pagamento parcial recalcula o saldo restante
      Dado uma comanda aberta com total original de 100,00 e um pagamento
      anterior de 60,00 já registrado
      Quando um desconto de 20,00 com descrição "erro de lançamento" é
      aplicado a essa comanda
      Então o total ajustado da comanda passa a ser 80,00
      E o saldo restante da comanda passa a ser 20,00
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Quando
    response = aplicar_ajuste(
        client, comanda["id"], "DESCONTO", "20.00", "erro de lançamento"
    )

    # Então
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["totalAjustado"])) == Decimal("80.00")
    assert Decimal(str(body["saldoRestante"])) == Decimal("20.00")


def test_desconto_apos_pagamento_gera_saldo_credor(test_engine):
    """
    # language: pt
    Cenário: Desconto após pagamento gera saldo credor
      Dado uma comanda aberta com total original de 100,00 e um pagamento
      anterior de 60,00 já registrado
      Quando um desconto de 50,00 com descrição "erro de lançamento" é
      aplicado a essa comanda
      Então o total ajustado da comanda passa a ser 50,00
      E o saldo restante da comanda passa a ser -10,00, indicando saldo credor
    """
    # Dado
    client = build_client(test_engine)
    comanda = criar_comanda_com_total(client, "100.00")
    registrar_pagamento(client, comanda["id"], "60.00", "DINHEIRO")

    # Quando
    response = aplicar_ajuste(
        client, comanda["id"], "DESCONTO", "50.00", "erro de lançamento"
    )

    # Então
    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["totalAjustado"])) == Decimal("50.00")
    assert Decimal(str(body["saldoRestante"])) == Decimal("-10.00")
