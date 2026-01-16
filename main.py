from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Klientlarni saqlash
clients = {}

@app.get("/")
async def root():
    return {"message": "Audio Call Signaling Server", "status": "online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Client ID berish
    client_id = id(websocket)
    clients[client_id] = websocket
    
    print(f"Client connected: {client_id}, Total clients: {len(clients)}")
    
    # Boshqa clientlarga yangi online xabarini yuborish
    try:
        for cid, client in clients.items():
            if cid != client_id:
                try:
                    await client.send_json({
                        "type": "peer_online",
                        "clientId": client_id
                    })
                except:
                    pass
        
        # O'ziga online statusini yuborish
        await websocket.send_json({
            "type": "self_online",
            "clientId": client_id,
            "onlineCount": len(clients)
        })
        
        # Asosiy loop
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            # Call boshlash
            if message_type == "call":
                print(f"Call started by {client_id}")
                for cid, client in clients.items():
                    if cid != client_id:
                        try:
                            await client.send_json({
                                "type": "call_started",
                                "from": client_id
                            })
                        except:
                            pass
            
            # WebRTC signaling
            elif message_type == "signal":
                target_client = data.get("target", "all")
                
                if target_client == "all":
                    # Barchaga yuborish (masalan, STUN/ICE)
                    for cid, client in clients.items():
                        if cid != client_id:
                            try:
                                await client.send_json({
                                    "type": "signal",
                                    "from": client_id,
                                    "data": data.get("data")
                                })
                            except:
                                pass
                else:
                    # Faqat ma'lum bir clientga
                    target_id = data.get("targetId")
                    if target_id in clients:
                        try:
                            await clients[target_id].send_json({
                                "type": "signal",
                                "from": client_id,
                                "data": data.get("data")
                            })
                        except:
                            pass
            
            # Online clientlar ro'yxati
            elif message_type == "get_online":
                online_ids = list(clients.keys())
                await websocket.send_json({
                    "type": "online_list",
                    "clients": online_ids
                })
                
    except WebSocketDisconnect:
        print(f"Client disconnected: {client_id}")
        if client_id in clients:
            del clients[client_id]
        
        # Boshqalarga offline xabari
        for cid, client in clients.items():
            try:
                await client.send_json({
                    "type": "peer_offline",
                    "clientId": client_id
                })
            except:
                pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
