
from src.router.room.chat.vector_engines import VectorStoreAndQueryEngine
from src.router.room.chat.sql import NLSQLQueryEngineManager
from sqlalchemy import create_engine
from llama_index.core.tools import ToolMetadata
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import QueryBundle
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core import ServiceContext
from llama_index.llms.openai import OpenAI
from llama_index.core.selectors.prompts import (
    DEFAULT_MULTI_SELECT_PROMPT_TMPL,
    DEFAULT_SINGLE_SELECT_PROMPT_TMPL,
    MultiSelectPrompt,
    SingleSelectPrompt,
)
from llama_index.core.output_parsers.selection import SelectionOutputParser
from llama_index.core.prompts.base import PromptTemplate
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
        self.choices = []
        self.llm = OpenAI(temperature=0.2, model="gpt-4",api_key=openai_api_key)
        self.service_context = ServiceContext.from_defaults(llm=self.llm)

    def setup_vector_query_engines(self, collection_names):
        for collection_name in collection_names:
            self.vector_store_query_engine_manager.add_vector_query_engine(collection_name, model="gpt-4", temperature=0.4, similarity_top_k=5)
            self.query_engines_dict[collection_name] = self.vector_store_query_engine_manager.vector_query_engines[collection_name]

    def add_nlsql_query_engine(self, table_name):
        self.query_engines_dict[table_name] = self.nlsql_manager.create_nlsql_query_engine(table_name)

    def setup_query_engine_tools(self):
        self.query_engine_tools = [
    QueryEngineTool(
        query_engine=self.query_engines_dict['keirikou.pdf'],
        metadata=ToolMetadata(
            name="Engineering Department",
            description=(
                "Provides data for students in  the Engineering Department, "
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=self.query_engines_dict['keihou.pdf'],
        metadata=ToolMetadata(
            name="Law Department",
            description=(
                "Provides data for students in the Law Department, "
            ),
        ),
    ),

    QueryEngineTool(
        query_engine=self.query_engines_dict['keikei.pdf'],
        metadata=ToolMetadata(
            name="Economics Department",
            description=(
                "Provides data for students in the the Economics Department, "
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=self.query_engines_dict["keibunn.pdf"],
        metadata=ToolMetadata(
            name="Literature Department",
            description=(
                "Provides data for students in the Literature Department, "
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=self.query_engines_dict['keishou.pdf'],
        metadata=ToolMetadata(
            name="Commerce Department",
            description=(
                "Provides data for students in the Commerce Department, "
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=self.query_engines_dict["keishou.pdf"],
        metadata=ToolMetadata(
            name="If no specific department is specified (general case)",
            description=(
                "If none of the choices provided in the list seem to directly address this question, please refer to this.If no specific department is specified (general case)\n"
            ),
        ),
    ),
    #QueryEngineTool(query_engine=self.query_engines_dict['all_curce'],metadata=ToolMetadata(name="全ての授業データ",description=("授業データ: コースID, キャンパス, 授業名, 学期,  時間割, 教授名, 形式(対面授業かオンライン授業か), 年度, 取得可能な学部, シラバスの詳細, URL。授業に関する時間割などの詳細は、こちらを参照してください。"),),),
]
      

    async def query_engine(self):
        llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo",api_key=openai_api_key)
        DEFAULT_TREE_SUMMARIZE_TMPL = (
    "以下に複数の情報源からのコンテキスト情報があります。\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "複数の情報源からの情報に基づいて、事前知識を使わずに以下の質問に答えてください。\n"
    "答える際は日本語で答えるようにしてください。\n"
    "質問: {query_str}\n"
    "回答: "
)
        summary_template=PromptTemplate(
            template = DEFAULT_TREE_SUMMARIZE_TMPL,
            prompt_type=PromptType.SUMMARY
        )
        summarizer = TreeSummarize(llm=llm, streaming=True, use_async=True,summary_template=summary_template)
        router_query_engine = RouterQueryEngine.from_defaults(
            selector=LLMMultiSelector.from_defaults(llm = llm,max_outputs=4),
            query_engine_tools=self.query_engine_tools,
            summarizer=summarizer,
            verbose=True, 
            )
        
        return router_query_engine
    '''
    async def query_engine(self, query_bundle: QueryBundle):
        # 適切なプロンプトテンプレート文字列を設定
        prompt_template_str = """
"""

        # 適切なOutputParserを設定
        output_parser = SelectionOutputParser()

        # プロンプトのインスタンスを作成
        prompt = PromptTemplate(
            template=prompt_template_str,
            output_parser=output_parser,
            prompt_type=PromptType.MULTI_SELECT,
        )

        # LLMのインスタンスを作成
    
        llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo", api_key=openai_api_key)
        max_outputs = 10

        # LLMMultiSelectorのインスタンスを作成
        selector = LLMMultiSelector(
            llm=llm,
            prompt=prompt,
            #max_outputs=max_outputs
        )

        # 非同期メソッドをawaitで呼び出し
        choices = [x.metadata for x in self.query_engine_tools]
        selected_results = await selector._aselect(
            choices=choices, 
            query=query_bundle
            )

        # RouterQueryEngineのインスタンスを作成
        router_query_engine = RouterQueryEngine.from_defaults(
            selector=selected_results,
            query_engine_tools=self.query_engine_tools,
            verbose=True,
            # service_context=self.service_context
        )

        return router_query_engine'''