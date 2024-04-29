import os
from supabase import create_client, Client
from cors_config import add_cors_middleware
from llama_index.core.base.response.schema import StreamingResponse,AsyncStreamingResponse,Response
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
from starlette.websockets import WebSocketDisconnect ,WebSocketState
import os
from time import time
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
    global query_engine, app_ready
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
    #"all_curce": {"name": "Course Data","description": "Course data: ID, campus, name, field, term, schedule, mode, year, faculties, URL. Covers all departments and provides detailed information on each course offered."}
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
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global query_engine
    await websocket.accept()
    logging.debug("WebSocket connection accepted.")

    try:
        while True:
            now = time()
            data = await websocket.receive_text()
            logging.debug(f"Received data: {data}")

            data = json.loads(data)
            message_id = data['id']
            query_str = data.get('content')
            logging.debug(f"Processing query: {query_str}")

            # result = query_engine.query(query_str)
            result = await query_engine.aquery(query_str)
            logging.debug(f"Query result type: {type(result)}")

            if isinstance(result, AsyncStreamingResponse):
                logging.debug(f"Type of async_response_gen: {type(result.async_response_gen)}")
                async for text in result.async_response_gen():
                    reply_json_str = json.dumps({"id": message_id, "reply_from_bot": text}, ensure_ascii=False)
                    logging.debug(f"Sending streaming response: {reply_json_str}")
                    await websocket.send_text(reply_json_str)
            elif isinstance(result, Response):
                reply_from_bot = result.response
                reply_json_str = json.dumps({"id": message_id, "reply_from_bot": reply_from_bot}, ensure_ascii=False)
                logging.debug(f"Sending response: {reply_json_str}")
                await websocket.send_text(reply_json_str)
    except Exception as e:
        logging.error(f"Error during websocket communication: {e}")
        # エラー発生時にWebSocketがまだ開いていればクローズする
        if websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()
            logging.debug("WebSocket connection closed due to an error.")

@app.websocket("/ws_test")
async def websocket_endpoint(websocket: WebSocket):
    global query_engine  
    await websocket.accept()
    try:
        while True:
           
            now = time()
            data = await websocket.receive_text()
            data = json.loads(data)
            message_id = data['id']
            query_str = data.get('content')
            #result = query_engine.query(query_str)
            result = await query_engine.aquery(query_str)
            
            if isinstance(result, AsyncStreamingResponse):
                
                async for text in result.async_response_gen:
                    reply_json_str = json.dumps({"id": message_id, "reply_from_bot": text}, ensure_ascii=False)
                    print(reply_json_str)
                    await websocket.send_text(reply_json_str)
                end_time = time()  
                elapsed_time = end_time - now  
                print(f"Query execution took {elapsed_time} seconds.")  
            elif isinstance(result, Response):
                
                reply_from_bot = result.response
                print(reply_from_bot)
                reply_json_str = json.dumps({"id": message_id, "reply_from_bot": reply_from_bot}, ensure_ascii=False)
                await websocket.send_text(reply_json_str)
                end_time = time() 
                elapsed_time = end_time - now  
                print(f"Query execution took {elapsed_time} seconds.")
    except Exception as e:
        print(f"Error during websocket communication: {e}")
    finally:
        await websocket.close()