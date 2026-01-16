from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Frontend papkani static fayllar sifatida xizmat qilish
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# WebSocket clientlari
clients = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    # yangi client online deb xabar
    for c in clients:
        if c != ws:
            await c.send_json({"type": "peer_online"})

    try:
        while True:
            data = await ws.receive_json()

            # Call tugmasi bosilganda
            if data["type"] == "call":
                for c in clients:
                    if c != ws:
                        await c.send_json({"type": "call_started"})

            # WebRTC signaling
            if data["type"] == "signal":
                for c in clients:
                    if c != ws:
                        await c.send_json({"type": "signal", "data": data["data"]})

    except WebSocketDisconnect:
        clients.remove(ws)
        # offline xabar
        for c in clients:
            await c.send_json({"type": "peer_offline"})
