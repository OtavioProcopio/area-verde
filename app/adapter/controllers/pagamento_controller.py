from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from adapter.controllers.dependencies import (
    build_pagamento_service,
    get_current_session,
)
from adapter.dtos.pagamento_dto import (
    FecharComandaRequest,
    FecharComandaResponse,
    PagamentoResponse,
)
from core.application.use_cases.pagamento_service import PagamentoService

router = APIRouter(prefix="/api/comandas", tags=["Pagamentos"])


@router.post(
    "/{comanda_id}/fechar",
    response_model=FecharComandaResponse,
    status_code=status.HTTP_200_OK,
    summary="Fecha uma comanda e registra o pagamento",
)
def fechar_comanda(
    comanda_id: int,
    request: FecharComandaRequest,
    session: Session = Depends(get_current_session),
):
    service: PagamentoService = build_pagamento_service(session)
    return service.fechar_comanda(comanda_id, request)


@router.get(
    "/{comanda_id}/pagamentos",
    response_model=List[PagamentoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista os pagamentos de uma comanda",
)
def listar_pagamentos_da_comanda(
    comanda_id: int,
    session: Session = Depends(get_current_session),
):
    service: PagamentoService = build_pagamento_service(session)
    return service.listar_pagamentos(comanda_id)
