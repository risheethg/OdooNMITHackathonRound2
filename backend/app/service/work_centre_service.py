# app/work_centres/work_centre_service.py

import inspect
from datetime import datetime, timezone
from bson import ObjectId
from app.core.logger import logs
from app.utils.response_model import response
from app.repo.work_centre_repo import WorkCentreRepository, get_work_centre_repo
from app.models.work_centre_model import CreateWorkCentreSchema, WorkCentreResponseSchema

class WorkCentreService:
    """
    Service layer containing the business logic for work centre operations.
    """
    def __init__(self, repo: WorkCentreRepository):
        self.repo = repo

    def create_work_centre(self, data: CreateWorkCentreSchema):
        try:
            work_centre_data = data.model_dump()
            
            now = datetime.now(timezone.utc)
            work_centre_data["createdAt"] = now
            work_centre_data["updatedAt"] = now

            result = self.repo.create(work_centre_data)
            new_id = result.inserted_id
            
            logs.define_logger(level=20, loggName=inspect.stack()[0], message=f"Successfully created work centre with ID: {new_id}")
            return response.success(data={"id": str(new_id)}, message="Work centre created successfully", status_code=201)

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error creating work centre: {e}", body=data.model_dump_json())
            return response.failure(message=f"Failed to create work centre: {e}", status_code=500)

    def get_all_work_centres(self):
        try:
            work_centres_docs = self.repo.get_all()
            # Serialize each document to ensure correct format (e.g., ObjectId to str)
            results = [
                WorkCentreResponseSchema.model_validate(wc).model_dump(by_alias=True) 
                for wc in work_centres_docs
            ]
            return response.success(data=results)
        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error retrieving all work centres: {e}")
            return response.failure(message=f"An error occurred: {e}", status_code=500)

    def get_work_centre_by_id(self, item_id: str):
        if not ObjectId.is_valid(item_id):
            return response.failure(message="Invalid work centre ID format", status_code=400)

        try:
            work_centre_doc = self.repo.get_by_id(item_id)
            if work_centre_doc:
                validated_data = WorkCentreResponseSchema.model_validate(work_centre_doc)
                return response.success(data=validated_data.model_dump(by_alias=True))
            else:
                return response.failure(message="Work centre not found", status_code=404)
        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error retrieving work centre {item_id}: {e}")
            return response.failure(message=f"An error occurred: {e}", status_code=500)

def get_work_centre_service() -> WorkCentreService:
    """
    Returns an instance of the WorkCentreService for dependency injection.
    """
    repo = get_work_centre_repo()
    return WorkCentreService(repo)