# app/work_centres/work_centre_router.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.service.work_centre_service import WorkCentreService, get_work_centre_service
from app.models.work_centre_model import CreateWorkCentreSchema

router = APIRouter(
    prefix="/work-centres",
    tags=["Work Centres"]
)

@router.post("/")
def create_work_centre(
    data: CreateWorkCentreSchema,
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Create a new Work Centre.
    """
    result = service.create_work_centre(data)
    return JSONResponse(status_code=result["status_code"], content=result)

@router.get("/")
def get_all_work_centres(
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Retrieve a list of all Work Centres.
    """
    result = service.get_all_work_centres()
    return JSONResponse(status_code=result["status_code"], content=result)


@router.get("/{item_id}")
def get_work_centre(
    item_id: str,
    service: WorkCentreService = Depends(get_work_centre_service)
):
    """
    Retrieve a single Work Centre by its unique ID.
    """
    result = service.get_work_centre_by_id(item_id)
    return JSONResponse(status_code=result["status_code"], content=result)