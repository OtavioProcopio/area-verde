from dependency_injector import providers
from fastapi.testclient import TestClient

from api import create_app


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def create_categoria(client: TestClient, nome: str = "Drinks") -> dict:
    response = client.post("/api/categorias", json={"nome": nome})
    assert response.status_code == 201
    return response.json()


def create_produto(
    client: TestClient,
    categoria_id: int,
    nome: str,
    tipo_produto: str = "SIMPLES",
    controla_estoque: bool = True,
) -> dict:
    payload = {
        "nome": nome,
        "categoriaId": categoria_id,
        "precoVenda": 10,
        "tipoProduto": tipo_produto,
        "controlaEstoque": controla_estoque,
    }
    if controla_estoque:
        payload |= {
            "unidadeEstoque": "ML",
            "quantidadeEstoque": 1000,
            "quantidadeBaixaPorVenda": 50,
            "estoqueMinimo": 100,
        }

    response = client.post("/api/produtos", json=payload)
    assert response.status_code == 201
    return response.json()


def add_componente(
    client: TestClient,
    produto_pai_id: int,
    produto_componente_id: int,
    quantidade_baixa: int = 50,
):
    return client.post(
        f"/api/produtos/{produto_pai_id}/composicao/componentes",
        json={
            "produtoComponenteId": produto_componente_id,
            "quantidadeBaixa": quantidade_baixa,
        },
    )


def test_consulta_composicao_vazia_de_produto_composto(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    composto = create_produto(
        client,
        categoria["id"],
        "Dose Mista A+B",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )

    response = client.get(f"/api/produtos/{composto['id']}/composicao")

    assert response.status_code == 200
    assert response.json() == {
        "produtoId": composto["id"],
        "tipoProduto": "COMPOSTO",
        "componentes": [],
    }


def test_adiciona_edita_e_remove_componente(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    composto = create_produto(
        client,
        categoria["id"],
        "Dose Mista A+B",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    componente = create_produto(client, categoria["id"], "Pinga A")

    add_response = add_componente(client, composto["id"], componente["id"])

    assert add_response.status_code == 201
    componente_response = add_response.json()["componentes"][0]
    assert componente_response["produtoComponenteId"] == componente["id"]
    assert componente_response["nomeProdutoComponente"] == "Pinga A"
    assert componente_response["unidadeEstoque"] == "ML"
    assert componente_response["quantidadeBaixa"] == "50.000"

    update_response = client.put(
        f"/api/produtos/{composto['id']}/composicao/componentes/{componente['id']}",
        json={"quantidadeBaixa": 75},
    )
    assert update_response.status_code == 200
    assert update_response.json()["componentes"][0]["quantidadeBaixa"] == "75.000"

    delete_response = client.delete(
        f"/api/produtos/{composto['id']}/composicao/componentes/{componente['id']}"
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["componentes"] == []


def test_rejeita_componente_em_produto_simples_e_produtos_inexistentes(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    simples = create_produto(client, categoria["id"], "Dose simples")
    componente = create_produto(client, categoria["id"], "Pinga A")

    produto_simples = add_componente(client, simples["id"], componente["id"])
    assert produto_simples.status_code == 400
    assert produto_simples.json()["code"] == "produto_pai_deve_ser_composto"

    pai_inexistente = add_componente(client, 999, componente["id"])
    assert pai_inexistente.status_code == 404
    assert pai_inexistente.json()["code"] == "produto_pai_nao_encontrado"

    composto = create_produto(
        client,
        categoria["id"],
        "Dose Mista A+B",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    componente_inexistente = add_componente(client, composto["id"], 999)
    assert componente_inexistente.status_code == 404
    assert componente_inexistente.json()["code"] == "produto_componente_nao_encontrado"


def test_rejeita_componente_invalido_duplicado_e_quantidade(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    composto = create_produto(
        client,
        categoria["id"],
        "Dose Mista A+B",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    componente = create_produto(client, categoria["id"], "Pinga A")
    inativo = create_produto(client, categoria["id"], "Inativo")
    sem_estoque = create_produto(
        client,
        categoria["id"],
        "Taxa",
        controla_estoque=False,
    )
    composto_componente = create_produto(
        client,
        categoria["id"],
        "Outro composto",
        tipo_produto="COMPOSTO",
        controla_estoque=False,
    )
    client.patch(f"/api/produtos/{inativo['id']}/inativar")

    casos = [
        (inativo["id"], "produto_componente_inativo"),
        (sem_estoque["id"], "produto_componente_sem_controle_estoque"),
        (composto_componente["id"], "componente_composto_nao_permitido"),
        (composto["id"], "componente_igual_produto_pai"),
    ]

    for componente_id, code in casos:
        response = add_componente(client, composto["id"], componente_id)
        assert response.status_code == 400
        assert response.json()["code"] == code

    for quantidade in (0, -1):
        response = add_componente(
            client,
            composto["id"],
            componente["id"],
            quantidade_baixa=quantidade,
        )
        assert response.status_code == 400
        assert response.json()["code"] == "quantidade_baixa_invalida"

    response = add_componente(client, composto["id"], componente["id"])
    assert response.status_code == 201

    duplicado = add_componente(client, composto["id"], componente["id"])
    assert duplicado.status_code == 409
    assert duplicado.json()["code"] == "produto_componente_duplicado"
