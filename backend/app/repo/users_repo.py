from typing import Optional
from app.models.user_models import UserCreate, User, UserRole
from app.core.firebase_connection import get_firestore_client
from pymongo.database import Database
from fastapi import Depends
from app.core.db_connection import get_db

class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    async def get(self, uid: str) -> Optional[User]:
        """
        Get a user profile from Firestore using their Firebase Auth UID.
        The UID is the document ID.
        """
        db = get_firestore_client()
        user_doc_ref = db.collection("users").document(uid)
        user_doc = await user_doc_ref.get()

        if user_doc.exists:
            # Pass the UID into the model since it's the document's ID
            user_data = user_doc.to_dict()
            user_data["uid"] = uid
            return User(**user_data)
        return None
    
    async def create(self, *, obj_in: UserCreate) -> User:
        """
        Create a new user document in Firestore.
        The document ID will be the user's Firebase Auth UID.
        """
        db = get_firestore_client()
        
        # Create a full User object to get default values for fields like 'roles'
        new_user = User(**obj_in.model_dump())
        
        # Now convert the full User object to a dict for Firestore
        user_data = new_user.model_dump()
        
        # We explicitly use the UID as the document ID
        uid = user_data.pop("uid")
        
        # set() creates or overwrites a document
        await db.collection("users").document(uid).set(user_data)
        
        # Re-fetch the created user to return a consistent object
        created_user = await self.get(uid)
        return created_user

    async def update(self, uid: str, data_to_update: dict) -> Optional[User]:
        """
        Update a user's document in Firestore.
        """
        db = get_firestore_client()
        user_doc_ref = db.collection("users").document(uid)
        
        # Ensure roles are stored as strings if they are enums
        if 'roles' in data_to_update:
            data_to_update['roles'] = [role.value for role in data_to_update['roles']]
            
        # update() merges data into an existing document
        await user_doc_ref.update(data_to_update)
        
        updated_user = await self.get(uid)
        return updated_user

def get_user_repo(db: Database = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

users_repo = UserRepository(get_db())