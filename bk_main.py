from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import wikipediaapi
from dotenv import load_dotenv
import os
from transformers import pipeline
from googletrans import Translator
from rake_nltk import Rake


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

def translate_summary(summary):
    translator = Translator()
    translated_summary = translator.translate(summary, dest='en').text
    return translated_summary

def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()

# /motivateエンドポイントにPOSTリクエストが来たときの処理
@app.post("/summarize")
async def summarize(query: Query):
    summary, url = get_wikipedia_summary(query.query)
    if summary:
        translated_summary = translate_summary(summary)
        keywords = extract_keywords(translated_summary)
        return {
            "summary": summary,
            "translated_summary": translated_summary,
            "keywords": keywords,
            "url": url
        }
    else:
        raise HTTPException(status_code=404, detail="記事が見つかりません")

def get_wikipedia_summary(query, max_length=500):
    wiki_wiki = wikipediaapi.Wikipedia(language='ja')
    page = wiki_wiki.page(query)
    if page.exists():
        summary = page.summary
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        return summary, page.fullurl
    else:
        return "指定された記事は存在しません。", None