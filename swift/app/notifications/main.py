from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
from datetime import datetime
from bson import ObjectId

from ..shared.utils.database import mongodb
from ..shared.config.settings import get_settings

settings = get_settings()

app = FastAPI(title="Notifications Service")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

manager = ConnectionManager()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            await manager.send_personal_message(data, user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.post("/notifications/")
async def create_notification(
    recipient_id: str,
    sender_id: str,
    notification_type: str,
    content: str
):
    notification = {
        "recipient_id": recipient_id,
        "sender_id": sender_id,
        "type": notification_type,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "read": False
    }
    
    result = mongodb.notifications.insert_one(notification)
    notification["_id"] = str(result.inserted_id)
    
    # Send notification to recipient if they're connected
    await manager.send_personal_message(
        json.dumps({
            "type": "new_notification",
            "data": notification
        }),
        recipient_id
    )
    
    return notification

@app.get("/notifications/{user_id}")
def get_notifications(user_id: str, skip: int = 0, limit: int = 10):
    notifications = mongodb.notifications.find(
        {"recipient_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit)#.list(length=limit)
    
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
    
    return notifications

@app.put("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: str):
    result = mongodb.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 


