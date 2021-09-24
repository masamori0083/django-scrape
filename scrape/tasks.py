# celoryが担当する処理

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from .models import Request
from celery import shared_task


def get_yahooauction(url):
  # スクレイピングの実行コード
    res = requests.get(url)
    soup = bs(res.content, "html.parser")
    items = soup.findAll("li", class_="Product")
    return[
        {
            "title": item.find("a", class_="Product__titleLink").text.strip(),
            "url": item.find("a", class_="Product__titleLink").get("href"),
            "picture": item.find("img").get("src")
        }
        for item in items
    ]


@shared_task
def start_task(_uuid):
    gcs_bucket = "gs://scraping_django0083"
    obj = Request.objects.get(uuid=_uuid)
    # 受け取ったurlからデータをスクレイピング
    # htmlに描画
    result = get_yahooauction(obj.url)
    # データフレームに変換
    # pklファイルとして保存
    df = pd.DataFrame(result)
    filename = f"{gcs_bucket}/{_uuid}.pkl"
    # データ保存
    df.to_pickle(filename)

    return True
