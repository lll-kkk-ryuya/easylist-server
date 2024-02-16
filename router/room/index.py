from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RoomCreateRequest(BaseModel):
    name: str
    description: str
    capacity: int

@router.post("/create")
async def create_room(data: RoomCreateRequest):
    ...

@router.delete("/delete/{room_id}")
async def delete_room(room_id: int):
    ...
