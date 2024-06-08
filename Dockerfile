FROM python:3.9.7-slim

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    rm -rf /var/lib/apt/lists/*

# SQLiteの最新版をダウンロードしてビルド
RUN wget https://www.sqlite.org/2024/sqlite-autoconf-3450200.tar.gz && \
    tar xvfz sqlite-autoconf-3450200.tar.gz && \
    cd sqlite-autoconf-3450200 && \
    ./configure --prefix=/usr/local && \
    make && make install

# 環境変数LD_LIBRARY_PATHに/usr/local/libを追加
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# SQLiteのバージョンを確認
RUN sqlite3 --version

# 慣例に従った作業ディレクトリを設定
WORKDIR /app

# 現在のディレクトリ内のすべてのファイルとディレクトリをコピー
COPY . .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "uvicorn[standard]>=0.18.3"

# コンテナ起動時に実行するコマンドを指定
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level debug --loop asyncio"
