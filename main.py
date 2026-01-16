from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import json

app = FastAPI()

# Maksimum 2 ta ishtirokchi
clients: Dict[WebSocket, str] = {}


async def broadcast_ready():
    users = list(clients.items())
    if len(users) == 2:
        (ws1, name1), (ws2, name2) = users

        await ws1.send_text(json.dumps({
            "type": "ready",
            "peer": name2
        }))
        await ws2.send_text(json.dumps({
            "type": "ready",
            "peer": name1
        }))


async def broadcast_waiting():
    for ws in clients:
        await ws.send_text(json.dumps({
            "type": "waiting"
        }))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            data = json.loads(await ws.receive_text())

            # =====================
            # JOIN
            # =====================
            if data["type"] == "join":
                if len(clients) >= 2:
                    await ws.send_text(json.dumps({
                        "type": "error",
                        "message": "Xona band"
                    }))
                    await ws.close()
                    return

                clients[ws] = data["name"]
                print(f"JOIN: {data['name']}")

                if len(clients) == 1:
                    await broadcast_waiting()

                if len(clients) == 2:
                    await broadcast_ready()

            # =====================
            # CALL
            # =====================
            elif data["type"] == "call":
                # faqat signal beramiz (WebRTC keyin)
                for client in clients:
                    if client != ws:
                        await client.send_text(json.dumps({
                            "type": "call"
                        }))

            # =====================
            # WEBRTC SIGNAL
            # =====================
            elif data["type"] == "signal":
                for client in clients:
                    if client != ws:
                        await client.send_text(json.dumps({
                            "type": "signal",
                            "data": data["data"]
                        }))

    except WebSocketDisconnect:
        name = clients.get(ws, "unknown")
        print(f"DISCONNECT: {name}")

        if ws in clients:
            del clients[ws]

        # qolgan user yana waiting bo‘ladi
        await broadcast_waiting()
