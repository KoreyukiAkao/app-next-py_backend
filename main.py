from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import wikipediaapi
from dotenv import load_dotenv
import os
import requests


load_dotenv()

# FastAPIのアプリケーションを作成
app = FastAPI()

# HEADリクエスト用エンドポイント: UptimeRobotや監視ツール向けに対応
@app.head("/summarize")
async def summarize_head():
    return {"message": "HEAD request successful"}

# 環境変数からフロントエンドのURLを取得
frontend_url = os.getenv("PY_PUBLIC_FRONTEND_URL") 
print(frontend_url)
# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # フロントエンドのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

class Theme(BaseModel):
    theme: str

class Query(BaseModel):
    query: str

# ルートURLにアクセスしたときの処理
@app.get("/")
async def read_root():
    # "Hello": "World"というメッセージを返す
    return {"Hello": "World"}

def get_wikipedia_summary(query, max_length=150):
    wiki_wiki = wikipediaapi.Wikipedia(language='ja', user_agent='YourAppName/1.0 (your-email@example.com)')
    page = wiki_wiki.page(query)
    if page.exists():
        summary = page.summary
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        return summary, page.fullurl
    else:
        return "指定された記事は存在しません。", None

def translate_with_deepl(text, target_lang='EN'):
    api_key = os.getenv('DEEPL_API_KEY')  # 環境変数からAPIキーを取得
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        'auth_key': api_key,
        'text': text,
        'target_lang': target_lang
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.json()['translations'][0]['text']
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()

# /motivateエンドポイントにPOSTリクエストが来たときの処理
@app.post("/summarize")
async def summarize(query: Query):
    summary, url = get_wikipedia_summary(query.query)
    if summary:
        translated_summary = translate_with_deepl(summary)
        return {
            "summary": summary,
            "translated_summary": translated_summary,
            "url": url
        }
    else:
        raise HTTPException(status_code=404, detail="記事が見つかりません")