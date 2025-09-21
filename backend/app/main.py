from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    product_routes,
    bom_routes,
    manufacture_routes,
    work_center_routes,
    analytics_routes,
    stock_ledger_routes,
    user_routes
)

app = FastAPI(
    title="Manufacturing ERP API",
    description="API for a modern, lean manufacturing management system.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This is the key change to allow your frontend to communicate with the backend.
origins = [
    "http://localhost",
    "http://localhost:8080", # Default for some local servers
    "http://127.0.0.1:8080",
    "http://localhost:5173", # Default for Vite
    "http://172.17.53.42:8080", # The IP from your error logs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(product_routes.router)
app.include_router(bom_routes.router)
app.include_router(manufacture_routes.router)
app.include_router(analytics_routes.router)
app.include_router(stock_ledger_routes.router)
app.include_router(user_routes.router)
app.include_router(work_center_routes.router)