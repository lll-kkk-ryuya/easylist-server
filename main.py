from fastapi import FastAPI
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/")
async def read_root():
    users = await supabase.table('User').select("*").execute()
    print("hello")
    return {"message": "Hello World From Fast API"}