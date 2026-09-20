from datetime import date, timedelta
from decimal import Decimal

from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlmodel import Session

from api import create_app
from core.domain.models import Comanda, Produto


def build_client(test_engine, abrir_caixa: bool = False) -> TestClient:
    app = create_app()
    app.container.engine.override(  # type: ignore[attr-defined]
        providers.Object(test_engine)
    )
    client = TestClient(app)
    if abrir_caixa:
        response = client.post("/api/caixas/abrir", json={"valorInicial": 100})
        assert response.status_code == 201
    return client


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
    quantidade_baixa: float,
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


def create_cliente(client: TestClient, nome: str = "João da Oficina") -> dict:
    response = client.post(
        "/api/clientes",
        json={"nome": nome, "apelido": "João", "telefone": "16999999999"},
    )
    assert response.status_code == 201
    return response.json()


def get_produto(test_engine, produto_id: int) -> Produto:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        return produto


def get_comanda(test_engine, comanda_id: int) -> Comanda:
    with Session(test_engine) as session:
        comanda = session.get(Comanda, comanda_id)
        assert comanda is not None
        return comanda


def test_get_configuracao_cria_padrao_sem_expor_hash(test_engine):
    client = build_client(test_engine)

    response = client.get("/api/configuracoes")

    assert response.status_code == 200
    body = response.json()
    assert body["nomeBar"] == "Area Verde"
    assert body["diasParaAlertaFiado"] == 7
    assert body["permitirEstoqueNegativo"] is True
    assert body["senhaConfigurada"] is False
    assert "senhaAcessoHash" not in body


def test_put_e_patch_configuracao_atualizam_parametros(test_engine):
    client = build_client(test_engine)

    put_response = client.put(
        "/api/configuracoes",
        json={
            "nomeBar": "Area Verde Matriz",
            "diasParaAlertaFiado": 10,
            "permitirEstoqueNegativo": False,
            "observacao": "Configuração principal",
        },
    )

    assert put_response.status_code == 200
    assert put_response.json()["nomeBar"] == "Area Verde Matriz"
    assert put_response.json()["diasParaAlertaFiado"] == 10
    assert put_response.json()["permitirEstoqueNegativo"] is False

    patch_response = client.patch(
        "/api/configuracoes",
        json={"permitirEstoqueNegativo": True, "nomeBar": "Area Verde Centro"},
    )

    assert patch_response.status_code == 200
    body = patch_response.json()
    assert body["nomeBar"] == "Area Verde Centro"
    assert body["diasParaAlertaFiado"] == 10
    assert body["permitirEstoqueNegativo"] is True


def test_cors_permite_frontend_local(test_engine):
    client = build_client(test_engine)

    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_acesso_define_valida_e_altera_senha(test_engine):
    client = build_client(test_engine)

    sem_senha = client.post("/api/acesso/validar", json={"senha": "1234"})
    assert sem_senha.status_code == 400
    assert sem_senha.json()["code"] == "senha_nao_configurada"

    definir = client.put("/api/acesso/senha", json={"novaSenha": "1234"})
    assert definir.status_code == 200
    assert definir.json()["senhaConfigurada"] is True

    validar = client.post("/api/acesso/validar", json={"senha": "1234"})
    assert validar.status_code == 200
    assert validar.json() == {"valido": True}

    invalida = client.post("/api/acesso/validar", json={"senha": "9999"})
    assert invalida.status_code == 401
    assert invalida.json()["code"] == "senha_invalida"

    sem_atual = client.put("/api/acesso/senha", json={"novaSenha": "5678"})
    assert sem_atual.status_code == 400
    assert sem_atual.json()["code"] == "senha_atual_obrigatoria"

    troca = client.put(
        "/api/acesso/senha",
        json={"senhaAtual": "1234", "novaSenha": "5678"},
    )
    assert troca.status_code == 200

    validar_nova = client.post("/api/acesso/validar", json={"senha": "5678"})
    assert validar_nova.status_code == 200
    assert validar_nova.json() == {"valido": True}


def test_bloqueia_venda_com_estoque_negativo_quando_config_desabilita(test_engine):
    client = build_client(test_engine, abrir_caixa=True)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=1)
    comanda = client.post("/api/comandas", json={"nomeCliente": "João"}).json()

    config_response = client.patch(
        "/api/configuracoes",
        json={"permitirEstoqueNegativo": False},
    )
    assert config_response.status_code == 200

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 3},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "estoque_insuficiente"
    assert get_produto(test_engine, produto["id"]).quantidade_estoque == Decimal(
        "1.000"
    )


def test_bloqueia_composto_sem_persistencia_parcial_quando_ficaria_negativo(
    test_engine,
):
    client = build_client(test_engine, abrir_caixa=True)
    categoria = create_categoria(client)
    composto = create_produto(
        client,
        categoria["id"],
        nome="Dose Mista",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    componente_ok = create_produto(
        client,
        categoria["id"],
        nome="Pinga A",
        unidade_estoque="ML",
        quantidade_estoque=100,
        quantidade_baixa_por_venda=50,
    )
    componente_insuficiente = create_produto(
        client,
        categoria["id"],
        nome="Pinga B",
        unidade_estoque="ML",
        quantidade_estoque=10,
        quantidade_baixa_por_venda=50,
    )
    add_componente(client, composto["id"], componente_ok["id"], quantidade_baixa=50)
    add_componente(
        client,
        composto["id"],
        componente_insuficiente["id"],
        quantidade_baixa=50,
    )
    comanda = client.post("/api/comandas", json={"nomeCliente": "Maria"}).json()

    config_response = client.patch(
        "/api/configuracoes",
        json={"permitirEstoqueNegativo": False},
    )
    assert config_response.status_code == 200

    response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": composto["id"], "quantidade": 1},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "estoque_insuficiente"
    assert get_produto(test_engine, componente_ok["id"]).quantidade_estoque == Decimal(
        "100.000"
    )
    assert get_produto(
        test_engine, componente_insuficiente["id"]
    ).quantidade_estoque == Decimal("10.000")
    assert get_comanda(test_engine, comanda["id"]).total == Decimal("0.00")


def test_fiado_usa_dias_configurados_quando_vencimento_nao_informado(test_engine):
    client = build_client(test_engine, abrir_caixa=True)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)
    cliente = create_cliente(client)
    comanda = client.post(
        "/api/comandas",
        json={"nomeCliente": "João", "clienteId": cliente["id"]},
    ).json()
    item_response = client.post(
        f"/api/comandas/{comanda['id']}/itens",
        json={"produtoId": produto["id"], "quantidade": 1},
    )
    assert item_response.status_code == 200

    config_response = client.patch(
        "/api/configuracoes",
        json={"diasParaAlertaFiado": 10},
    )
    assert config_response.status_code == 200

    fiado_response = client.post(
        f"/api/comandas/{comanda['id']}/fiado",
        json={"clienteId": cliente["id"]},
    )

    assert fiado_response.status_code == 200
    assert fiado_response.json()["vencimentoEm"] == str(
        date.today() + timedelta(days=10)
    )
