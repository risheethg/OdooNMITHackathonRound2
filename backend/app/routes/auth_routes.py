from fastapi import APIRouter, Depends, status, HTTPException

# Import the correct dependencies from your updated security.py
from app.core.security import get_current_user_token, get_current_active_user, RoleChecker

# Import the models and the repository
from app.models.user_models import User, UserCreate, UserRole
from app.repo.users_repo import users_repo

router = APIRouter(tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
async def register_user(
    # This route needs a valid token, but the user might not be in our DB yet.
    # So we use the token-only dependency.
    decoded_token: dict = Depends(get_current_user_token)
):
    """
    Handles first-time user registration.
    It takes a valid Firebase ID token, extracts user info,
    and creates a new user profile document in Firestore.
    """
    user_uid = decoded_token.get("uid")
    
    # Check if the user already exists in Firestore
    if await users_repo.get(user_uid):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user has already been registered."
        )

    # Create a user object from the token data and create it in the DB
    user_to_create = UserCreate(**decoded_token)
    created_user = await users_repo.create(obj_in=user_to_create)
    return created_user


@router.post("/token", response_model=User)
async def login_user(
    # This dependency handles everything: token validation AND fetching the user from Firestore.
    current_user: User = Depends(get_current_active_user)
):
    """
    Handles user "login" for our backend. If the token is valid and the
    user exists in our Firestore DB, this returns their profile.
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user():
    """
    Client-side responsibility. This endpoint is a placeholder.
    """
    return {"message": "Logout successful. Please discard your token on the client-side."}


@router.get("/me", response_model=User)
async def read_current_user(
    # Just like /login, this requires a fully authenticated and registered user.
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches the profile for the currently authenticated user from Firestore.
    The dependency `get_current_active_user` does all the work.
    """
    return current_user


@router.get(
    "/admin/dashboard",
    response_model=dict,
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]
)
async def read_admin_dashboard(current_user: User = Depends(get_current_active_user)):
    """
    An example admin-only endpoint.
    The RoleChecker dependency ensures that only users with the 'admin' role can access this.
    """
    return {"message": f"Welcome to the admin dashboard, {current_user.name}!"}