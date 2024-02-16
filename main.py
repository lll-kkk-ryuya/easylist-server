from fastapi import FastAPI
from query_engines import QueryEngineManager
import pickle
import os
os.environ["OPENAI_API_KEY"] = "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"
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# 環境変数や設定値
# インスタンスの作成に必要なパラメータ
vector_store_path = "path/to/chroma_db"
db_url = 'sqlite:///path/to/example.db'
openai_api_key = "your_openai_api_key"

# QueryEngineManagerインスタンスの作成
qem = QueryEngineManager(vector_store_path, db_url, openai_api_key)
# セットアップするコレクションの名前
collection_names = ["bunn_senn4", "keizai5", "hougakubu5", "shougakub1", "rikougakubu1"]
qem.setup_vector_query_engines(collection_names)

# NLSQLクエリエンジンを追加するテーブル名
table_name = "all_curce"
qem.add_nlsql_query_engine(table_name)
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
# クエリエンジンツールのセットアップ
qem.setup_query_engine_tools(tool_metadata)

# インスタンスの作成
# 実行するクエリのテキスト
query_text = "文学部の一年生の必修語学科目について教えてください。"

# クエリの実行と結果の取得
result = qem.query(query_text)

# 結果の出力
print(result)

