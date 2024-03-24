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
import json
from typing import Optional
from uuid import uuid4, UUID
import asyncio
from starlette.websockets import WebSocketDisconnect
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
    prompt_id: str
    reply_from_bot: str
    createdAt: str



@app.post("/prompt", response_model=ResponseModel)
async def handle_query(request: QueryRequest):
    chatroom_id = request.chatroom_id
    if chatroom_id is None or chatroom_id == "":
        chatroom_response = await create_chatroom()
        chatroom_id = chatroom_response['id']  # 新しいチャットルームIDを取得して設定
    # userIdがNoneまたは空文字列の場合の処理を確認
    user_id = request.user_id if request.user_id not in [None, ""] else None
    #チャットボットの処理
    #result = query_engine.query(request.message)
    if isinstance(result, Response):
        print("resultはResponse型です。")
        reply_from_bot = result.response
    elif isinstance(result, StreamingResponse):
        print("resultはStreamingResponse型です。")
        reply_from_bot = result.get_response().response
        #reply_from_bot = result.response_txt  一つずつ単語を抽出
    else:
        print("resultは未知の型です。")
        reply_from_bot = "エラー: 未知のレスポンスタイプ"
    print(type(result))
    # Promptテーブルにユーザーのクエリとレスポンスを保存
    prompt_data = {
        "chatRoomId": chatroom_id,
        "userId": user_id,  # 修正されたuserIdを使用
        "message": request.message,
        "replyFromBot": reply_from_bot
    }
    inserted_prompt = supabase.table("Prompt").insert(prompt_data).execute()
    if inserted_prompt.data:
        prompt_id = str(inserted_prompt.data[0].get('id'))
        createdAt = inserted_prompt.data[0].get('createdAt')
        result = {"prompt_id": prompt_id, "reply_from_bot": reply_from_bot, "createdAt": createdAt}
    print(result)
    return result



@app.post("/prompt_test", response_model=ResponseModel)
async def handle_querytest(request: QueryRequest):
    reply_from_bot="レスです"
    chatroom_id = request.chatroom_id
    if chatroom_id is None or chatroom_id == "":
        chatroom_response = await create_chatroom()
        chatroom_id = chatroom_response['id']  # 新しいチャットルームIDを取得して設定
    # userIdがNoneまたは空文字列の場合の処理を確認
    user_id = request.user_id if request.user_id not in [None, ""] else None

    prompt_data = {
        "chatRoomId": chatroom_id,
        "userId": user_id,  # 修正されたuserIdを使用
        "message": request.message,
        "replyFromBot": reply_from_bot
    }
    inserted_prompt = supabase.table("Prompt").insert(prompt_data).execute()
    if inserted_prompt.data:
        prompt_id = str(inserted_prompt.data[0].get('id'))
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

class ChatroomRequest(BaseModel):
    chatroom_id: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None

async def create_chatroom(chatroom_id: Optional[str] = None, user_id: Optional[str] = None, name: Optional[str] = None):
    id_value = str(uuid4())
    # ここにデータベース挿入のロジックを実装する
    # デモ用には、ダミーのレスポンスを返します
    chatroom_id = chatroom_id if chatroom_id else id_value
    name=name if name else "Untitled Chatroom"
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, lambda: supabase.table("ChatRoom").insert({
        "id": chatroom_id,
        "name": name,
        "userId": user_id
    }).execute())

    return {"id": chatroom_id, "name": name, "userId": user_id}


#リアルタイム通信
#StreamingResponseのprint_response_streamという関数は文字を一つ一つ出現させることが可能
# WebSocketエンドポイントを定義
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    db_url = 'sqlite:///example.db'
    collection_names = ["bunngakubu", "keizai", "hougakubu", "shougakub", "rikougakubu"]
    table_name = "all_curce"
    tool_metadata = {
    "rikougakubu": {
        "name": "Engineering Department",
        "description": "Provides comprehensive data excluding course information for the Engineering Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    },
    "hougakubu": {
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
    print("起動")
    await websocket.accept()
    try:
        while True:
            # クライアントからメッセージを受信
            
            data = await websocket.receive_text()
            print(data)
            # query_engineを非同期的に取得（もしquery_engineの取得が非同期である場合）
            # query_engine = await query_service.get_query_engine()
            data = json.loads(data)
            query_str = data.get('content')
            print(query_str)
            print(type(query_str))
            # query_engine.queryが非同期関数である場合、awaitを使用して呼び出し
            result = query_engine.query(query_str)
            # resultの型に応じて処理を分岐
            print(type(result))
            if isinstance(result, Response):
                reply_from_bot = result.response
            elif isinstance(result, StreamingResponse):
                reply_from_bot =result.get_response().response
            else:
                reply_from_bot = "エラー: 未知のレスポンスタイプ"
            # 結果をクライアントに送信
            reply_json_str = json.dumps({ "reply_from_bot": reply_from_bot}, ensure_ascii=False)
            await websocket.send_text(reply_json_str)
            print("送信されたメッセージ:", reply_json_str)


    except WebSocketDisconnect:
        # WebSocketの接続がクライアントによって閉じられた場合
        print("WebSocket connection was closed")


@app.websocket("/ws_test")
async def websocket_endpoint(websocket: WebSocket):
    print("起動")
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            reply_from_bot="レスです"
            reply_from_bot_encoded = reply_from_bot.encode('utf-8')
            reply_from_bot_utf8 = reply_from_bot_encoded.decode('utf-8')
            reply_json_str = json.dumps({ "reply_from_bot": reply_from_bot_utf8 }, ensure_ascii=False)
            await websocket.send_text(reply_json_str)
            print("送信されたメッセージ:", reply_json_str)

    except WebSocketDisconnect:
        # WebSocketの接続がクライアントによって閉じられた場合
        print("WebSocket connection was closed")

