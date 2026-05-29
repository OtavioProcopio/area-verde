from decimal import Decimal

from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlmodel import Session

from adapter.repositories.produto_composicao_repository import (
    ProdutoComposicaoRepository,
)
from adapter.repositories.produto_repository import ProdutoRepository
from api import create_app
from core.application.use_cases.produto_composicao_service import (
    ProdutoComposicaoService,
)
from core.domain.enums import TipoProduto
from core.domain.exceptions import ApplicationError
from core.domain.models import Produto


def build_client(test_engine):
    app = create_app()
    app.container.engine.override(providers.Object(test_engine))
    return TestClient(app)


def create_categoria(client: TestClient, nome: str = "Cervejas") -> dict:
    response = client.post("/api/categorias", json={"nome": nome})
    assert response.status_code == 201
    return response.json()


def create_produto_payload(categoria_id: int) -> dict:
    return {
        "nome": "Cerveja lata",
        "categoriaId": categoria_id,
        "precoVenda": 7.00,
        "controlaEstoque": True,
        "unidadeEstoque": "UNIDADE",
        "quantidadeEstoque": 24,
        "quantidadeBaixaPorVenda": 1,
        "estoqueMinimo": 6,
    }


def test_categoria_lifecycle(test_engine):
    client = build_client(test_engine)

    categoria = create_categoria(client)
    categoria_id = categoria["id"]

    assert categoria["nome"] == "Cervejas"
    assert categoria["ativo"] is True
    assert "criadoEm" in categoria
    assert "atualizadoEm" in categoria

    list_response = client.get("/api/categorias")
    assert list_response.status_code == 200
    assert [item["nome"] for item in list_response.json()] == ["Cervejas"]

    get_response = client.get(f"/api/categorias/{categoria_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == categoria_id

    update_response = client.put(
        f"/api/categorias/{categoria_id}",
        json={"nome": "Cervejas especiais"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["nome"] == "Cervejas especiais"

    inactive_response = client.patch(f"/api/categorias/{categoria_id}/inativar")
    assert inactive_response.status_code == 200
    assert inactive_response.json()["ativo"] is False

    active_list_response = client.get("/api/categorias?ativo=true")
    assert active_list_response.status_code == 200
    assert active_list_response.json() == []

    active_response = client.patch(f"/api/categorias/{categoria_id}/ativar")
    assert active_response.status_code == 200
    assert active_response.json()["ativo"] is True


def test_categoria_validation_not_found_and_active_duplicate(test_engine):
    client = build_client(test_engine)

    invalid_response = client.post("/api/categorias", json={"nome": "   "})
    assert invalid_response.status_code == 422
    assert invalid_response.json()["code"] == "dados_invalidos"

    not_found_response = client.get("/api/categorias/999")
    assert not_found_response.status_code == 404
    assert not_found_response.json()["code"] == "categoria_nao_encontrada"

    categoria = create_categoria(client, "Doses")

    duplicate_response = client.post("/api/categorias", json={"nome": "doses"})
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["code"] == "nome_duplicado"

    client.patch(f"/api/categorias/{categoria['id']}/inativar")
    recreated_response = client.post("/api/categorias", json={"nome": "doses"})
    assert recreated_response.status_code == 201


def test_produto_lifecycle_and_filters(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    payload = create_produto_payload(categoria["id"])

    produto_response = client.post("/api/produtos", json=payload)
    assert produto_response.status_code == 201

    produto = produto_response.json()
    produto_id = produto["id"]
    assert produto["nome"] == "Cerveja lata"
    assert produto["categoria"]["id"] == categoria["id"]
    assert produto["precoVenda"] == 7.0
    assert produto["tipoProduto"] == "SIMPLES"
    assert produto["controlaEstoque"] is True
    assert produto["unidadeEstoque"] == "UNIDADE"
    assert produto["quantidadeEstoque"] == 24.0
    assert produto["quantidadeBaixaPorVenda"] == 1.0
    assert produto["estoqueMinimo"] == 6.0
    assert produto["ativo"] is True

    list_response = client.get(
        f"/api/produtos?ativo=true&categoriaId={categoria['id']}&nome=cerveja"
    )
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [produto_id]

    get_response = client.get(f"/api/produtos/{produto_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == produto_id

    payload["nome"] = "Cerveja long neck"
    payload["precoVenda"] = 9.5
    update_response = client.put(f"/api/produtos/{produto_id}", json=payload)
    assert update_response.status_code == 200
    assert update_response.json()["nome"] == "Cerveja long neck"
    assert update_response.json()["precoVenda"] == 9.5

    inactive_response = client.patch(f"/api/produtos/{produto_id}/inativar")
    assert inactive_response.status_code == 200
    assert inactive_response.json()["ativo"] is False

    active_list_response = client.get("/api/produtos?ativo=true")
    assert active_list_response.status_code == 200
    assert active_list_response.json() == []

    active_response = client.patch(f"/api/produtos/{produto_id}/ativar")
    assert active_response.status_code == 200
    assert active_response.json()["ativo"] is True


def test_produto_ml_and_without_stock_control(test_engine):
    client = build_client(test_engine)
    doses = create_categoria(client, "Doses")
    avulsos = create_categoria(client, "Avulsos")

    ml_response = client.post(
        "/api/produtos",
        json={
            "nome": "Dose de pinga",
            "categoriaId": doses["id"],
            "precoVenda": 5.00,
            "controlaEstoque": True,
            "unidadeEstoque": "ML",
            "quantidadeEstoque": 1000,
            "quantidadeBaixaPorVenda": 50,
            "estoqueMinimo": 200,
        },
    )
    assert ml_response.status_code == 201
    assert ml_response.json()["unidadeEstoque"] == "ML"
    assert ml_response.json()["quantidadeBaixaPorVenda"] == 50.0

    no_stock_response = client.post(
        "/api/produtos",
        json={
            "nome": "Taxa de serviço",
            "categoriaId": avulsos["id"],
            "precoVenda": 2.00,
            "controlaEstoque": False,
        },
    )
    assert no_stock_response.status_code == 201
    no_stock = no_stock_response.json()
    assert no_stock["controlaEstoque"] is False
    assert no_stock["unidadeEstoque"] == "UNIDADE"
    assert no_stock["quantidadeEstoque"] == 0.0
    assert no_stock["quantidadeBaixaPorVenda"] == 0.0
    assert no_stock["estoqueMinimo"] == 0.0


def test_produto_composto_pode_ser_criado(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Drinks")

    response = client.post(
        "/api/produtos",
        json={
            "nome": "Dose Mista A+B",
            "categoriaId": categoria["id"],
            "precoVenda": 12.00,
            "tipoProduto": "COMPOSTO",
            "controlaEstoque": False,
        },
    )

    assert response.status_code == 201
    produto = response.json()
    assert produto["nome"] == "Dose Mista A+B"
    assert produto["tipoProduto"] == "COMPOSTO"
    assert produto["controlaEstoque"] is False


def test_produto_criado_sem_tipo_deve_ser_simples(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)

    response = client.post(
        "/api/produtos",
        json=create_produto_payload(categoria["id"]),
    )

    assert response.status_code == 201
    assert response.json()["tipoProduto"] == "SIMPLES"


def test_produto_validations(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)
    payload = create_produto_payload(categoria["id"])

    sem_nome = payload | {"nome": "   "}
    sem_nome_response = client.post("/api/produtos", json=sem_nome)
    assert sem_nome_response.status_code == 422
    assert sem_nome_response.json()["code"] == "dados_invalidos"

    sem_categoria = payload.copy()
    sem_categoria.pop("categoriaId")
    sem_categoria_response = client.post("/api/produtos", json=sem_categoria)
    assert sem_categoria_response.status_code == 422
    assert sem_categoria_response.json()["code"] == "dados_invalidos"

    preco_negativo = payload | {"precoVenda": -1}
    preco_response = client.post("/api/produtos", json=preco_negativo)
    assert preco_response.status_code == 400
    assert preco_response.json()["code"] == "preco_invalido"

    sem_unidade = payload.copy()
    sem_unidade.pop("unidadeEstoque")
    unidade_response = client.post("/api/produtos", json=sem_unidade)
    assert unidade_response.status_code == 400
    assert unidade_response.json()["code"] == "unidade_estoque_invalida"

    baixa_invalida = payload | {"quantidadeBaixaPorVenda": 0}
    baixa_response = client.post("/api/produtos", json=baixa_invalida)
    assert baixa_response.status_code == 400
    assert baixa_response.json()["code"] == "quantidade_baixa_invalida"


def test_produto_not_found_and_invalid_categoria(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client)

    not_found_response = client.get("/api/produtos/999")
    assert not_found_response.status_code == 404
    assert not_found_response.json()["code"] == "produto_nao_encontrado"

    missing_category_payload = create_produto_payload(999)
    missing_category_response = client.post(
        "/api/produtos", json=missing_category_payload
    )
    assert missing_category_response.status_code == 404
    assert missing_category_response.json()["code"] == "categoria_nao_encontrada"

    client.patch(f"/api/categorias/{categoria['id']}/inativar")
    inactive_category_payload = create_produto_payload(categoria["id"])
    inactive_category_response = client.post(
        "/api/produtos", json=inactive_category_payload
    )
    assert inactive_category_response.status_code == 400
    assert inactive_category_response.json()["code"] == "categoria_inativa"


def build_composicao_service(session: Session) -> ProdutoComposicaoService:
    return ProdutoComposicaoService(
        produto_repository=ProdutoRepository(session),
        composicao_repository=ProdutoComposicaoRepository(session),
    )


def create_produto_model(
    session: Session,
    categoria_id: int,
    nome: str,
    tipo_produto: TipoProduto = TipoProduto.SIMPLES,
    controla_estoque: bool = True,
    ativo: bool = True,
) -> Produto:
    produto = Produto(
        nome=nome,
        categoria_id=categoria_id,
        preco_venda=Decimal("10.00"),
        tipo_produto=tipo_produto,
        controla_estoque=controla_estoque,
        ativo=ativo,
    )
    session.add(produto)
    session.commit()
    session.refresh(produto)
    return produto


def test_composicao_produto_composto_pode_ter_componente(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")

    with Session(test_engine) as session:
        produto_pai = create_produto_model(
            session,
            categoria["id"],
            "Dose Mista A+B",
            tipo_produto=TipoProduto.COMPOSTO,
            controla_estoque=False,
        )
        componente = create_produto_model(session, categoria["id"], "Bebida A")
        service = build_composicao_service(session)

        composicao = service.add_componente(
            produto_pai_id=produto_pai.id,
            produto_componente_id=componente.id,
            quantidade_baixa=Decimal("50.000"),
        )

        assert composicao.id is not None
        assert composicao.produto_pai_id == produto_pai.id
        assert composicao.produto_componente_id == componente.id
        assert composicao.quantidade_baixa == Decimal("50.000")
        assert service.list_by_parent(produto_pai.id) == [composicao]


def test_composicao_exige_produtos_existentes(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")

    with Session(test_engine) as session:
        produto_pai = create_produto_model(
            session,
            categoria["id"],
            "Dose Mista A+B",
            tipo_produto=TipoProduto.COMPOSTO,
            controla_estoque=False,
        )
        componente = create_produto_model(session, categoria["id"], "Bebida A")
        service = build_composicao_service(session)

        produto_pai_inexistente = service.add_componente
        try:
            produto_pai_inexistente(999, componente.id, Decimal("50.000"))
        except ApplicationError as error:
            assert error.code == "produto_pai_nao_encontrado"
            assert error.status_code == 404
        else:
            raise AssertionError("Deveria rejeitar produto pai inexistente")

        try:
            service.add_componente(produto_pai.id, 999, Decimal("50.000"))
        except ApplicationError as error:
            assert error.code == "produto_componente_nao_encontrado"
            assert error.status_code == 404
        else:
            raise AssertionError("Deveria rejeitar componente inexistente")


def test_composicao_rejeita_componente_invalido_duplicado_e_quantidade(test_engine):
    client = build_client(test_engine)
    categoria = create_categoria(client, "Doses")

    with Session(test_engine) as session:
        produto_pai = create_produto_model(
            session,
            categoria["id"],
            "Dose Mista A+B",
            tipo_produto=TipoProduto.COMPOSTO,
            controla_estoque=False,
        )
        componente = create_produto_model(session, categoria["id"], "Bebida A")
        inativo = create_produto_model(session, categoria["id"], "Inativo", ativo=False)
        sem_estoque = create_produto_model(
            session,
            categoria["id"],
            "Taxa",
            controla_estoque=False,
        )
        composto_componente = create_produto_model(
            session,
            categoria["id"],
            "Outro composto",
            tipo_produto=TipoProduto.COMPOSTO,
            controla_estoque=False,
        )
        service = build_composicao_service(session)

        casos = [
            (produto_pai.id, produto_pai.id, "componente_igual_produto_pai"),
            (produto_pai.id, inativo.id, "produto_componente_inativo"),
            (
                produto_pai.id,
                sem_estoque.id,
                "produto_componente_sem_controle_estoque",
            ),
            (
                produto_pai.id,
                composto_componente.id,
                "componente_composto_nao_permitido",
            ),
        ]

        for produto_pai_id, componente_id, code in casos:
            try:
                service.add_componente(
                    produto_pai_id,
                    componente_id,
                    Decimal("50.000"),
                )
            except ApplicationError as error:
                assert error.code == code
            else:
                raise AssertionError(f"Deveria rejeitar {code}")

        for quantidade in (Decimal("0"), Decimal("-1")):
            try:
                service.add_componente(produto_pai.id, componente.id, quantidade)
            except ApplicationError as error:
                assert error.code == "quantidade_baixa_invalida"
            else:
                raise AssertionError("Deveria rejeitar quantidade invalida")

        service.add_componente(produto_pai.id, componente.id, Decimal("50.000"))

        try:
            service.add_componente(produto_pai.id, componente.id, Decimal("25.000"))
        except ApplicationError as error:
            assert error.code == "produto_componente_duplicado"
            assert error.status_code == 409
        else:
            raise AssertionError("Deveria rejeitar componente duplicado")
