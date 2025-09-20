import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import MongoClient
from app.core.db_connection import DBConnection
from app.routes import product_routes,bom_route
from app.core.logger import logs 
import inspect
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application startup...", loggName=log_info, pid=os.getpid())
    app.state.db_connection = DBConnection()
    logs.define_logger(level=logging.INFO, message="MongoDB connection established.", loggName=log_info, pid=os.getpid())
    
    yield
    
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application shutdown...", loggName=log_info, pid=os.getpid())
    if DBConnection._client:
        DBConnection._client.close()
        logs.define_logger(level=logging.INFO, message="MongoDB connection closed.", loggName=log_info, pid=os.getpid())

app = FastAPI(
    title="Manufacturing Management API",
    description="API for managing the end-to-end manufacturing process.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(product_routes.router)
app.include_router(bom_route.router)


@app.get("/", tags=["Health Check"])
def health_check():
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Health check endpoint called.", loggName=log_info, pid=os.getpid())
    return {"status": "healthy", "message": "Welcome to the Manufacturing Management API!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )