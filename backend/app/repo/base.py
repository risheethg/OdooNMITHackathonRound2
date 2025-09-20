from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

class BaseRepository:
    """
    A base class for repository patterns that provides generic CRUD operations
    for a MongoDB collection.
    """
    def __init__(self, collection: Collection):
        """
        Initializes the repository with a specific MongoDB collection.

        Args:
            collection (Collection): The PyMongo collection object.
        """
        self.collection = collection

    def get_all(self, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        Retrieves all documents from the collection that match a query.

        Args:
            query (Dict[str, Any], optional): A MongoDB query filter. Defaults to {}.

        Returns:
            List[Dict[str, Any]]: A list of documents.
        """
        return list(self.collection.find(query))

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single document by its unique _id.

        Args:
            item_id (str): The string representation of the document's ObjectId.

        Returns:
            Optional[Dict[str, Any]]: The document if found, otherwise None.
        """
        return self.collection.find_one({"_id": ObjectId(item_id)})

    def create(self, data: Dict[str, Any]) -> InsertOneResult:
        """
        Creates a new document in the collection.

        Args:
            data (Dict[str, Any]): The data for the new document.

        Returns:
            InsertOneResult: The result from the insert operation, containing the new _id.
        """
        return self.collection.insert_one(data)

    def update(self, item_id: str, data: Dict[str, Any]) -> UpdateResult:
        """
        Updates an existing document by its _id.

        Args:
            item_id (str): The string representation of the document's ObjectId.
            data (Dict[str, Any]): The data to update, using operators like $set.

        Returns:
            UpdateResult: The result from the update operation.
        """
        return self.collection.update_one({"_id": ObjectId(item_id)}, {"$set": data})

    def delete(self, item_id: str) -> DeleteResult:
        """
        Deletes a document by its _id.

        Args:
            item_id (str): The string representation of the document's ObjectId.

        Returns:
            DeleteResult: The result from the delete operation.
        """
        return self.collection.delete_one({"_id": ObjectId(item_id)})
