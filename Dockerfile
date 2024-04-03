FROM python:3.9.7-slim

# 不要なファイルリストを削除
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 慣例に従った作業ディレクトリを設定
WORKDIR /app

# 現在のディレクトリ内のすべてのファイルとディレクトリをコピー
COPY . .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn==0.15.0

# コンテナ起動時に実行するコマンドを指定
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT"]




