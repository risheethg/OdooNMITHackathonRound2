# app/users/user_service.py

import inspect
from bson import ObjectId
from datetime import timedelta
from app.core.logger import logs
from app.core.auth import create_access_token, get_password_hash, verify_password
from app.utils.response_model import response
from app.repo.user_repo import UserRepository, get_user_repo 
from app.models.user_model import CreateUserSchema, UserResponseSchema, UserRole, UserLogin, Token

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, data: CreateUserSchema):
        try:
            # 1. Check if user already exists in our DB
            existing_user = self.repo.get_by_email(data.email)
            if existing_user:
                return response.failure("A user with this email already exists.", status_code=400)

            # 2. Hash the password
            hashed_password = get_password_hash(data.password)

            # 3. Store user in our MongoDB database
            user_data = {
                "email": data.email,
                "role": data.role.value,
                "hashed_password": hashed_password
            }
            
            result = self.repo.create(user_data)
            new_id = result.inserted_id
            
            logs.define_logger(level=20, loggName=inspect.stack()[0], message=f"Successfully created user with ID: {new_id}")
            return response.success(data={"id": str(new_id)}, message="User created successfully", status_code=201)

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error creating user: {e}", body=data.model_dump_json(exclude={'password'}))
            return response.failure(message=f"Failed to create user: {e}", status_code=500)

    def authenticate_user(self, email: str, password: str):
        """
        Authenticate a user by email and password.
        Returns user data if successful, None if authentication fails.
        """
        try:
            user = self.repo.get_by_email(email)
            if not user:
                return None
            
            if not verify_password(password, user["hashed_password"]):
                return None
            
            return user
        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error authenticating user: {e}")
            return None

    def login_user(self, data: UserLogin):
        try:
            # Authenticate the user
            user = self.authenticate_user(data.email, data.password)
            if not user:
                return response.failure("Incorrect email or password", status_code=401)

            # Create access token
            access_token_expires = timedelta(minutes=60 * 24 * 8)  # 8 days
            access_token = create_access_token(
                subject=str(user["_id"]), expires_delta=access_token_expires
            )

            # Return token and user data
            user_response = UserResponseSchema.model_validate(user)
            return response.success(
                data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_response.model_dump(by_alias=True)
                },
                message="Login successful",
                status_code=200
            )

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error logging in user: {e}")
            return response.failure(message=f"Login failed: {e}", status_code=500)

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