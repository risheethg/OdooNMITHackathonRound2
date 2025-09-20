from fastapi import HTTPException, status
from ..repo.bom_repo import BOMRepository
from ..repo.product_repo import ProductRepository
from ..models.bom_model import BOM
from pymongo.results import InsertOneResult

class BOMService:
    def __init__(self, bom_repo: BOMRepository, product_repo: ProductRepository):
        self.bom_repo = bom_repo
        self.product_repo = product_repo

    def create_bom(self, bom: BOM) -> InsertOneResult:
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
        bom_data = bom.dict(by_alias=True)
        return self.bom_repo.create(bom_data)