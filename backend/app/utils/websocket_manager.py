from fastapi import WebSocket
from typing import Dict, Optional

class ConnectionManager:
    """
    Manages active WebSocket connections using a topic-based approach.
    Each connection is identified by a unique client_id, which is a combination
    of a topic and a project_id (e.g., "srs_generation_project-123").
    """
    def __init__(self):
        # This is the only dictionary needed. It stores the actual WebSocket objects.
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Stores a new, already accepted WebSocket connection using its unique client_id.
        """
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str):
        """Removes a WebSocket connection from the manager."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_to_topic(self, project_id: str, data: dict,topic: str):
        """
        Sends a JSON message to a client subscribed to a specific topic for a project.
        This is the primary method your services should use.
        """
        # Construct the unique client_id from the topic and project_id
        client_id = f"{topic}_{project_id}"
        
        connection = self.active_connections.get(client_id)
        if connection:
            try:
                await connection.send_json(data)
            except RuntimeError:
                # The client disconnected without a proper handshake. Clean up.
                await self.disconnect(client_id)

# Create a single, shared instance to be used across the application
connection_manager = ConnectionManager()