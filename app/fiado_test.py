from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlmodel import Session

from api import create_app
from core.domain.enums import StatusCaixa
from core.domain.models import Caixa


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def _money(value) -> Decimal:
    return Decimal(str(value))


def criar_cliente(client: TestClient, nome: str = "João da Oficina") -> dict:
    response = client.post(
        "/api/clientes",
        json={"nome": nome, "apelido": "João", "telefone": "16999999999"},
    )
    assert response.status_code == 201
    return response.json()


def garantir_caixa_aberto(client: TestClient) -> dict:
    response = client.get("/api/caixas/aberto")
    if response.status_code == 200:
        return response.json()
    return abrir_caixa(client)


def fechar_caixa_direto(test_engine, caixa_id: int) -> None:
    with Session(test_engine) as session:
        caixa = session.get(Caixa, caixa_id)
        assert caixa is not None
        caixa.status = StatusCaixa.FECHADO
        session.add(caixa)
        session.commit()


def criar_produto(client: TestClient, nome: str = "Agua") -> dict:
    categoria = client.post("/api/categorias", json={"nome": f"Bebidas {nome}"}).json()
    produto = client.post(
        "/api/produtos",
        json={
            "categoriaId": categoria["id"],
            "nome": nome,
            "precoVenda": 10,
            "controlaEstoque": False,
        },
    )
    assert produto.status_code == 201
    return produto.json()


def criar_comanda_com_consumo(
    client: TestClient,
    cliente_id: int | None = None,
    nome: str | None = "João",
) -> dict:
    garantir_caixa_aberto(client)
    payload: dict[str, Any] = {"observacao": "Mesa 1"}
    if nome is not None:
        payload["nomeCliente"] = nome
    if cliente_id is not None:
        payload["clienteId"] = cliente_id

    comanda = client.post("/api/comandas", json=payload)
    assert comanda.status_code == 201
    produto = criar_produto(client, nome=f"Agua {comanda.json()['id']}")
    client.post(
        f"/api/comandas/{comanda.json()['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 2},
    )
    return client.get(f"/api/comandas/{comanda.json()['id']}").json()


def abrir_caixa(client: TestClient, valor_inicial: int = 100) -> dict:
    response = client.post("/api/caixas/abrir", json={"valorInicial": valor_inicial})
    assert response.status_code == 201
    return response.json()


def marcar_fiado(client: TestClient, comanda_id: int, cliente_id: int | None = None):
    payload = {}
    if cliente_id is not None:
        payload["clienteId"] = cliente_id
    return client.post(f"/api/comandas/{comanda_id}/fiado", json=payload)


def test_deve_criar_comanda_com_cliente_e_usar_nome_quando_nome_nao_enviado(
    test_engine,
):
    client = build_client(test_engine)
    abrir_caixa(client)
    cliente = criar_cliente(client)

    com_nome = client.post(
        "/api/comandas",
        json={"nomeCliente": "João mesa 2", "clienteId": cliente["id"]},
    )
    sem_nome = client.post("/api/comandas", json={"clienteId": cliente["id"]})

    assert com_nome.status_code == 201
    assert com_nome.json()["clienteId"] == cliente["id"]
    assert com_nome.json()["nomeCliente"] == "João mesa 2"
    assert com_nome.json()["nomeClienteSnapshot"] == "João"
    assert sem_nome.status_code == 201
    assert sem_nome.json()["nomeCliente"] == "João"


def test_deve_rejeitar_cliente_inexistente_ou_inativo_em_comanda(test_engine):
    client = build_client(test_engine)
    abrir_caixa(client)
    cliente = criar_cliente(client)
    client.patch(f"/api/clientes/{cliente['id']}/inativar")

    inexistente = client.post("/api/comandas", json={"clienteId": 999})
    inativo = client.post("/api/comandas", json={"clienteId": cliente["id"]})

    assert inexistente.status_code == 404
    assert inexistente.json()["code"] == "cliente_nao_encontrado"
    assert inativo.status_code == 400
    assert inativo.json()["code"] == "cliente_inativo"


def test_deve_vincular_cliente_a_comanda_aberta(test_engine):
    client = build_client(test_engine)
    abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = client.post("/api/comandas", json={"nomeCliente": "Balcão"}).json()

    response = client.patch(
        f"/api/comandas/{comanda['id']}/cliente",
        json={"clienteId": cliente["id"]},
    )

    assert response.status_code == 200
    assert response.json()["clienteId"] == cliente["id"]
    assert response.json()["nomeClienteSnapshot"] == "João"


def test_deve_rejeitar_vincular_cliente_a_comanda_nao_aberta(test_engine):
    client = build_client(test_engine)
    abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = client.post("/api/comandas", json={"nomeCliente": "Balcão"}).json()
    client.patch(f"/api/comandas/{comanda['id']}/cancelar")

    response = client.patch(
        f"/api/comandas/{comanda['id']}/cliente",
        json={"clienteId": cliente["id"]},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "comanda_nao_aberta"


def test_deve_marcar_comanda_aberta_com_consumo_como_pendente(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)

    response = marcar_fiado(client, comanda["id"], cliente["id"])

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDENTE"
    assert body["cliente"]["id"] == cliente["id"]
    assert body["caixaOrigemId"] == comanda["caixaOrigemId"]
    assert body["nomeComanda"] == comanda["nomeCliente"]
    assert body["nomeExibicao"] == "João"
    assert body["pendenteEm"] is not None
    assert body["vencimentoEm"] == str(date.today() + timedelta(days=7))
    assert body["pagamentos"] == []


def test_deve_rejeitar_marcar_fiado_sem_caixa_aberto(test_engine):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    fechar_caixa_direto(test_engine, caixa["id"])

    response = marcar_fiado(client, comanda["id"], cliente["id"])

    assert response.status_code == 400
    assert response.json()["code"] == "caixa_aberto_nao_encontrado"


def test_deve_exigir_cliente_para_fiado_e_permitir_cliente_ja_vinculado(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    sem_cliente = criar_comanda_com_consumo(client)
    com_cliente = criar_comanda_com_consumo(client, cliente_id=cliente["id"], nome=None)

    rejeitado = marcar_fiado(client, sem_cliente["id"])
    aceito = marcar_fiado(client, com_cliente["id"])

    assert rejeitado.status_code == 400
    assert rejeitado.json()["code"] == "cliente_obrigatorio_para_fiado"
    assert aceito.status_code == 200
    assert aceito.json()["status"] == "PENDENTE"


def test_deve_validar_vencimento_comanda_vazia_status_e_cliente_inativo(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    garantir_caixa_aberto(client)
    comanda_vazia = client.post("/api/comandas", json={"nomeCliente": "Vazia"}).json()

    vencimento_passado = client.post(
        f"/api/comandas/{criar_comanda_com_consumo(client)['id']}/fiado",
        json={
            "clienteId": cliente["id"],
            "vencimentoEm": str(date.today() - timedelta(days=1)),
        },
    )
    vazia = marcar_fiado(client, comanda_vazia["id"], cliente["id"])
    cancelada = criar_comanda_com_consumo(client)
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")
    status_invalido = marcar_fiado(client, cancelada["id"], cliente["id"])
    client.patch(f"/api/clientes/{cliente['id']}/inativar")
    inativo = marcar_fiado(
        client, criar_comanda_com_consumo(client)["id"], cliente["id"]
    )

    assert vencimento_passado.status_code == 400
    assert vencimento_passado.json()["code"] == "vencimento_invalido"
    assert vazia.status_code == 400
    assert vazia.json()["code"] == "comanda_sem_consumo"
    assert status_invalido.status_code == 400
    assert status_invalido.json()["code"] == "comanda_nao_aberta"
    assert inativo.status_code == 400
    assert inativo.json()["code"] == "cliente_inativo"


def test_deve_listar_pendencias_vencidas_e_consultar_por_comanda(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    vencimento = date.today()
    client.post(
        f"/api/comandas/{comanda['id']}/fiado",
        json={"clienteId": cliente["id"], "vencimentoEm": str(vencimento)},
    )

    pendencias = client.get("/api/fiados")
    vencidas = client.get("/api/fiados/vencidos")
    detalhe = client.get(f"/api/fiados/{comanda['id']}")
    historico = client.get(f"/api/clientes/{cliente['id']}/pendencias")

    assert pendencias.status_code == 200
    assert [item["comandaId"] for item in pendencias.json()] == [comanda["id"]]
    assert vencidas.status_code == 200
    assert vencidas.json() == []
    assert detalhe.status_code == 200
    assert detalhe.json()["comandaId"] == comanda["id"]
    assert detalhe.json()["pendenteEm"] is not None
    assert detalhe.json()["nomeComanda"] == comanda["nomeCliente"]
    assert detalhe.json()["nomeExibicao"] == "João"
    assert historico.status_code == 200
    assert historico.json()["totalPendente"] == "20.00"


def test_deve_quitar_pendencia_com_dinheiro_e_somar_no_caixa(test_engine):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    marcar_fiado(client, comanda["id"], cliente["id"])

    response = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "DINHEIRO", "valorPago": comanda["total"]},
    )
    detalhe_caixa = client.get(f"/api/caixas/{caixa['id']}").json()

    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"
    assert response.json()["fechadaEm"] is not None
    assert response.json()["pendenteEm"] is not None
    assert response.json()["vencimentoEm"] is not None
    assert response.json()["pagamentos"][0]["caixaId"] == caixa["id"]
    assert _money(detalhe_caixa["dinheiroEsperado"]) == Decimal("120.00")


def test_deve_quitar_pendencia_mesmo_com_cliente_inativo(test_engine):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    pendencia = marcar_fiado(client, comanda["id"], cliente["id"]).json()
    client.patch(f"/api/clientes/{cliente['id']}/inativar")

    response = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FECHADA"
    assert response.json()["pendenteEm"] == pendencia["pendenteEm"]
    assert response.json()["vencimentoEm"] == pendencia["vencimentoEm"]
    assert response.json()["pagamentos"][0]["caixaId"] == caixa["id"]


def test_deve_mostrar_pendencias_de_cliente_inativo(test_engine):
    client = build_client(test_engine)
    abrir_caixa(client)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    marcar_fiado(client, comanda["id"], cliente["id"])
    client.patch(f"/api/clientes/{cliente['id']}/inativar")

    historico = client.get(f"/api/clientes/{cliente['id']}/pendencias")
    fiados = client.get("/api/fiados")
    detalhe = client.get(f"/api/fiados/{comanda['id']}")

    assert historico.status_code == 200
    assert historico.json()["pendencias"][0]["comandaId"] == comanda["id"]
    assert fiados.status_code == 200
    assert fiados.json()[0]["comandaId"] == comanda["id"]
    assert detalhe.status_code == 200
    assert detalhe.json()["comandaId"] == comanda["id"]


def test_deve_quitar_pendencia_com_pix_e_cartao_sem_somar_dinheiro(test_engine):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    cliente = criar_cliente(client)
    pix = criar_comanda_com_consumo(client)
    cartao = criar_comanda_com_consumo(client)
    marcar_fiado(client, pix["id"], cliente["id"])
    marcar_fiado(client, cartao["id"], cliente["id"])

    pix_response = client.post(
        f"/api/fiados/{pix['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": pix["total"]},
    )
    cartao_response = client.post(
        f"/api/fiados/{cartao['id']}/quitar",
        json={"formaPagamento": "CARTAO", "valorPago": cartao["total"]},
    )
    detalhe_caixa = client.get(f"/api/caixas/{caixa['id']}").json()

    assert pix_response.status_code == 200
    assert cartao_response.status_code == 200
    assert _money(detalhe_caixa["dinheiroEsperado"]) == Decimal("100.00")


def test_deve_validar_quitacao(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    comanda = criar_comanda_com_consumo(client)
    marcar_fiado(client, comanda["id"], cliente["id"])
    caixa = client.get("/api/caixas/aberto").json()
    fechar_caixa_direto(test_engine, caixa["id"])

    sem_caixa = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )
    abrir_caixa(client)
    fiado = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "FIADO", "valorPago": comanda["total"]},
    )
    valor_diferente = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"] + 1},
    )

    assert sem_caixa.status_code == 400
    assert sem_caixa.json()["code"] == "caixa_aberto_nao_encontrado"
    assert fiado.status_code == 400
    assert fiado.json()["code"] == "fiado_nao_pode_quitar_fiado"
    assert valor_diferente.status_code == 400
    assert valor_diferente.json()["code"] == "valor_pago_invalido"


def test_deve_bloquear_fechamento_de_caixa_com_comanda_aberta(test_engine):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    aberta = client.post("/api/comandas", json={"nomeCliente": "Aberta"}).json()

    response = client.post(
        f"/api/caixas/{caixa['id']}/fechar",
        json={"dinheiroInformado": 100},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "existem_comandas_abertas"
    assert response.json()["details"][0]["id"] == aberta["id"]


def test_deve_permitir_fechar_caixa_com_comanda_pendente_fechada_ou_cancelada(
    test_engine,
):
    client = build_client(test_engine)
    caixa = abrir_caixa(client)
    cliente = criar_cliente(client)
    pendente = criar_comanda_com_consumo(client)
    marcar_fiado(client, pendente["id"], cliente["id"])
    fechada = criar_comanda_com_consumo(client)
    client.post(
        f"/api/comandas/{fechada['id']}/fechar",
        json={"formaPagamento": "PIX", "valorPago": fechada["total"]},
    )
    cancelada = client.post("/api/comandas", json={"nomeCliente": "Cancelada"}).json()
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")

    response = client.post(
        f"/api/caixas/{caixa['id']}/fechar",
        json={"dinheiroInformado": 100},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FECHADO"
