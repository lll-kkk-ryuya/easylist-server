import os
from dotenv import load_dotenv
# .env ファイルを読み込む
load_dotenv()
# 環境変数 'OPENAI_API_KEY' を取得
openai_api_key = os.getenv('OPENAI_API_KEY')
print(openai_api_key)