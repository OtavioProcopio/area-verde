from fastapi import APIRouter, Depends
from sqlmodel import Session

from adapter.controllers.dependencies import (
    build_configuracao_service,
    get_current_session,
)
from adapter.dtos.configuracao_dto import (
    ConfiguracaoPatchRequest,
    ConfiguracaoRequest,
    ConfiguracaoResponse,
)
from core.application.use_cases.configuracao_service import ConfiguracaoService

router = APIRouter(prefix="/api/configuracoes", tags=["Configurações"])


def get_service(
    session: Session = Depends(get_current_session),
) -> ConfiguracaoService:
    return build_configuracao_service(session)


@router.get("", response_model=ConfiguracaoResponse)
def get_configuracao(
    service: ConfiguracaoService = Depends(get_service),
) -> ConfiguracaoResponse:
    configuracao = service.get_or_create()
    return ConfiguracaoResponse.from_model(configuracao)


@router.put("", response_model=ConfiguracaoResponse)
def update_configuracao(
    request: ConfiguracaoRequest,
    service: ConfiguracaoService = Depends(get_service),
) -> ConfiguracaoResponse:
    configuracao = service.update(
        nome_bar=request.nome_bar,
        dias_para_alerta_fiado=request.dias_para_alerta_fiado,
        permitir_estoque_negativo=request.permitir_estoque_negativo,
        observacao=request.observacao,
    )
    return ConfiguracaoResponse.from_model(configuracao)


@router.patch("", response_model=ConfiguracaoResponse)
def patch_configuracao(
    request: ConfiguracaoPatchRequest,
    service: ConfiguracaoService = Depends(get_service),
) -> ConfiguracaoResponse:
    configuracao = service.patch(
        nome_bar=request.nome_bar,
        dias_para_alerta_fiado=request.dias_para_alerta_fiado,
        permitir_estoque_negativo=request.permitir_estoque_negativo,
        observacao=request.observacao,
    )
    return ConfiguracaoResponse.from_model(configuracao)
