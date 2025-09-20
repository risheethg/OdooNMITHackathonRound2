import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import MongoClient

# Importing the connection manager from the core directory
from core.db_connection import DBConnection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager to handle application startup and shutdown events.
    This is the recommended way to manage resources like database connections.
    """
    print("Application startup...")
    # Initialize the database connection on startup
    # The DBConnection class uses a singleton pattern, so this initializes it once.
    app.state.db_connection = DBConnection()
    print("MongoDB connection established.")
    
    yield  # The application runs while the context manager is active
    
    print("Application shutdown...")
    # Safely close the MongoDB client connection on shutdown
    if DBConnection._client:
        DBConnection._client.close()
        print("MongoDB connection closed.")

# Create the FastAPI application instance with the lifespan manager
app = FastAPI(
    title="Manufacturing Management API",
    description="API for managing the end-to-end manufacturing process.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(product_routes.router)

@app.get("/", tags=["Health Check"])
def health_check():
    """
    A simple health check endpoint.
    Returns a success message if the application is running.
    """
    return {"status": "healthy", "message": "Welcome to the Manufacturing Management API!"}

# This block allows running the app directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
