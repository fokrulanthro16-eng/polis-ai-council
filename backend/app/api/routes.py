from fastapi import APIRouter

from app.models.schemas import DeliberateRequest, DeliberateResponse
from app.services.council import run_council
from app.utils.session_logger import write_session_log

router = APIRouter(prefix="/api/council", tags=["council"])


@router.post("/deliberate", response_model=DeliberateResponse)
def deliberate(request: DeliberateRequest) -> DeliberateResponse:
    """Run the full agent council on a problem statement and return the
    per-agent breakdown, debate timeline, and consensus summary."""
    response = run_council(request.problem)
    write_session_log(request.problem, response)
    return response
