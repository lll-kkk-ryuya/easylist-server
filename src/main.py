import os
from supabase import create_client, Client
from cors_config import add_cors_middleware
# main_test.py
from llama_index.core.response.schema import Response, StreamingResponse
from starlette.responses import Response as StarletteResponse
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
# 正しいrouterインスタンスのインポート
from src.router.room.chat.mainbot import QueryService
import json
from typing import Optional
from uuid import uuid4, UUID
import asyncio
from starlette.websockets import WebSocketDisconnect
import os
import uvicorn

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

query_engine = None
app_ready = False

@app.on_event("startup")
async def startup_event():
    global query_engine 
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
    app_ready = True  # アプリケーションの準備が完了

@app.get("/health")
def health_check():
    if app_ready:
        return {"status": "ok"}
    else:
        return StarletteResponse(content={"status": "starting"}, status_code=503)

#リアルタイム通信
#StreamingResponseのprint_response_streamという関数は文字を一つ一つ出現させることが可能
# WebSocketエンドポイントを定義
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global query_engine  # グローバル変数を参照
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
