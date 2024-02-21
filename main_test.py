import os
from supabase import create_client, Client
# main_test.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# 正しいrouterインスタンスのインポート
from router.room.room_router import router as room_router
from router.room.chat.mainbot import QueryService

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()
# 正しくrouterをアプリケーションに追加

from fastapi import FastAPI, HTTPException
from supabase import create_client, Client

# 環境変数からSupabaseの情報を取得
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

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
    vector_store_path = "chroma_db"
    db_url = 'sqlite:///example.db'
    collection_names = ["bunn_senn4", "keizai5", "hougakubu5", "shougakub1", "rikougakubu1"]
    table_name = "all_curce"
    tool_metadata = {
    "rikougakubu1": {
        "name": "Engineering Department",
        "description": "Provides comprehensive data excluding course information for the Engineering Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "hougakubu5": {
        "name": "Law Department",
        "description": "Provides comprehensive data excluding course information for the Law Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "keizai5": {
        "name": "Economics Department",
        "description": "Provides comprehensive data excluding course information for the Economics Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "bunn_senn4": {
        "name": "Literature Department",
        "description": "Provides comprehensive data excluding course information for the Literature Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "shougakub1": {
        "name": "Commerce Department",
        "description": "Provides comprehensive data excluding course information for the Commerce Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "all_curce": {
        "name": "Course Data",
        "description": "Course data: ID, campus, name, field, term, schedule, mode, year, faculties, URL. Covers all departments and provides detailed information on each course offered."
    }
}
    
    query_service = QueryService(vector_store_path, db_url,collection_names,table_name,tool_metadata)
    await query_service.setup_engines()
    query_engine = await query_service.query_engine()
    result = query_engine.query(request.message)
    standard_response = result.get_response()
    reply_from_bot = standard_response.response
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
    delete_result = supabase.table("ChatRoom").delete().eq("id", chatroom_id).execute()

    return {"message": "チャットルームが正常に削除されました。"}


@app.get("/chatroom/{chatroom_id}/history")
async def get_chat_history(chatroom_id: str):
    history = supabase.table("Prompt").select("*").eq("chatRoomId", chatroom_id).execute()
    if history.error:
        raise HTTPException(status_code=500, detail="履歴の取得に失敗しました。")
    return history.data


class ChatRoomCreate(BaseModel):
    name: str
    userId: str

@app.post("/chatroom/create")
async def create_chatroom(request: ChatRoomCreate):
    chatroom = supabase.table("ChatRoom").insert({"name": request.name, "userId": request.userId}).execute()
    if chatroom.error:
        raise HTTPException(status_code=500, detail="チャットルームの作成に失敗しました。")
    return chatroom.data

#リアルタイム通信
@app.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data} in chatroom {chatroom_id}")
