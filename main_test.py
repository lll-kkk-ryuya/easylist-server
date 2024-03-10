import os
from supabase import create_client, Client
from cors_config import add_cors_middleware
from llama_index.core.response.schema import Response, StreamingResponse
# main_test.py
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# 正しいrouterインスタンスのインポート
from router.room.chat.mainbot import QueryService
import uuid
from typing import Optional
from uuid import uuid4
import asyncio
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()
add_cors_middleware(app)


class QueryRequest(BaseModel):
    user_id: Optional[str] = None  # ユーザーID
    chatroom_id: Optional[str] = None # チャットルームID
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
    if isinstance(result, Response):
        print("resultはResponse型です。")
        reply_from_bot = result.response
    elif isinstance(result, StreamingResponse):
        print("resultはStreamingResponse型です。")
        reply_from_bot = result.get_response().response
        #reply_from_bot = response_object.response_txt
    else:
        print("resultは未知の型です。")
        reply_from_bot = "エラー: 未知のレスポンスタイプ"
    print(type(result))
    # Promptテーブルにユーザーのクエリとレスポンスを保存
    chatroom_id = request.chatroom_id
    if chatroom_id is None:
        chatroom_response = await create_chatroom()
        chatroom_id = chatroom_response['id']
    prompt_data = {
        "chatRoomId": chatroom_id,
        "userId": request.user_id if request.user_id is not None else None,
        "message": request.message,
        "replyFromBot": reply_from_bot  # チャットボットの応答
    }
    inserted_prompt = supabase.table("Prompt").insert(prompt_data).execute()
    if inserted_prompt.error():
        raise HTTPException(status_code=400, detail="Failed to save prompt.")


    result = {"prompt_id": inserted_prompt['id'], "reply_from_bot": reply_from_bot,"createdAt":inserted_prompt["createdAt"]}
    print(result)
    return result



@app.post("/prompt_test", response_model=ResponseModel)
async def handle_querytest(request: QueryRequest):
    reply_from_bot=request.message
    chatroom_id = request.chatroom_id
    if chatroom_id is None:
        chatroom_response = await create_chatroom()
        chatroom_id = chatroom_response['id']
    prompt_data = {
        "chatRoomId": chatroom_id,
        "userId": request.user_id if request.user_id is not None else None,
        "message": request.message,
        "replyFromBot": reply_from_bot  # チャットボットの応答
    }
    inserted_prompt = supabase.table("Prompt").insert(prompt_data).execute()
    if inserted_prompt.data:
        prompt_id = inserted_prompt.data[0].get('id')
        createdAt = inserted_prompt.data[0].get('createdAt')
        result = {"prompt_id": prompt_id, "reply_from_bot": reply_from_bot, "createdAt": createdAt}

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




async def create_chatroom(chatroom_name: Optional[str] = None, user_id: Optional[str] = None):
    id_value = str(uuid4())
    
    # 非同期実行に適応させるため、同期コードをrun_in_executorでラップ
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: supabase.table("ChatRoom").insert({
        "id": id_value,
        "name": chatroom_name if chatroom_name else "Untitled Chatroom",
        "userId": user_id
    }).execute())

  
    
    return {"id": id_value}


#リアルタイム通信
#StreamingResponseのprint_response_streamという関数は文字を一つ一つ出現させることが可能
@app.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        await websocket.send_text(f"Message text was: {data} in chatroom {chatroom_id}")
