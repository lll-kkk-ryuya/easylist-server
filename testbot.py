# 使用例
from router.room.chat.mainbot import QueryService
async def main():
    vector_store_path = "chroma_db"
    db_url = 'sqlite:///example.db'
    collection_names = ["bunn_senn4", "keizai5", "hougakubu5", "shougakub1", "rikougakubu1"]
    table_name = "all_curce"
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
    
    query_service = QueryService(vector_store_path, db_url,collection_names,table_name,tool_metadata)
    await query_service.setup_engines()
    query_engine = await query_service.query_engine()
    query_text = "文学部の一年生の必修語学科目について教えてください。"
    result = query_engine.query(query_text)
    print(type(result))
    result=result.response
    print(type(result))

# 非同期の main 関数を実行
import asyncio
if __name__ == "__main__":
    asyncio.run(main())