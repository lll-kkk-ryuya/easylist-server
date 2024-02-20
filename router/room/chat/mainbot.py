from router.room.chat.query_engines import QueryEngineManager

class QueryService:
    def __init__(self, vector_store_path: str, db_url: str, collection_names: list, table_name: str, tool_metadata: dict):
        self.vector_store_path = vector_store_path
        self.db_url = db_url
        self.collection_names = collection_names
        self.table_name = table_name
        self.tool_metadata = tool_metadata
        # QueryEngineManagerのインスタンス化は同期的に行われます
        self.qem = QueryEngineManager(self.vector_store_path, self.db_url)

    async def setup_engines(self):
        # セットアップ処理を非同期で実行する
        self.qem.setup_vector_query_engines(self.collection_names)
        self.qem.add_nlsql_query_engine(self.table_name)
        self.qem.setup_query_engine_tools(self.tool_metadata)

    async def query_engine(self):
        # クエリの実行と結果の取得を非同期で行う
        # この部分はQueryEngineManagerが非同期操作をサポートしている場合の例です
        result = self.qem.query_engine()
        return result


# 使用例
#if __name__ == "__main__":
    #vector_store_path = "chroma_db"
    #db_url = 'sqlite:///example.db'
    #collection_names = ["bunn_senn4", "keizai5", "hougakubu5", "shougakub1", "rikougakubu1"]
    #table_name = "all_curce"
    #tool_metadata = {
    #"rikougakubu1": {
        #"name": "Engineering Department",
        #"description": "Provides comprehensive data excluding course information for the Engineering Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    #},
    #"hougakubu5": {
        #"name": "Law Department",
        ##},
    #"keizai5": {
        #"name": "Economics Department",
        #"description": "Provides comprehensive data excluding course information for the Economics Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    #},
    #"bunn_senn4": {
        #"name": "Literature Department",
        #"description": "Provides comprehensive data excluding course information for the Literature Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    #},
    #"shougakub1": {
        #"name": "Commerce Department",
        #"description": "Provides comprehensive data excluding course information for the Commerce Department, such as enrollment requirements, graduation criteria, and advancement conditions."
    #},
    #"all_curce": {
        #"name": "Course Data",
        #"description": "Course data: ID, campus, name, field, term, schedule, mode, year, faculties, URL. Covers all departments and provides detailed information on each course offered."
    #}
#}
    
    #query_service = QueryService(vector_store_path, db_url, collection_names, table_name, tool_metadata)
    #query_text = "文学部の一年生の必修語学科目について教えてください。"
    #result = query_service.query(query_text)
    #print(result)
