import logging
import inspect
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..utils.websocket_manager import connection_manager
from ..core.logger import logs


router = APIRouter(tags=["Websockets"])


@router.websocket("/ws/")
async def progress_websocket_endpoint(
    websocket: WebSocket,
    topic: str = Query(..., description="srs_progress,epic_progress,ac_progress,qgen_progress"),
    project_id: str = Query(...)
):
    """
    A single, dynamic WebSocket endpoint for all real-time progress updates.
    """
    logg_name = inspect.stack()[0]
    client_id = f"{topic}_{project_id}"
    
    await websocket.accept()
    await connection_manager.connect(websocket, client_id)
    
    # Log successful connection
    logs.define_logger(
        logging.INFO, None, logg_name, 
        message=f"WebSocket connected: client_id='{client_id}', project_id='{project_id}'"
    )
    
    try:
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        # Log clean disconnection
        logs.define_logger(
            logging.INFO, None, logg_name, 
            message=f"WebSocket client '{client_id}' disconnected cleanly."
        )
    except Exception as e:
        # Log unexpected errors
        logs.define_logger(
            logging.ERROR, None, logg_name, 
            message=f"WebSocket error for client '{client_id}': {e}"
        )
    finally:
        await connection_manager.disconnect(client_id)
        # Log connection cleanup
        logs.define_logger(
            logging.INFO, None, logg_name, 
            message=f"Cleaned up connection for client '{client_id}'."
        )
