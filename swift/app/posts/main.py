from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from datetime import datetime
from bson import ObjectId

from ..shared.utils.database import mongodb
from ..shared.config.settings import get_settings

settings = get_settings()

app = FastAPI(title="Posts Service")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
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

@app.websocket("/ws/posts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/posts/")
async def create_post(content: str, user_id: str):
    post = {
        "content": content,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "likes": 0,
        "comments": []
    }
    result = mongodb.posts.insert_one(post)
    post["_id"] = str(result.inserted_id)
    
    # Broadcast new post to all connected clients
    await manager.broadcast(json.dumps({
        "type": "new_post",
        "data": post
    }))
    
    return post

@app.get("/posts/")
async def get_posts(skip: int = 0, limit: int = 10):
    posts = await mongodb.posts.find().sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    for post in posts:
        post["_id"] = str(post["_id"])
    return posts

@app.post("/posts/{post_id}/like")
async def like_post(post_id: str, user_id: str):
    post = mongodb.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    mongodb.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"likes": 1}}
    )
    
    # Broadcast like update
    await manager.broadcast(json.dumps({
        "type": "post_liked",
        "data": {
            "post_id": post_id,
            "user_id": user_id,
            "likes": post["likes"] + 1
        }
    }))
    
    return {"message": "Post liked successfully"}

@app.post("/posts/{post_id}/comment")
async def add_comment(post_id: str, user_id: str, content: str):
    comment = {
        "user_id": user_id,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }
    
    mongodb.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )
    
    # Broadcast new comment
    await manager.broadcast(json.dumps({
        "type": "new_comment",
        "data": {
            "post_id": post_id,
            "comment": comment
        }
    }))
    
    return {"message": "Comment added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 