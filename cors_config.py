# cors_config.py

from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    # 許可するオリジンのリスト
    allowed_origins = [
        "https://staging.keioeasylist.net",
        "http://localhost:3000",
        # 必要に応じて他のオリジンを追加
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["X-Custom-Header", "Authorization"],
    )