
from router.room.chat.vector_engines import VectorStoreAndQueryEngine
from router.room.chat.sql import NLSQLQueryEngineManager
from sqlalchemy import create_engine
from llama_index.tools import ToolMetadata
from llama_index.tools.query_engine import QueryEngineTool
from llama_index.query_engine.router_query_engine import RouterQueryEngine
from llama_index.selectors.llm_selectors import LLMMultiSelector
from llama_index import ServiceContext
from llama_index.llms import OpenAI
import os
from dotenv import load_dotenv
import os
# .env ファイルを読み込む
load_dotenv()
# 環境変数 'OPENAI_API_KEY' を取得
openai_api_key = os.getenv('OPENAI_API_KEY')

# query_engines_dict をファイルに保存する
class QueryEngineManager:
    def __init__(self, db_url):
        self.vector_store_query_engine_manager = VectorStoreAndQueryEngine()
        self.engine = create_engine(db_url, echo=True)
        self.nlsql_manager = NLSQLQueryEngineManager(engine=self.engine)
        self.query_engines_dict = {}
        self.query_engine_tools = []
        self.llm = OpenAI(temperature=0.2, model="gpt-4")
        self.service_context = ServiceContext.from_defaults(llm=self.llm)

    def setup_vector_query_engines(self, collection_names):
        for collection_name in collection_names:
            self.vector_store_query_engine_manager.add_vector_query_engine(collection_name, model="gpt-4", temperature=0.4, similarity_top_k=5)
            self.query_engines_dict[collection_name] = self.vector_store_query_engine_manager.vector_query_engines[collection_name]

    def add_nlsql_query_engine(self, table_name):
        self.query_engines_dict[table_name] = self.nlsql_manager.create_nlsql_query_engine(table_name)

    def setup_query_engine_tools(self, tool_metadata):
        for collection_name, metadata in tool_metadata.items():
            self.query_engine_tools.append(
                QueryEngineTool(
                    query_engine=self.query_engines_dict[collection_name],
                    metadata=ToolMetadata(name=metadata["name"], description=metadata["description"])
                )
            )

    def query_engine(self):
        router_query_engine = RouterQueryEngine(
            selector=LLMMultiSelector.from_defaults(service_context=self.service_context),
            query_engine_tools=self.query_engine_tools, verbose=True, service_context=self.service_context
        )
        return router_query_engine
