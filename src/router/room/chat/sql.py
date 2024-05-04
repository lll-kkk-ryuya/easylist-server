
import os
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
# .env ファイルを読み込む
load_dotenv()
# 環境変数 'OPENAI_API_KEY' を取得
import openai

openai.api_key =os.getenv('OPENAI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import insert
from llama_index.core import BasePromptTemplate, PromptTemplate
from llama_index.core.prompts import PromptType

from llama_index.core.indices.struct_store.sql_query import NLSQLTableQueryEngine,NLStructStoreQueryEngine,PGVectorSQLQueryEngine
from llama_index.core.indices import SQLStructStoreIndex
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, StorageContext, SQLDatabase

from sqlalchemy.exc import NoSuchTableError 

# データベースエンジンとメタデータオブジェクトの定義
#engine = create_engine('sqlite:///example.db', echo=True)
#metadata_obj = MetaData(engine)



class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()

    def create_table(self, table_name):
        try:
            old_table = Table(table_name, self.metadata, autoload_with=self.engine)
            old_table.drop(self.engine)
        except NoSuchTableError:
            print(f"テーブル '{table_name}' は存在しません。新規作成します。")

        new_table = Table(
            table_name,
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("campusName", String(32)),
            Column("academicFieldName", String(64)),
            Column("season", String(32)),
            Column("subjectName", String(64)),
            Column("dayOfWeekPeriod", String(32)),
            Column("locationName", String(32)),
            Column("lessonModeName", String(32)),
            Column("timetableYear", String(32)),
            Column("faculties", String(64)),
            Column("entryNumber", String(32)),
            Column("syllabusDetailUrl", String(64)),
            extend_existing=True
        )

        self.metadata.create_all(self.engine)
        self.metadata.reflect(bind=self.engine)
        return new_table

    def insert_data(self, table_name, df):
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        rows = df.to_dict(orient='records')
        with self.engine.begin() as connection:
            for row in rows:
                stmt = insert(table).values(**row)
                connection.execute(stmt)


class NLSQLQueryEngineManager:
    def __init__(self, engine):
        self.engine = engine
        self.query_engines = {}

    def create_nlsql_query_engine(self, table_name):
        engine = create_engine('sqlite:///example.db', echo=True)
        llm = OpenAI(temperature=0, model="gpt-4",api_key=openai_api_key)
        service_context = ServiceContext.from_defaults(llm=llm)
        # Initialize SQLDatabase and NLSQLTableQueryEngine
        sql_database = SQLDatabase(engine, include_tables=[table_name])
        template =(
        "Given an input question, it is crucial to dissect the question to identify the principal keywords related to the 'subjectName' in our database. When extracting the 'subjectName', ensure to utilize actual course names from the database. If the course name includes alphanumeric characters, you are required to convert these numbers into Roman numerals (e.g., '1' to 'Ⅰ''2' to 'Ⅱ''3' to 'Ⅲ''4' to 'Ⅳ''5' to 'Ⅴ''6' to 'Ⅵ''7' to 'Ⅶ''8' to 'Ⅷ''9' to 'Ⅸ') for the search to align accurately with the database's formatting conventions. It's imperative to deconstruct the course's name into the maximum possible relevant keywords. These keywords will be used as the foundation for constructing a syntactically correct {dialect} SQL query. This meticulous approach guarantees a comprehensive search, effectively capturing the diverse cataloging of courses.\n"

"When constructing your SQL query for the 'subjectName' column, it is mandatory to dissect the course name into at least two distinct keywords and then ingeniously integrate these keywords into your query using logical operators no less than twice. This method significantly enhances the accuracy of aligning the search with the specific course details within the database. Here’s how to proceed:\n"

"Keyword Identification: Carefully analyze the input question to extract every conceivable keyword associated with the course name in question. Use actual course names from the database as reference points. For instance, if the inquiry pertains to 'French Cultural Studies', the essential keywords would be 'French' and 'Cultural Studies'.\n"

"Mandatory Query Structuring: With the identified keywords, formulate your SQL query. You must use the 'LIKE' clause with the '%' wildcard for partial matches on the 'subjectName' column. It's critical to incorporate the extracted keywords using 'OR' or 'AND' logical operators, ensuring you apply these operators at least twice within your query construction. For example:\n"

"SQLQuery: SELECT * FROM table_name WHERE subjectName LIKE '%French%' AND subjectName LIKE '%Cultural Studies%';\n"
"Analyzing and Ordering Results: After executing the query, analyze the results to identify the most pertinent information. You are encouraged to order the results by columns of significance, such as 'dayOfWeekPeriod' or 'timetableYear', to showcase the most relevant examples from the database.\n"

"Remember, your query must:\n"

"Avoid querying all columns from a specific table; target only a select few columns relevant to the question.\n"
"Use only the column names visible in the provided schema description, avoiding queries on non-existent columns.\n"
"Clarify column names by prefixing them with the table name when ambiguity is present.\n"
"For achieving partial matches, the LIKE clause with '%' wildcard becomes your tool of choice. Should the search term within the LIKE clause include numerical values, convert them to Roman numerals with the roman_str function to ensure alignment with the database's formatting conventions.\n"
"Each stage of your query process should conform to the following format:\n"

"Question: The original question posed.\n"
"SQLQuery: The carefully crafted SQL query following the guidelines above.\n"
"SQLResult: The outcome derived from executing the SQLQuery.\n"
"Answer: The conclusive answer distilled from the SQLResult, structured as directed.\n"
"Your queries should exclusively tap into tables and their corresponding columns as delineated in the schema provided.\n"




"{schema}\n\n"
"Column Descriptions:\n"
"id: レコードの識別子。降順で並べられます。\n"
"campusName: 授業が開催されるキャンパス名 (例: 日吉、三田キャンパス)。\n"
"subjectName: 授業名。通常の授業に関する質問に使用します。必修科目など特定の状況を除き、こちらのカラムを優先的に使用してください。\n"
"academicFieldName: 総合教育科目や人文科学科目などの必修科目に関する質問に対して使用します\n"
"season: 授業が開催される学期 (春学期、秋学期、通年)。\n"
"dayOfWeekPeriod: 授業が開催される曜日と時間割。例: 月1(月曜1限）,金３(金曜日3限)このように曜日と何限かが入っている\n"
"locationName: 授業を担当する教授の名前。\n"
"lessonModeName: 授業の形式（対面授業かオンライン授業か）。\n"
"timetableYear: 授業が開催される年（西暦）。\n"
"faculties: 履修可能な学部（例: 商 - 商学部、経 - 経済学部、文 - 文学部、理 - 理工学部、法/政治 - 法学部政治学科、法/法律 - 法学部法律学科）。\n"
"entryNumber: 授業のID。\n"
"syllabusDetailUrl: 授業のシラバスのURL。\n\n"
"Question: {query_str}\n"
"SQLQuery: "
              )
        text_to_sql_prompt = PromptTemplate(
            #"SELECT * FROM {table_name} WHERE {column_name} LIKE '{query_str}';"
            template = template,
            prompt_type = PromptType.TEXT_TO_SQL,)
        #function_mappings={"roman_str": format_query_with_roman_numerals}
        
    #text_to_sql_prompt =text_to_sql_prompt.format(table_name=table_name)
        table_query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
            text_to_sql_prompt=text_to_sql_prompt,
            tables=[table_name],
            service_context=service_context,
        )

        # 作成したクエリーエンジンを返す
        return table_query_engine

    def process_files_to_query_engines(self, file_paths, template):
        for file_path in file_paths:
            table_name = os.path.splitext(os.path.basename(file_path))[0]
            table_query_engine = self.create_nlsql_query_engine(table_name, template)
            self.query_engines[table_name] = table_query_engine

# 使用例
# engine = create_engine('sqlite:///your_database.db')
# llm = "ここにLLMの設定"  # LLMのインスタンスまたは設定を指定
# nlsql_manager = NLSQLQueryEngineManager(engine, llm)

# NLSQLクエリーエンジンの管理に使用するテンプレート
#
# template = "ここにSQLクエリ生成に使用するテンプレートを指定"
# file_paths = ['path/to/your/file.csv']
# nlsql_manager.create_nlsql_query_engine(file_paths, template)
