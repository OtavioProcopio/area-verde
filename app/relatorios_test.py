from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api import create_app
from core.domain.models import Comanda, MovimentoEstoque, Produto


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def _money(value) -> Decimal:
    return Decimal(str(value))


def _abrir_caixa(client: TestClient, valor_inicial: int = 100) -> dict:
    response = client.post("/api/caixas/abrir", json={"valorInicial": valor_inicial})
    assert response.status_code == 201
    return response.json()


def _fechar_caixa(client: TestClient, caixa_id: int, dinheiro: int = 100) -> dict:
    response = client.post(
        f"/api/caixas/{caixa_id}/fechar",
        json={"dinheiroInformado": dinheiro},
    )
    assert response.status_code == 200
    return response.json()


def _criar_cliente(client: TestClient, nome: str = "João Cliente") -> dict:
    sufixo = nome.replace(" ", "").lower()
    response = client.post(
        "/api/clientes",
        json={
            "nome": nome,
            "apelido": nome.split()[0],
            "telefone": f"16{sufixo}"[:40],
        },
    )
    assert response.status_code == 201
    return response.json()


def _criar_produto(
    client: TestClient,
    nome: str,
    preco: int = 10,
    controla_estoque: bool = False,
    quantidade_estoque: int = 0,
    estoque_minimo: int = 0,
    tipo_produto: str = "SIMPLES",
    unidade_estoque: str = "UNIDADE",
    quantidade_baixa_por_venda: int = 1,
) -> dict:
    categoria = client.post(
        "/api/categorias",
        json={"nome": f"Categoria {nome}"},
    )
    assert categoria.status_code == 201
    response = client.post(
        "/api/produtos",
        json={
            "categoriaId": categoria.json()["id"],
            "nome": nome,
            "precoVenda": preco,
            "tipoProduto": tipo_produto,
            "controlaEstoque": controla_estoque,
            "quantidadeEstoque": quantidade_estoque,
            "quantidadeBaixaPorVenda": (
                quantidade_baixa_por_venda if controla_estoque else None
            ),
            "estoqueMinimo": estoque_minimo,
            "unidadeEstoque": unidade_estoque if controla_estoque else None,
        },
    )
    assert response.status_code == 201
    return response.json()


def _adicionar_componente(
    client: TestClient,
    produto_pai_id: int,
    produto_componente_id: int,
    quantidade_baixa: int = 50,
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


def _criar_comanda(
    client: TestClient,
    nome: str,
    produto: dict,
    quantidade: int = 2,
    cliente_id: int | None = None,
) -> dict:
    payload: dict[str, Any] = {"nomeCliente": nome}
    if cliente_id is not None:
        payload["clienteId"] = cliente_id
    comanda = client.post("/api/comandas", json=payload)
    assert comanda.status_code == 201
    item = client.post(
        f"/api/comandas/{comanda.json()['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": quantidade},
    )
    assert item.status_code == 200
    return client.get(f"/api/comandas/{comanda.json()['id']}").json()


def _fechar_comanda(client: TestClient, comanda: dict, forma: str = "PIX") -> dict:
    response = client.post(
        f"/api/comandas/{comanda['id']}/fechar",
        json={"formaPagamento": forma, "valorPago": comanda["total"]},
    )
    assert response.status_code == 200
    return response.json()


def _marcar_fiado(client: TestClient, comanda: dict, cliente: dict) -> dict:
    response = client.post(
        f"/api/comandas/{comanda['id']}/fiado",
        json={"clienteId": cliente["id"]},
    )
    assert response.status_code == 200
    return response.json()


def _set_comanda_dates(
    test_engine,
    comanda_id: int,
    aberta_em: datetime | None = None,
    pendente_em: datetime | None = None,
    vencimento_em: date | None = None,
) -> None:
    with Session(test_engine) as session:
        comanda = session.get(Comanda, comanda_id)
        assert comanda is not None
        if aberta_em is not None:
            comanda.aberta_em = aberta_em
        if pendente_em is not None:
            comanda.pendente_em = pendente_em
        if vencimento_em is not None:
            comanda.vencimento_em = vencimento_em
        session.add(comanda)
        session.commit()


def _set_estoque(test_engine, produto_id: int, quantidade: str, minimo: str) -> None:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        produto.quantidade_estoque = Decimal(quantidade)
        produto.estoque_minimo = Decimal(minimo)
        session.add(produto)
        session.commit()


def _set_movimentos_dates(test_engine, produto_id: int, criado_em: datetime) -> None:
    with Session(test_engine) as session:
        movimentos = session.exec(
            select(MovimentoEstoque).where(MovimentoEstoque.produto_id == produto_id)
        )
        for movimento in movimentos:
            movimento.criado_em = criado_em
            session.add(movimento)
        session.commit()


def test_deve_retornar_relatorio_diario_sem_caixa_com_totais_zerados(test_engine):
    client = build_client(test_engine)

    response = client.get("/api/relatorios/diario")

    assert response.status_code == 200
    body = response.json()
    assert body["caixa"] is None
    assert body["vendas"]["totalVendido"] == "0.00"
    assert body["vendas"]["totalRecebido"] == "0.00"
    assert body["comandas"]["abertas"] == 0


def test_deve_retornar_relatorio_diario_com_caixa_aberto(test_engine):
    client = build_client(test_engine)
    caixa = _abrir_caixa(client)

    response = client.get("/api/relatorios/diario")

    assert response.status_code == 200
    assert response.json()["caixa"]["id"] == caixa["id"]
    assert response.json()["caixa"]["status"] == "ABERTO"


def test_deve_retornar_relatorio_diario_com_caixa_fechado(test_engine):
    client = build_client(test_engine)
    caixa = _abrir_caixa(client)
    _fechar_caixa(client, caixa["id"], dinheiro=100)

    response = client.get(f"/api/relatorios/diario?data={date.today()}")

    assert response.status_code == 200
    assert response.json()["caixa"]["status"] == "FECHADO"


def test_deve_somar_pagamentos_por_forma_e_separar_venda_recebimento(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    produto = _criar_produto(client, "Agua")
    dinheiro = _criar_comanda(client, "Dinheiro", produto, quantidade=1)
    pix = _criar_comanda(client, "Pix", produto, quantidade=2)
    cartao = _criar_comanda(client, "Cartao", produto, quantidade=3)
    cliente = _criar_cliente(client)
    fiado = _criar_comanda(client, "Fiado", produto, quantidade=4)
    _fechar_comanda(client, dinheiro, "DINHEIRO")
    _fechar_comanda(client, pix, "PIX")
    _fechar_comanda(client, cartao, "CARTAO")
    _marcar_fiado(client, fiado, cliente)

    response = client.get("/api/relatorios/diario")

    assert response.status_code == 200
    body = response.json()
    assert _money(body["pagamentos"]["dinheiro"]) == Decimal("10.00")
    assert _money(body["pagamentos"]["pix"]) == Decimal("20.00")
    assert _money(body["pagamentos"]["cartao"]) == Decimal("30.00")
    assert _money(body["vendas"]["totalVendido"]) == Decimal("100.00")
    assert _money(body["vendas"]["totalRecebido"]) == Decimal("60.00")
    assert _money(body["vendas"]["totalFiadoGerado"]) == Decimal("40.00")
    assert _money(body["vendas"]["totalPendenteAtual"]) == Decimal("40.00")


def test_deve_incluir_fiado_quitado_e_contar_comandas_estoque(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    cliente = _criar_cliente(client)
    produto = _criar_produto(client, "Fiado Quitado")
    baixo = _criar_produto(
        client,
        "Baixo",
        controla_estoque=True,
        quantidade_estoque=5,
        estoque_minimo=10,
    )
    negativo = _criar_produto(
        client,
        "Negativo",
        controla_estoque=True,
        quantidade_estoque=0,
        estoque_minimo=0,
    )
    _set_estoque(test_engine, negativo["id"], "-1.000", "0.000")
    pendente = _criar_comanda(client, "Pendente", produto, quantidade=1)
    quitado = _criar_comanda(client, "Quitado", produto, quantidade=2)
    cancelada = client.post("/api/comandas", json={"nomeCliente": "Cancelada"}).json()
    _marcar_fiado(client, pendente, cliente)
    _marcar_fiado(client, quitado, cliente)
    client.post(
        f"/api/fiados/{quitado['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": quitado["total"]},
    )
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")

    response = client.get("/api/relatorios/diario")

    assert response.status_code == 200
    body = response.json()
    assert body["comandas"]["fechadas"] == 1
    assert body["comandas"]["pendentes"] == 1
    assert body["comandas"]["canceladas"] == 1
    assert _money(body["fiados"]["quitadosNoDia"]) == Decimal("20.00")
    assert body["estoque"]["produtosComEstoqueBaixo"] >= 1
    assert body["estoque"]["produtosComEstoqueNegativo"] == 1
    assert baixo["id"] is not None


def test_deve_contar_fiado_gerado_mesmo_quando_quitado_no_mesmo_dia(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    cliente = _criar_cliente(client)
    produto = _criar_produto(client, "Fiado Gerado Quitado")
    comanda = _criar_comanda(client, "Fiado quitado", produto, quantidade=4)
    _marcar_fiado(client, comanda, cliente)

    quitacao = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )
    response = client.get("/api/relatorios/diario")

    assert quitacao.status_code == 200
    assert response.status_code == 200
    body = response.json()
    assert _money(body["fiados"]["geradosNoDia"]) == Decimal("40.00")
    assert _money(body["fiados"]["quitadosNoDia"]) == Decimal("40.00")
    assert _money(body["fiados"]["pendentesAtuais"]) == Decimal("0.00")


def test_deve_contar_fiado_gerado_no_relatorio_por_caixa_mesmo_quando_quitado(
    test_engine,
):
    client = build_client(test_engine)
    caixa = _abrir_caixa(client)
    cliente = _criar_cliente(client)
    produto = _criar_produto(client, "Fiado Caixa Quitado")
    comanda = _criar_comanda(client, "Fiado caixa", produto, quantidade=4)
    _marcar_fiado(client, comanda, cliente)

    quitacao = client.post(
        f"/api/fiados/{comanda['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": comanda["total"]},
    )
    response = client.get(f"/api/relatorios/caixas/{caixa['id']}")

    assert quitacao.status_code == 200
    assert response.status_code == 200
    body = response.json()
    assert _money(body["fiados"]["geradosNoDia"]) == Decimal("40.00")
    assert _money(body["fiados"]["quitadosNoDia"]) == Decimal("40.00")


def test_deve_considerar_pendente_em_para_fiado_gerado(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    cliente = _criar_cliente(client)
    produto = _criar_produto(client, "Fiado Data")
    comanda = _criar_comanda(client, "Ontem", produto, quantidade=1)
    _marcar_fiado(client, comanda, cliente)
    _set_comanda_dates(
        test_engine,
        comanda["id"],
        aberta_em=datetime.now() - timedelta(days=1),
        pendente_em=datetime.now(),
    )

    response = client.get(f"/api/relatorios/diario?data={date.today()}")

    assert response.status_code == 200
    assert _money(response.json()["fiados"]["geradosNoDia"]) == Decimal("10.00")
    assert response.json()["comandas"]["pendentes"] == 0


def test_deve_retornar_relatorio_por_caixa_e_consolidar_dados(test_engine):
    client = build_client(test_engine)
    caixa = _abrir_caixa(client)
    client.post(f"/api/caixas/{caixa['id']}/reforcos", json={"valor": 50})
    client.post(f"/api/caixas/{caixa['id']}/sangrias", json={"valor": 30})
    produto = _criar_produto(client, "Cerveja")
    comanda = _criar_comanda(client, "Mesa", produto, quantidade=3)
    _fechar_comanda(client, comanda, "DINHEIRO")

    response = client.get(f"/api/relatorios/caixas/{caixa['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["caixa"]["id"] == caixa["id"]
    assert _money(body["pagamentos"]["dinheiro"]) == Decimal("30.00")
    assert _money(body["movimentos"]["reforcos"]) == Decimal("50.00")
    assert _money(body["movimentos"]["sangrias"]) == Decimal("30.00")
    assert body["comandas"]["fechadas"] == 1
    assert body["produtosMaisVendidos"][0]["produtoId"] == produto["id"]


def test_deve_retornar_erro_para_caixa_inexistente(test_engine):
    client = build_client(test_engine)

    response = client.get("/api/relatorios/caixas/999")

    assert response.status_code == 404
    assert response.json()["code"] == "caixa_nao_encontrado"


def test_deve_listar_produtos_mais_vendidos_e_ignorar_status_invalidos(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    produto_a = _criar_produto(client, "Produto A")
    produto_b = _criar_produto(client, "Produto B")
    fechada = _criar_comanda(client, "Fechada", produto_a, quantidade=3)
    pendente = _criar_comanda(client, "Pendente", produto_b, quantidade=2)
    aberta = _criar_comanda(client, "Aberta", produto_a, quantidade=10)
    cancelada = _criar_comanda(client, "Cancelada", produto_a, quantidade=9)
    cliente = _criar_cliente(client)
    _fechar_comanda(client, fechada, "PIX")
    _marcar_fiado(client, pendente, cliente)
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")

    response = client.get("/api/relatorios/produtos-mais-vendidos?limite=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["produtoId"] == produto_a["id"]
    assert _money(body[0]["quantidadeVendida"]) == Decimal("3.000")
    assert aberta["id"] is not None


def test_produto_composto_aparece_como_vendido_sem_componentes(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    componente_a = _criar_produto(
        client,
        "Pinga A Relatorio",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
        quantidade_baixa_por_venda=50,
    )
    componente_b = _criar_produto(
        client,
        "Pinga B Relatorio",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
        quantidade_baixa_por_venda=50,
    )
    composto = _criar_produto(
        client,
        "Dose Mista Relatorio",
        preco=18,
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    simples = _criar_produto(client, "Agua Relatorio", preco=5)
    _adicionar_componente(client, composto["id"], componente_a["id"], 50)
    _adicionar_componente(client, composto["id"], componente_b["id"], 25)
    comanda_composta = _criar_comanda(client, "Composto", composto, quantidade=2)
    comanda_simples = _criar_comanda(client, "Simples", simples, quantidade=1)
    _fechar_comanda(client, comanda_composta)
    _fechar_comanda(client, comanda_simples)

    response = client.get("/api/relatorios/produtos-mais-vendidos")

    assert response.status_code == 200
    ids = {item["produtoId"] for item in response.json()}
    composto_item = next(
        item for item in response.json() if item["produtoId"] == composto["id"]
    )
    simples_item = next(
        item for item in response.json() if item["produtoId"] == simples["id"]
    )
    assert _money(composto_item["quantidadeVendida"]) == Decimal("2.000")
    assert _money(composto_item["valorTotal"]) == Decimal("36.00")
    assert _money(simples_item["quantidadeVendida"]) == Decimal("1.000")
    assert componente_a["id"] not in ids
    assert componente_b["id"] not in ids


def test_comanda_cancelada_com_composto_nao_entra_em_produtos_mais_vendidos(
    test_engine,
):
    client = build_client(test_engine)
    _abrir_caixa(client)
    componente = _criar_produto(
        client,
        "Pinga Cancelada",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
    )
    composto = _criar_produto(
        client,
        "Dose Cancelada",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    _adicionar_componente(client, composto["id"], componente["id"], 50)
    comanda = _criar_comanda(client, "Cancelada composto", composto, quantidade=1)
    client.patch(f"/api/comandas/{comanda['id']}/cancelar")

    response = client.get("/api/relatorios/produtos-mais-vendidos")

    assert response.status_code == 200
    assert response.json() == []


def test_deve_rejeitar_limite_invalido_e_periodo_invalido(test_engine):
    client = build_client(test_engine)

    limite = client.get("/api/relatorios/produtos-mais-vendidos?limite=0")
    periodo = client.get(
        "/api/relatorios/comandas?dataInicio=2026-05-29&dataFim=2026-05-28"
    )

    assert limite.status_code == 400
    assert limite.json()["code"] == "parametro_invalido"
    assert periodo.status_code == 400
    assert periodo.json()["code"] == "periodo_invalido"


def test_deve_retornar_resumo_de_fiados_com_filtros(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    cliente = _criar_cliente(client)
    outro = _criar_cliente(client, nome="Maria")
    produto = _criar_produto(client, "Fiado")
    pendente = _criar_comanda(client, "Pendente", produto, quantidade=1)
    vencida = _criar_comanda(client, "Vencida", produto, quantidade=2)
    quitada = _criar_comanda(client, "Quitada", produto, quantidade=3)
    outra = _criar_comanda(client, "Outra", produto, quantidade=4)
    _marcar_fiado(client, pendente, cliente)
    _marcar_fiado(client, vencida, cliente)
    _marcar_fiado(client, quitada, cliente)
    _marcar_fiado(client, outra, outro)
    _set_comanda_dates(
        test_engine,
        vencida["id"],
        pendente_em=datetime.now() - timedelta(days=2),
        vencimento_em=date.today() - timedelta(days=1),
    )
    client.post(
        f"/api/fiados/{quitada['id']}/quitar",
        json={"formaPagamento": "PIX", "valorPago": quitada["total"]},
    )

    response = client.get(f"/api/relatorios/fiados?clienteId={cliente['id']}")
    vencidos = client.get("/api/relatorios/fiados?status=vencidos")
    quitados = client.get("/api/relatorios/fiados?status=quitados")

    assert response.status_code == 200
    assert response.json()["resumo"]["quantidadePendencias"] == 2
    assert response.json()["resumo"]["quantidadeVencidas"] == 1
    assert _money(response.json()["resumo"]["totalQuitadoPeriodo"]) == Decimal("30.00")
    assert len(response.json()["pendencias"]) == 2
    assert vencidos.status_code == 200
    assert vencidos.json()["pendencias"][0]["comandaId"] == vencida["id"]
    assert quitados.status_code == 200
    assert quitados.json()["pendencias"][0]["comandaId"] == quitada["id"]


def test_deve_retornar_relatorio_estoque_e_filtrar_tipo(test_engine):
    client = build_client(test_engine)
    baixo = _criar_produto(
        client,
        "Estoque Baixo",
        controla_estoque=True,
        quantidade_estoque=3,
        estoque_minimo=5,
    )
    negativo = _criar_produto(
        client,
        "Estoque Negativo",
        controla_estoque=True,
        quantidade_estoque=0,
        estoque_minimo=0,
    )
    _set_estoque(test_engine, negativo["id"], "-2.000", "0.000")

    todos = client.get("/api/relatorios/estoque")
    apenas_baixo = client.get("/api/relatorios/estoque?tipo=baixo")
    apenas_negativo = client.get("/api/relatorios/estoque?tipo=negativo")
    invalido = client.get("/api/relatorios/estoque?tipo=critico")

    assert todos.status_code == 200
    assert todos.json()["resumo"]["produtosControlados"] == 2
    assert todos.json()["baixo"][0]["produtoId"] == baixo["id"]
    assert todos.json()["negativo"][0]["produtoId"] == negativo["id"]
    assert apenas_baixo.json()["negativo"] == []
    assert apenas_negativo.json()["baixo"] == []
    assert invalido.status_code == 400
    assert invalido.json()["code"] == "parametro_invalido"


def test_relatorio_estoque_considera_componentes_controlados(test_engine):
    client = build_client(test_engine)
    componente_baixo = _criar_produto(
        client,
        "Componente Baixo",
        controla_estoque=True,
        quantidade_estoque=2,
        estoque_minimo=5,
        unidade_estoque="ML",
    )
    componente_negativo = _criar_produto(
        client,
        "Componente Negativo",
        controla_estoque=True,
        quantidade_estoque=0,
        estoque_minimo=0,
        unidade_estoque="ML",
    )
    composto = _criar_produto(
        client,
        "Composto Sem Controle",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    _set_estoque(test_engine, componente_negativo["id"], "-1.000", "0.000")

    response = client.get("/api/relatorios/estoque")

    assert response.status_code == 200
    body = response.json()
    ids_baixo = {item["produtoId"] for item in body["baixo"]}
    ids_negativo = {item["produtoId"] for item in body["negativo"]}
    assert body["resumo"]["produtosControlados"] == 2
    assert componente_baixo["id"] in ids_baixo
    assert componente_negativo["id"] in ids_negativo
    assert composto["id"] not in ids_baixo
    assert composto["id"] not in ids_negativo


def test_deve_retornar_estoque_consumido_vazio_e_rejeitar_periodo_invalido(
    test_engine,
):
    client = build_client(test_engine)

    vazio = client.get("/api/relatorios/estoque-consumido")
    invalido = client.get(
        "/api/relatorios/estoque-consumido?dataInicio=2026-05-29&dataFim=2026-05-28"
    )

    assert vazio.status_code == 200
    assert vazio.json() == []
    assert invalido.status_code == 400
    assert invalido.json()["code"] == "periodo_invalido"


def test_estoque_consumido_consolida_simples_e_componentes_de_composto(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    simples = _criar_produto(
        client,
        "Cerveja Consumo",
        controla_estoque=True,
        quantidade_estoque=20,
        quantidade_baixa_por_venda=1,
    )
    componente_a = _criar_produto(
        client,
        "Pinga A Consumo",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
    )
    componente_b = _criar_produto(
        client,
        "Pinga B Consumo",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
    )
    composto = _criar_produto(
        client,
        "Dose Mista Consumo",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    sem_controle = _criar_produto(client, "Servico Consumo", controla_estoque=False)
    _adicionar_componente(client, composto["id"], componente_a["id"], 50)
    _adicionar_componente(client, composto["id"], componente_b["id"], 25)
    _criar_comanda(client, "Simples consumo", simples, quantidade=3)
    _criar_comanda(client, "Composto consumo", composto, quantidade=2)
    _criar_comanda(client, "Servico consumo", sem_controle, quantidade=4)

    response = client.get("/api/relatorios/estoque-consumido")

    assert response.status_code == 200
    body = {item["produtoId"]: item for item in response.json()}
    assert body[simples["id"]]["quantidadeConsumida"] == "3.000"
    assert body[simples["id"]]["unidadeEstoque"] == "UNIDADE"
    assert body[componente_a["id"]]["quantidadeConsumida"] == "100.000"
    assert body[componente_a["id"]]["unidadeEstoque"] == "ML"
    assert body[componente_b["id"]]["quantidadeConsumida"] == "50.000"
    assert composto["id"] not in body
    assert sem_controle["id"] not in body


def test_estoque_consumido_desconta_cancelamento_e_filtra_periodo(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    antigo = _criar_produto(
        client,
        "Cerveja Antiga",
        controla_estoque=True,
        quantidade_estoque=20,
    )
    componente = _criar_produto(
        client,
        "Pinga Liquida",
        controla_estoque=True,
        quantidade_estoque=1000,
        unidade_estoque="ML",
    )
    composto = _criar_produto(
        client,
        "Dose Liquida",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    _adicionar_componente(client, composto["id"], componente["id"], 50)
    _criar_comanda(client, "Antiga", antigo, quantidade=2)
    _set_movimentos_dates(test_engine, antigo["id"], datetime.now() - timedelta(days=3))
    _criar_comanda(client, "Liquida", composto, quantidade=2)
    cancelada = _criar_comanda(client, "Cancelada consumo", composto, quantidade=1)
    client.patch(f"/api/comandas/{cancelada['id']}/cancelar")

    hoje = date.today()
    response = client.get(
        f"/api/relatorios/estoque-consumido?dataInicio={hoje}&dataFim={hoje}"
    )

    assert response.status_code == 200
    body = {item["produtoId"]: item for item in response.json()}
    assert antigo["id"] not in body
    assert body[componente["id"]]["quantidadeConsumida"] == "100.000"


def test_deve_retornar_comandas_por_status_e_filtrar(test_engine):
    client = build_client(test_engine)
    _abrir_caixa(client)
    produto = _criar_produto(client, "Comandas")
    fechada = _criar_comanda(client, "Fechada", produto, quantidade=1)
    aberta = _criar_comanda(client, "Aberta", produto, quantidade=2)
    _fechar_comanda(client, fechada, "PIX")
    antiga = datetime.now() - timedelta(days=3)
    _set_comanda_dates(test_engine, aberta["id"], aberta_em=antiga)

    todas = client.get("/api/relatorios/comandas")
    filtrada = client.get("/api/relatorios/comandas?status=FECHADA")
    periodo = client.get(
        f"/api/relatorios/comandas?dataInicio={date.today()}&dataFim={date.today()}"
    )

    assert todas.status_code == 200
    assert todas.json()["resumo"]["total"] == 2
    assert filtrada.json()["resumo"]["fechadas"] == 1
    assert filtrada.json()["resumo"]["abertas"] == 0
    assert periodo.json()["resumo"]["total"] == 1
