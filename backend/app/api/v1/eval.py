from fastapi import APIRouter, HTTPException
from app.schemas.hardware import DVCase, Trajectory
from app.services.evaluator import compute_r_total

router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.post("/process-trajectory", response_model=Trajectory)
async def process_eval(case: DVCase, proposed_fix: str):

    try:

        return {"status": "success", "message": "Logic isolated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        