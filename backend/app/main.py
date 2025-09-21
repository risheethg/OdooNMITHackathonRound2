import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

# Importing the connection manager from the core directory
from app.core.db_connection import DBConnection
# Import the routes
from pymongo import MongoClient
from app.core.db_connection import DBConnection

from app.routes.user_routes import router as auth_router, user_router
from app.routes.work_order_route import router as work_order_router
from app.routes.work_centre_route import router as work_centre_router
from app.routes import product_routes, bom_route
from app.routes.manufacture_routes import router as manufacture_router
from app.routes.websocket_routes import router as websocket_router
from app.routes.ledger_routes import router as ledger_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.inventory_route import router as inventory_router
from app.core.logger import logs 
from app.service.automation_service import AutomationService
from app.service.polling_service import polling_service
import inspect
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application startup...", loggName=log_info, pid=os.getpid())
    db_connection = DBConnection()
    app.state.db_connection = db_connection
    logs.define_logger(level=logging.INFO, message="MongoDB connection established.", loggName=log_info, pid=os.getpid())
    
    # --- AUTOMATION: Setup and start the polling service ---
    db = db_connection.get_database()
    automation_service = AutomationService(db)
    polling_service.register_task(automation_service.polling_task)
    await polling_service.start_polling()
    
    yield
    
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application shutdown...", loggName=log_info, pid=os.getpid())
    # --- AUTOMATION: Stop the polling service ---
    await polling_service.stop_polling()
    if DBConnection._client:
        DBConnection._client.close()
        logs.define_logger(level=logging.INFO, message="MongoDB connection closed.", loggName=log_info, pid=os.getpid())

app = FastAPI(
    title="Manufacturing Management API",
    description="API for managing the end-to-end manufacturing process.",
    version="1.0.0",
    lifespan=lifespan
)

# --- ADD THIS BLOCK FOR CORS ---
# List of allowed origins (your frontend's URL)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allows specific origins
    allow_credentials=True,      # Allows cookies to be included in requests
    allow_methods=["*"],         # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allows all headers
)
# --------------------------------

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(product_routes.router, prefix="/api")
app.include_router(bom_route.router, prefix="/api")
app.include_router(manufacture_router, prefix="/api")
app.include_router(ledger_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")

@app.get("/", tags=["Health Check"])
def health_check():
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Health check endpoint called.", loggName=log_info, pid=os.getpid())
    return {"status": "healthy", "message": "Welcome to the Manufacturing Management API!"}

#include the routes
app.include_router(work_order_router, prefix="/api")
app.include_router(work_centre_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
