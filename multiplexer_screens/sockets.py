from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(
    prefix="/websocket"
)

@router.websocket("/screen4")
async def visualise_screen4(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data_json = await websocket.receive_json()
            await websocket.send_json(data_json)
    except WebSocketDisconnect as disconnect:
        print(f"Disconnected due to {disconnect}")