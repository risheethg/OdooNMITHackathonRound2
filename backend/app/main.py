import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db_connection import DBConnection
# from app.core.firebase_app import initialize_firebase  # Firebase disabled for now

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application startup...", loggName=log_info, pid=os.getpid())

    # initialize_firebase()  # Firebase initialization skipped for now

    db_connection = DBConnection()
    app.state.db_connection = db_connection
    logs.define_logger(level=logging.INFO, message="MongoDB connection established.", loggName=log_info, pid=os.getpid())

    # Automation polling setup
    db = db_connection.get_database()
    automation_service = AutomationService(db)
    polling_service.register_task(automation_service.polling_task)
    await polling_service.start_polling()

    yield

    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Application shutdown...", loggName=log_info, pid=os.getpid())

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

# CORS setup: allow all origins (adjust as needed)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes without role-based dependencies on app level
app.include_router(product_routes.router)
app.include_router(bom_route.router)
app.include_router(manufacture_router)
app.include_router(ledger_router)
app.include_router(websocket_router)
app.include_router(inventory_router)
app.include_router(work_order_router)
app.include_router(work_centre_router)
app.include_router(analytics_router)


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
