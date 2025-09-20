# app/work_centres/work_centre_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.service.work_centre_service import WorkCentreService, get_work_centre_service
from app.models.work_centre_model import CreateWorkCentreSchema
from app.utils.response_model import response
from app.core.security import RoleChecker
from app.models.user_model import UserRole

router = APIRouter(
    prefix="/work-centres",
    tags=["Work Centres"],
    dependencies=[Depends(RoleChecker([UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN]))]
)

@router.post("/")
def create_work_centre(
    data: CreateWorkCentreSchema,
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Create a new Work Centre.
    """
    try:
        work_centre = service.create_work_centre(data)
        return response.success(data=work_centre, message="Work centre created successfully.", status_code=201)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_all_work_centres(
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Retrieve a list of all Work Centres.
    """
    try:
        work_centres = service.get_all_work_centres()
        return response.success(data=work_centres)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}")
def get_work_centre(
    item_id: str,
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Retrieve a single Work Centre by its unique ID.
    """
    try:
        work_centre = service.get_work_centre_by_id(item_id)
        if work_centre:
            return response.success(data=work_centre)
        return response.failure(message="Work centre not found", status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))