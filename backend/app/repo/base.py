from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from datetime import datetime

class BaseRepository:
    """
    A base class for repository patterns that provides generic CRUD operations
    for a MongoDB collection with clean ObjectId handling.
    """
    def __init__(self, collection: Collection):
        """
        Initializes the repository with a specific MongoDB collection.

        Args:
            collection (Collection): The PyMongo collection object.
        """
        self.collection = collection

    def _convert_id_to_string(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId to string in document"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def _convert_ids_to_strings(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert ObjectIds to strings in list of documents"""
        return [self._convert_id_to_string(doc) for doc in docs]

    def _prepare_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for creation - add timestamps and remove None _id"""
        # Remove _id if it's None to let MongoDB generate it
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        
        # Add timestamps if not present
        now = datetime.utcnow()
        if "created_at" not in data:
            data["created_at"] = now
        if "updated_at" not in data:
            data["updated_at"] = now
            
        return data

    def get_all(self, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        Retrieves all documents from the collection that match a query.

        Args:
            query (Dict[str, Any], optional): A MongoDB query filter. Defaults to {}.

        Returns:
            List[Dict[str, Any]]: A list of documents with string IDs.
        """
        docs = list(self.collection.find(query))
        return self._convert_ids_to_strings(docs)

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single document by its unique _id.

        Args:
            item_id (str): The string representation of the document's ObjectId.

        Returns:
            Optional[Dict[str, Any]]: The document if found with string ID, otherwise None.
        """
        doc = self.collection.find_one({"_id": ObjectId(item_id)})
        return self._convert_id_to_string(doc) if doc else None

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.

        Args:
            query (Dict[str, Any]): MongoDB query filter.

        Returns:
            Optional[Dict[str, Any]]: The document if found with string ID, otherwise None.
        """
        doc = self.collection.find_one(query)
        return self._convert_id_to_string(doc) if doc else None

    def create(self, data: Dict[str, Any]) -> InsertOneResult:
        """
        Creates a new document in the collection.

        Args:
            data (Dict[str, Any]): The data for the new document.

        Returns:
            InsertOneResult: The result from the insert operation, containing the new _id.
        """
        prepared_data = self._prepare_create_data(data)
        return self.collection.insert_one(prepared_data)

    def update(self, item_id: str, data: Dict[str, Any]) -> UpdateResult:
        """
        Updates an existing document by its _id.

        Args:
            item_id (str): The string representation of the document's ObjectId.
            data (Dict[str, Any]): The data to update, using operators like $set.

        Returns:
            UpdateResult: The result from the update operation.
        """
        # Add updated timestamp
        data["updated_at"] = datetime.utcnow()
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

    def count_documents(self, query: Dict[str, Any] = {}) -> int:
        """
        Counts the number of documents matching the query.

        Args:
            query (Dict[str, Any], optional): A MongoDB query filter. Defaults to {}.

        Returns:
            int: The number of documents.
        """
        return self.collection.count_documents(query)