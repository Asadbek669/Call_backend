from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    # yangi client online xabari
    for c in clients:
        if c != ws:
            await c.send_json({"type": "peer_online"})

    try:
        while True:
            data = await ws.receive_json()

            # Qo‘ng‘iroq bosildi
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
        for c in clients:
            await c.send_json({"type": "peer_offline"})
