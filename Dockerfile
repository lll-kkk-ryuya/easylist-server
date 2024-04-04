FROM python:3.9.7-slim

# 不要なファイルリストを削除
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# SQLite3の最新版をソースからビルドしてインストールするためのステップ
RUN apt-get update && apt-get install -y wget build-essential && \
    wget https://www.sqlite.org/2023/sqlite-autoconf-3390200.tar.gz && \
    tar xvfz sqlite-autoconf-3390200.tar.gz && \
    cd sqlite-autoconf-3390200 && \
    ./configure --prefix=/usr/local && \
    make && make install && \
    sqlite3 --version


# 慣例に従った作業ディレクトリを設定
WORKDIR /app

COPY . .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "uvicorn[standard]>=0.18.3"


# コンテナ起動時に実行するコマンドを指定
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT --log-level debug"]




