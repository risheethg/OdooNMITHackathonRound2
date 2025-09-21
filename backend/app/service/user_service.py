# app/users/user_service.py

import inspect
from bson import ObjectId
from app.core.logger import logs
from app.utils.response_model import response
from app.repo.user_repo import UserRepository, get_user_repo 
from app.models.user_model import CreateUserSchema, UserResponseSchema, UserRole
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, data: CreateUserSchema):
        try:
            # 1. Check if user already exists in our DB
            existing_user = self.repo.get_by_email(data.email)
            if existing_user:
                return response.failure("A user with this email already exists in the local database.", status_code=400)

            # 2. Create user in Firebase Authentication
            try:
                firebase_user = auth.create_user(
                    email=data.email,
                    password=data.password
                )
                uid = firebase_user.uid
            except FirebaseError as e:
                logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error creating user in Firebase: {e}", body=data.model_dump_json(exclude={'password'}))
                if e.code == 'EMAIL_EXISTS':
                    return response.failure(message="A user with this email already exists in Firebase.", status_code=409)
                return response.failure(message=f"Failed to create user in Firebase: {e.default_message}", status_code=500)

            # 3. Store user in our MongoDB database
            user_data = data.model_dump()
            del user_data["password"]  # Do not store the plain-text password
            user_data["uid"] = uid
            
            result = self.repo.create(user_data)
            new_id = result.inserted_id
            
            logs.define_logger(level=20, loggName=inspect.stack()[0], message=f"Successfully created user with ID: {new_id} and Firebase UID: {uid}")
            return response.success(data={"id": str(new_id), "uid": uid}, message="User created successfully", status_code=201)

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error creating user: {e}", body=data.model_dump_json(exclude={'password'}))
            return response.failure(message=f"Failed to create user: {e}", status_code=500)

    def get_user_by_id(self, item_id: str):
        if not ObjectId.is_valid(item_id):
            return response.failure(message="Invalid user ID format", status_code=400)

        try:
            user_doc = self.repo.get_by_id(item_id)
            if user_doc:
                # Use the response schema to ensure the password hash is NOT returned
                validated_data = UserResponseSchema.model_validate(user_doc)
                return response.success(data=validated_data.model_dump(by_alias=True))
            else:
                return response.failure(message="User not found", status_code=404)
        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error retrieving user {item_id}: {e}")
            return response.failure(message=f"An error occurred: {e}", status_code=500)

def get_user_service() -> UserService:
    repo = get_user_repo()
    return UserService(repo)