import os
from supabase import create_client, Client
# main_test.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# 正しいrouterインスタンスのインポート
from router.room.chat.mainbot import QueryService
import uuid

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()
# 正しくrouterをアプリケーションに追加

from fastapi import FastAPI, HTTPException
from supabase import create_client, Client


class QueryRequest(BaseModel):
    user_id: str  # ユーザーID
    chatroom_id: str # チャットルームID
    message: str  # ユーザーからのメッセージ

class ResponseModel(BaseModel):
    prompt_id: int  # 生成されたプロンプトID
    reply_from_bot: str  # チャットボットからのレスポンス

@app.post("/prompt", response_model=ResponseModel)
async def handle_query(request: QueryRequest):
    #チャットボットの処理
    db_url = 'sqlite:///example.db'
    collection_names = ["bunngakubu", "keizai", "法学部", "shougakub", "rikougakubu"]
    table_name = "all_curce"
    tool_metadata = {
    "rikougakubu": {
        "name": "Engineering Department",
        "description": "Provides comprehensive data excluding course information for the Engineering Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "法学部": {
        "name": "Law Department",
        "description": "Provides comprehensive data excluding course information for the Law Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "keizai": {
        "name": "Economics Department",
        "description": "Provides comprehensive data excluding course information for the Economics Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "bunngakubu": {
        "name": "Literature Department",
        "description": "Provides comprehensive data excluding course information for the Literature Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "shougakub": {
        "name": "Commerce Department",
        "description": "Provides comprehensive data excluding course information for the Commerce Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "all_curce": {
        "name": "Course Data",
        "description": "Course data: ID, campus, name, field, term, schedule, mode, year, faculties, URL. Covers all departments and provides detailed information on each course offered."
    }
}
    
    query_service = QueryService(db_url,collection_names,table_name,tool_metadata)
    await query_service.setup_engines()
    query_engine = await query_service.query_engine()
    result = query_engine.query(request.message)
    reply_from_bot = result.response
    # query_engine.query を呼び出して StreamingResponse オブジェクトを取得
    print(reply_from_bot)
    #response_text=result.response
    # チャットボットからのレスポンスを生成する（ダミー）
    #response_text = "これはダミーレスポンスです。"
    
    # Promptテーブルにユーザーのクエリとレスポンスを保存
    prompt_data = {
        "chatRoomId": request.chatroom_id,
        "userId": request.user_id,
        "message": request.message,
        "replyFromBot": reply_from_bot
    }
    inserted_prompt = supabase.table("Prompt").insert(prompt_data).execute()
    #if inserted_prompt.error:
        #raise HTTPException(status_code=400, detail="プロンプトの保存に失敗しました。")
    res = inserted_prompt.data[0]


    result = {"prompt_id": res['id'], "reply_from_bot": reply_from_bot,"createdAt":res["createdAt"]}
    print(result)
    return result

# 他のルーターを追加する場合
# app.include_router(room_router)
@app.delete("/chatroom/{chatroom_id}")
async def delete_chatroom(chatroom_id: str):

    # 関連するプロンプトを削除
    delete_prompts_result = supabase.table("Prompt").delete().eq("chatRoomId", chatroom_id).execute()

    # チャットルームを削除
    delete_result = supabase.table("ChatRoom").delete().eq("id", chatroom_id).execute()
    return {"message": "チャットルームが正常に削除されました。"}




class ChatRoomCreate(BaseModel):
    name: str
    userId: str

@app.post("/chatroom/create")
async def create_chatroom(request: ChatRoomCreate):
    # UUIDを生成
    id_value = str(uuid.uuid4())
    # 生成したUUIDを使用してデータを挿入
    chatroom = supabase.table("ChatRoom").insert({
        "id": id_value,  # UUIDをidとして設定
        "name": request.name,
        "userId": request.userId
    }).execute()
    return chatroom.data

#リアルタイム通信
@app.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        await websocket.send_text(f"Message text was: {data} in chatroom {chatroom_id}")

