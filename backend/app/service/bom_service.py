from fastapi import HTTPException, status
from ..repo.bom_repo import BOMRepository
from ..repo.product_repo import ProductRepository
from ..models.bom_model import BOM, BOMCreate
from pymongo.results import InsertOneResult

class BOMService:
    def __init__(self, bom_repo: BOMRepository, product_repo: ProductRepository):
        self.bom_repo = bom_repo
        self.product_repo = product_repo

    def create_bom(self, bom: BOMCreate) -> InsertOneResult:
        # Validate that the finished product exists
        finished_product_doc = self.product_repo.get_by_id(str(bom.finishedProductId))
        if not finished_product_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Finished product with ID '{bom.finishedProductId}' not found."
            )

        # Validate that all components exist
        for comp in bom.components:
            if not self.product_repo.get_by_id(str(comp.productId)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Component product with ID '{comp.productId}' not found."
                )

        # Create the BOM document
        bom_data = bom.model_dump()
        return self.bom_repo.create(bom_data)

    def get_all_boms(self):
        """Get all BOMs from the database."""
        return self.bom_repo.get_all()

    def get_bom_by_id(self, bom_id: str):
        """Get a specific BOM by ID."""
        bom = self.bom_repo.get_by_id(bom_id)
        if not bom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"BOM with ID '{bom_id}' not found."
            )
        return bom

    def get_bom_by_product_id(self, product_id: str):
        """Get BOM for a specific finished product."""
        bom = self.bom_repo.find_one({"finishedProductId": product_id})
        if not bom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"BOM for product ID '{product_id}' not found."
            )
        return bom