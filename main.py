# FastAPI + WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        # boshida barcha klientlarga peer_online xabar
        for c in clients:
            if c != ws:
                await c.send_json({"type": "peer_online"})
        while True:
            data = await ws.receive_json()
            if data["type"] == "call":
                for c in clients:
                    if c != ws:
                        await c.send_json({"type": "call_started"})
    except WebSocketDisconnect:
        clients.remove(ws)
        for c in clients:
            await c.send_json({"type": "peer_offline"})
