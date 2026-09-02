import json

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket
    ):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

        print(f"User {user_id} connected")
        print(
            f"Active connections: "
            f"{len(self.active_connections[user_id])}"
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket
    ):
        connections = self.active_connections.get(user_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self.active_connections.pop(user_id, None)

        print(f"User {user_id} disconnected")

    async def send_to_user(
        self,
        user_id: int,
        message: dict
    ):
        connections = self.active_connections.get(user_id)

        if not connections:
            print(f"No active WebSocket for user {user_id}")
            return

        print(
            f"Sending notification to user {user_id} "
            f"on {len(connections)} connection(s)"
        )

        disconnected = []

        for websocket in connections.copy():
            try:
                await websocket.send_text(
                    json.dumps(message)
                )

                print(
                    f"Notification sent to user {user_id}"
                )

            except (WebSocketDisconnect, RuntimeError):
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(user_id, websocket)


manager = ConnectionManager()