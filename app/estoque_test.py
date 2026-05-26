from decimal import Decimal

from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlmodel import Session

from api import create_app
from core.domain.models import Produto


def build_client(test_engine):
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
    controla_estoque: bool = True,
    quantidade_estoque: float = 24,
    estoque_minimo: float = 6,
) -> dict:
    payload = {
        "nome": nome,
        "categoriaId": categoria_id,
        "precoVenda": 7.00,
        "controlaEstoque": controla_estoque,
    }
    if controla_estoque:
        payload |= {
            "unidadeEstoque": "UNIDADE",
            "quantidadeEstoque": quantidade_estoque,
            "quantidadeBaixaPorVenda": 1,
            "estoqueMinimo": estoque_minimo,
        }

    response = client.post("/api/produtos", json=payload)
    assert response.status_code == 201
    return response.json()


def set_quantidade_estoque(test_engine, produto_id: int, quantidade: Decimal) -> None:
    with Session(test_engine) as session:
        produto = session.get(Produto, produto_id)
        assert produto is not None
        produto.quantidade_estoque = quantidade
        session.add(produto)
        session.commit()


def test_consulta_estoque_lista_apenas_produtos_com_controle_e_filtra(test_engine):
    client = build_client(test_engine)
    cervejas = create_categoria(client, "Cervejas")
    doses = create_categoria(client, "Doses")
    cerveja = create_produto(
        client,
        cervejas["id"],
        nome="Cerveja lata",
        quantidade_estoque=24,
        estoque_minimo=6,
    )
    create_produto(
        client,
        doses["id"],
        nome="Dose de pinga",
        quantidade_estoque=150,
        estoque_minimo=200,
    )
    sem_controle = create_produto(
        client,
        cervejas["id"],
        nome="Taxa de serviço",
        controla_estoque=False,
    )

    response = client.get("/api/estoque")
    assert response.status_code == 200
    assert [produto["nome"] for produto in response.json()] == [
        "Cerveja lata",
        "Dose de pinga",
    ]
    assert sem_controle["nome"] not in [produto["nome"] for produto in response.json()]

    categoria_response = client.get(f"/api/estoque?categoriaId={cervejas['id']}")
    assert categoria_response.status_code == 200
    assert [produto["produtoId"] for produto in categoria_response.json()] == [
        cerveja["id"]
    ]

    nome_response = client.get("/api/estoque?nome=pinga")
    assert nome_response.status_code == 200
    assert [produto["nome"] for produto in nome_response.json()] == ["Dose de pinga"]

    client.patch(f"/api/produtos/{cerveja['id']}/inativar")
    ativo_response = client.get("/api/estoque?ativo=true")
    assert ativo_response.status_code == 200
    assert [produto["nome"] for produto in ativo_response.json()] == ["Dose de pinga"]


def test_consulta_estoque_indica_baixo_e_negativo(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    baixo = create_produto(
        client,
        categoria["id"],
        nome="Salgado",
        quantidade_estoque=5,
        estoque_minimo=5,
    )
    negativo = create_produto(
        client,
        categoria["id"],
        nome="Refrigerante",
        quantidade_estoque=1,
        estoque_minimo=3,
    )
    set_quantidade_estoque(test_engine, negativo["id"], Decimal("-2"))

    estoque_response = client.get("/api/estoque")
    assert estoque_response.status_code == 200
    por_nome = {produto["nome"]: produto for produto in estoque_response.json()}
    assert por_nome["Salgado"]["estoqueBaixo"] is True
    assert por_nome["Salgado"]["estoqueNegativo"] is False
    assert por_nome["Refrigerante"]["estoqueBaixo"] is True
    assert por_nome["Refrigerante"]["estoqueNegativo"] is True

    baixo_response = client.get("/api/estoque/baixo")
    assert baixo_response.status_code == 200
    assert {produto["produtoId"] for produto in baixo_response.json()} == {
        baixo["id"],
        negativo["id"],
    }

    negativo_response = client.get("/api/estoque/negativo")
    assert negativo_response.status_code == 200
    assert [produto["produtoId"] for produto in negativo_response.json()] == [
        negativo["id"]
    ]


def test_entrada_de_estoque_soma_atualiza_produto_e_registra_movimento(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)

    response = client.post(
        f"/api/estoque/produtos/{produto['id']}/entrada",
        json={"quantidade": 5, "observacao": "Compra do dia"},
    )

    assert response.status_code == 201
    movimento = response.json()
    assert movimento["produtoId"] == produto["id"]
    assert movimento["produtoNome"] == "Cerveja lata"
    assert movimento["tipo"] == "ENTRADA"
    assert movimento["origem"] == "ENTRADA_MANUAL"
    assert movimento["quantidade"] == 5.0
    assert movimento["estoqueAntes"] == 10.0
    assert movimento["estoqueDepois"] == 15.0
    assert movimento["observacao"] == "Compra do dia"

    produto_response = client.get(f"/api/produtos/{produto['id']}")
    assert produto_response.status_code == 200
    assert produto_response.json()["quantidadeEstoque"] == 15.0

    historico_response = client.get(f"/api/estoque/produtos/{produto['id']}/movimentos")
    assert historico_response.status_code == 200
    assert [item["id"] for item in historico_response.json()] == [movimento["id"]]


def test_entrada_de_estoque_rejeita_dados_invalidos(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"])
    inativo = create_produto(client, categoria["id"], nome="Inativo")
    sem_controle = create_produto(
        client,
        categoria["id"],
        nome="Sem controle",
        controla_estoque=False,
    )
    client.patch(f"/api/produtos/{inativo['id']}/inativar")

    zero_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/entrada",
        json={"quantidade": 0},
    )
    assert zero_response.status_code == 400
    assert zero_response.json()["code"] == "quantidade_invalida"

    negativa_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/entrada",
        json={"quantidade": -1},
    )
    assert negativa_response.status_code == 400
    assert negativa_response.json()["code"] == "quantidade_invalida"

    inexistente_response = client.post(
        "/api/estoque/produtos/999/entrada",
        json={"quantidade": 1},
    )
    assert inexistente_response.status_code == 404
    assert inexistente_response.json()["code"] == "produto_nao_encontrado"

    inativo_response = client.post(
        f"/api/estoque/produtos/{inativo['id']}/entrada",
        json={"quantidade": 1},
    )
    assert inativo_response.status_code == 400
    assert inativo_response.json()["code"] == "produto_inativo"

    sem_controle_response = client.post(
        f"/api/estoque/produtos/{sem_controle['id']}/entrada",
        json={"quantidade": 1},
    )
    assert sem_controle_response.status_code == 400
    assert sem_controle_response.json()["code"] == "produto_sem_controle_estoque"


def test_ajuste_de_estoque_define_novo_valor_e_calcula_diferencas(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)

    menor_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/ajuste",
        json={"novoEstoque": 7, "observacao": "Contagem física"},
    )
    assert menor_response.status_code == 201
    menor = menor_response.json()
    assert menor["tipo"] == "AJUSTE"
    assert menor["origem"] == "AJUSTE_MANUAL"
    assert menor["quantidade"] == -3.0
    assert menor["estoqueAntes"] == 10.0
    assert menor["estoqueDepois"] == 7.0

    maior_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/ajuste",
        json={"novoEstoque": 15},
    )
    assert maior_response.status_code == 201
    maior = maior_response.json()
    assert maior["quantidade"] == 8.0
    assert maior["estoqueAntes"] == 7.0
    assert maior["estoqueDepois"] == 15.0

    zero_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/ajuste",
        json={"novoEstoque": 0},
    )
    assert zero_response.status_code == 201
    assert zero_response.json()["estoqueDepois"] == 0.0

    produto_response = client.get(f"/api/produtos/{produto['id']}")
    assert produto_response.status_code == 200
    assert produto_response.json()["quantidadeEstoque"] == 0.0


def test_ajuste_de_estoque_rejeita_dados_invalidos(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"])
    inativo = create_produto(client, categoria["id"], nome="Inativo")
    sem_controle = create_produto(
        client,
        categoria["id"],
        nome="Sem controle",
        controla_estoque=False,
    )
    client.patch(f"/api/produtos/{inativo['id']}/inativar")

    negativo_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/ajuste",
        json={"novoEstoque": -1},
    )
    assert negativo_response.status_code == 400
    assert negativo_response.json()["code"] == "novo_estoque_invalido"

    inexistente_response = client.post(
        "/api/estoque/produtos/999/ajuste",
        json={"novoEstoque": 1},
    )
    assert inexistente_response.status_code == 404
    assert inexistente_response.json()["code"] == "produto_nao_encontrado"

    inativo_response = client.post(
        f"/api/estoque/produtos/{inativo['id']}/ajuste",
        json={"novoEstoque": 1},
    )
    assert inativo_response.status_code == 400
    assert inativo_response.json()["code"] == "produto_inativo"

    sem_controle_response = client.post(
        f"/api/estoque/produtos/{sem_controle['id']}/ajuste",
        json={"novoEstoque": 1},
    )
    assert sem_controle_response.status_code == 400
    assert sem_controle_response.json()["code"] == "produto_sem_controle_estoque"


def test_historico_lista_vazio_erro_e_ordena_decrescente(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    produto = create_produto(client, categoria["id"], quantidade_estoque=10)
    sem_movimento = create_produto(client, categoria["id"], nome="Sem movimento")

    vazio_response = client.get(
        f"/api/estoque/produtos/{sem_movimento['id']}/movimentos"
    )
    assert vazio_response.status_code == 200
    assert vazio_response.json() == []

    entrada_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/entrada",
        json={"quantidade": 5},
    )
    ajuste_response = client.post(
        f"/api/estoque/produtos/{produto['id']}/ajuste",
        json={"novoEstoque": 12},
    )
    assert entrada_response.status_code == 201
    assert ajuste_response.status_code == 201

    historico_response = client.get(f"/api/estoque/produtos/{produto['id']}/movimentos")
    assert historico_response.status_code == 200
    movimentos = historico_response.json()
    assert [movimento["id"] for movimento in movimentos] == [
        ajuste_response.json()["id"],
        entrada_response.json()["id"],
    ]

    inexistente_response = client.get("/api/estoque/produtos/999/movimentos")
    assert inexistente_response.status_code == 404
    assert inexistente_response.json()["code"] == "produto_nao_encontrado"
