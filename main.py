from fastapi import FastAPI
from vector_engines import VectorStoreAndQueryEngine
from sql import NLSQLQueryEngineManager
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from llama_index.tools import ToolMetadata
from llama_index.tools.query_engine import QueryEngineTool
from llama_index.query_engine.router_query_engine import RouterQueryEngine
from llama_index.selectors.llm_selectors import LLMMultiSelector
from llama_index import ServiceContext
from llama_index.llms import OpenAI
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


# VectorStoreAndQueryEngineインスタンスの作成
vector_store_query_engine_manager = VectorStoreAndQueryEngine(path="chroma_db")

# コレクション名のリスト
collection_names = ["bunn_senn2", "keizai5", "hougakubu5", "shougakub1", "rikougakubu1"]

# クエリエンジンを格納するための辞書を作成
query_engines_dict = {}

# 各コレクションに対してクエリエンジンを初期化し、辞書に追加
for collection_name in collection_names:
    # add_vector_query_engineメソッドを使用してクエリエンジンを追加
    vector_store_query_engine_manager.add_vector_query_engine(collection_name, model="gpt-4", temperature=0.4, similarity_top_k=5)
    
    # コレクション名をキーとして、対応するクエリエンジンオブジェクトを辞書に追加
    query_engines_dict[collection_name] = vector_store_query_engine_manager.vector_query_engines[collection_name]

# NLSQLQueryEngineManagerインスタンスの作成と辞書への追加
engine = create_engine('sqlite:///example.db', echo=True)
metadata = MetaData()
nlsql_manager = NLSQLQueryEngineManager(engine=engine)
table_name = "all_curce"
query_engines_dict[table_name] = nlsql_manager.create_nlsql_query_engine(table_name)

# 確認のため、各クエリエンジンの情報を表示
#for key, value in query_engines_dict.items():
    #print(f"Collection: {key}, Query Engine: {value}")

query_engine_tools = [
    QueryEngineTool(
        query_engine=query_engines_dict["rikougakubu1"],
        metadata=ToolMetadata(
            name="Engineering Department",
            description=(
                "Provides comprehensive data excluding course information for the Engineering Department, "
                "such as enrollment requirements, graduation criteria, and advancement conditions."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engines_dict["hougakubu5"],
        metadata=ToolMetadata(
            name="Law Department",
            description=(
                "Provides comprehensive data excluding course information for the Law Department, "
                "such as enrollment requirements, graduation criteria, and advancement conditions."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engines_dict["keizai5"],
        metadata=ToolMetadata(
            name="Economics Department",
            description=(
                "Provides comprehensive data excluding course information for the Economics Department, "
                "such as enrollment requirements, graduation criteria, and advancement conditions."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engines_dict["bunn_senn2"],
        metadata=ToolMetadata(
            name="Literature Department",
            description=(
                "Provides comprehensive data excluding course information for the Literature Department, "
                "such as enrollment requirements, graduation criteria, and advancement conditions."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engines_dict["shougakub1"],
        metadata=ToolMetadata(
            name="Commerce Department",
            description=(
                "Provides comprehensive data excluding course information for the Commerce Department, "
                "such as enrollment requirements, graduation criteria, and advancement conditions."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engines_dict['all_curce'],
        metadata=ToolMetadata(
            name="allcurce",
            description=(
                "Course data: ID, campus, name, field, term, schedule, mode, year, faculties, URL."
            ),
        ),
    ),
]
llm = OpenAI(temperature=0, model="gpt-4")
service_context = ServiceContext.from_defaults(llm=llm)
router_query_engine = RouterQueryEngine(
    selector=LLMMultiSelector.from_defaults(service_context=service_context),
    query_engine_tools=query_engine_tools, verbose=True
)
res=router_query_engine.query("文学部の一年の必修語学科目について教えて")
print(res)