from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

from jose import JWTError, jwt

from app.config import SECRET_KEY, ALGORITHM


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("WebSocket endpoint called")

    token = websocket.query_params.get("token")

    if not token:
        print("WebSocket rejected: no token")
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            print("WebSocket rejected: no user_id")
            await websocket.close(code=1008)
            return

        user_id = int(user_id)

        print(f"WebSocket authenticated for user {user_id}")

    except (JWTError, ValueError) as e:
        print(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    print(f"WebSocket registered for user {user_id}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)