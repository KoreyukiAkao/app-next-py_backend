# CORS（Cross-Origin Resource Sharing）について:
# CORSは、異なるオリジン（ドメイン、プロトコル、ポート）間でのリソース共有を許可する仕組みです。
# 通常、ブラウザはセキュリティのために異なるオリジン間のリクエストを制限します。
# CORSを設定することで、特定のオリジンからのリクエストを許可し、データ共有を可能にします。

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import wikipediaapi
from dotenv import load_dotenv
import os

load_dotenv()

# FastAPIのアプリケーションを作成
app = FastAPI()

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

# /motivateエンドポイントにPOSTリクエストが来たときの処理
@app.post("/summarize")
async def summarize(query: Query):
    # print(f"Received query: {query.query}")
    summary = get_wikipedia_summary(query.query)
    # print(f"Received query: {summary}")
    if summary:
        return {"summary": summary}
    else:
        raise HTTPException(status_code=404, detail="記事が見つかりません")

def get_wikipedia_summary(query, max_length=500):
    # ユーザーエージェントを指定してWikipediaインスタンスを作成
    wiki_wiki = wikipediaapi.Wikipedia(
        language='ja',
        user_agent='app-next-py/1.0 (https://app-next-py-lif4.vercel.app/; koreyuki1007@gmail.com)'
    )
    page = wiki_wiki.page(query)

    if page.exists():
        summary = page.summary
        # 要約の長さを調整
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
            print(summary)
        return summary
    else:
        return "指定された記事は存在しません。"