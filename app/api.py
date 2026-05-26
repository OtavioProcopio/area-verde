import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from adapter.controllers.categoria_produto_controller import (
    router as categoria_produto_router,
)
from adapter.controllers.estoque_controller import router as estoque_router
from adapter.controllers.produto_controller import router as produto_router
from core.domain.exceptions import ApplicationError
from infra.config.container import Container
from infra.config.context import db_session_context
from infra.config.database import run_migrations
from infra.config.settings import settings


def create_app() -> FastAPI:
    if settings.RUN_MIGRATIONS:
        run_migrations()

    container = Container()

    app = FastAPI(
        title="Area Verde API",
        description="API para apoiar a operacao do bar Area Verde",
        version="0.1.0",
    )

    app.container = container  # type: ignore[attr-defined]

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        engine = container.engine()
        with Session(engine) as session:
            token = db_session_context.set(session)
            try:
                response = await call_next(request)
                return response
            except Exception:
                session.rollback()
                raise
            finally:
                db_session_context.reset(token)

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": "dados_invalidos",
                "message": "Dados inválidos",
                "details": [
                    {
                        "field": ".".join(
                            str(location)
                            for location in error["loc"]
                            if location != "body"
                        ),
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ],
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "dados_invalidos",
                "message": "Dados inválidos",
            },
        )

    app.include_router(categoria_produto_router)
    app.include_router(produto_router)
    app.include_router(estoque_router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "UP"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
