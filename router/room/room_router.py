from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.get("/chat/")
async def get_chat(q):
    return {"q": q}

# 以下は、既存のコードの続きです
@router.post("/create")
async def create_room():
    # 部屋を作成するロジックを実装
    pass

@router.delete("/delete/{room_id}")
async def delete_room(room_id: int):
    # 部屋を削除するロジックを実装
    pass

