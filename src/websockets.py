from fastapi import WebSocket


class ConnectionManager:
    """
    Keeps track of current WebSockets clients so that we can broadcast() to them.

    From FastAPI tutorial: https://fastapi.tiangolo.com/advanced/websockets/
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
