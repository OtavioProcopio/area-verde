import uvicorn
from fastapi import FastAPI, Request
from sqlmodel import Session

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
            finally:
                db_session_context.reset(token)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "UP"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
