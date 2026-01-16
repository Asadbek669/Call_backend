from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# index.html va CSS/JS ni xizmat qilish
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# WebSocket clients
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
            if data["type"] == "call":
                # barcha boshqa clientlarga call boshlandi deb yuborish
                for c in clients:
                    if c != ws:
                        await c.send_json({"type": "call_started"})
            if data["type"] == "signal":
                # WebRTC signaling uchun peerga yuborish
                for c in clients:
                    if c != ws:
                        await c.send_json({"type": "signal", "data": data["data"]})
    except WebSocketDisconnect:
        clients.remove(ws)
        for c in clients:
            await c.send_json({"type": "peer_offline"})
