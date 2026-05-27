from dependency_injector import providers
from fastapi.testclient import TestClient

from api import create_app


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def criar_cliente(
    client: TestClient,
    nome: str = "João da Oficina",
    apelido: str = "João",
) -> dict:
    response = client.post(
        "/api/clientes",
        json={
            "nome": nome,
            "apelido": apelido,
            "telefone": "16999999999",
            "observacao": "Paga no fim da semana",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_deve_criar_cliente_valido(test_engine):
    client = build_client(test_engine)

    response = client.post(
        "/api/clientes",
        json={
            "nome": "João da Oficina",
            "apelido": "João",
            "telefone": "16999999999",
            "observacao": "Cliente costuma pagar no fim da semana",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["nome"] == "João da Oficina"
    assert body["apelido"] == "João"
    assert body["telefone"] == "16999999999"
    assert body["observacao"] == "Cliente costuma pagar no fim da semana"
    assert body["ativo"] is True
    assert body["criadoEm"] is not None
    assert body["atualizadoEm"] is not None


def test_deve_rejeitar_cliente_sem_nome(test_engine):
    client = build_client(test_engine)

    vazio = client.post("/api/clientes", json={"nome": "   "})
    nulo = client.post("/api/clientes", json={"nome": None})

    assert vazio.status_code == 422
    assert vazio.json()["code"] == "dados_invalidos"
    assert nulo.status_code == 422
    assert nulo.json()["code"] == "dados_invalidos"


def test_deve_listar_buscar_filtrar_editar_ativar_e_inativar_cliente(test_engine):
    client = build_client(test_engine)
    cliente = criar_cliente(client)
    criar_cliente(client, nome="Maria do Caixa", apelido="Maria")

    detalhe = client.get(f"/api/clientes/{cliente['id']}")
    assert detalhe.status_code == 200
    assert detalhe.json()["id"] == cliente["id"]

    por_nome = client.get("/api/clientes?nome=joão")
    assert por_nome.status_code == 200
    assert [item["id"] for item in por_nome.json()] == [cliente["id"]]

    editado = client.put(
        f"/api/clientes/{cliente['id']}",
        json={"nome": "João Editado", "apelido": "Jota"},
    )
    assert editado.status_code == 200
    assert editado.json()["nome"] == "João Editado"

    inativo = client.patch(f"/api/clientes/{cliente['id']}/inativar")
    assert inativo.status_code == 200
    assert inativo.json()["ativo"] is False

    ativos = client.get("/api/clientes?ativo=true")
    assert ativos.status_code == 200
    assert cliente["id"] not in {item["id"] for item in ativos.json()}

    ativado = client.patch(f"/api/clientes/{cliente['id']}/ativar")
    assert ativado.status_code == 200
    assert ativado.json()["ativo"] is True


def test_deve_retornar_erro_para_cliente_inexistente(test_engine):
    client = build_client(test_engine)

    response = client.get("/api/clientes/999")

    assert response.status_code == 404
    assert response.json()["code"] == "cliente_nao_encontrado"
