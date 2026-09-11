from fastapi import APIRouter, Depends
from sqlmodel import Session

from adapter.controllers.dependencies import build_acesso_service, get_current_session
from adapter.dtos.acesso_dto import (
    AlterarSenhaRequest,
    AlterarSenhaResponse,
    ValidarAcessoRequest,
    ValidarAcessoResponse,
)
from core.application.use_cases.acesso_service import AcessoService

router = APIRouter(prefix="/api/acesso", tags=["Acesso / Senha"])


def get_service(session: Session = Depends(get_current_session)) -> AcessoService:
    return build_acesso_service(session)


@router.post("/validar", response_model=ValidarAcessoResponse)
def validar_acesso(
    request: ValidarAcessoRequest,
    service: AcessoService = Depends(get_service),
) -> ValidarAcessoResponse:
    service.validar_senha(request.senha)
    return ValidarAcessoResponse(valido=True)


@router.put("/senha", response_model=AlterarSenhaResponse)
def alterar_senha(
    request: AlterarSenhaRequest,
    service: AcessoService = Depends(get_service),
) -> AlterarSenhaResponse:
    configuracao = service.definir_ou_alterar_senha(
        nova_senha=request.nova_senha,
        senha_atual=request.senha_atual,
    )
    return AlterarSenhaResponse(senhaConfigurada=bool(configuracao.senha_acesso_hash))
