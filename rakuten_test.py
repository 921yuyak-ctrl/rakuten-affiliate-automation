#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"


def load_env(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        raise RuntimeError(".env が見つかりません。楽天の3つの値を .env に設定してください。")

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} が .env に設定されていません。")
    return value


def main() -> int:
    try:
        load_env()
        app_id = require_env("RAKUTEN_APP_ID")
        access_key = require_env("RAKUTEN_ACCESS_KEY")
        affiliate_id = require_env("RAKUTEN_AFFILIATE_ID")

        params = {
            "applicationId": app_id,
            "affiliateId": affiliate_id,
            "keyword": "ゴルフ",
            "hits": "5",
            "format": "json",
            "formatVersion": "2",
            "elements": "itemName,itemPrice,reviewAverage,reviewCount,shopName,affiliateUrl",
        }
        url = ENDPOINT + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            url,
            headers={
                "accessKey": access_key,
                "User-Agent": "rakuten-affiliate-automation/1.0",
            },
            method="GET",
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        items = data.get("items", [])
        if not items:
            print("商品が取得できませんでした。")
            return 1

        print(f"楽天API接続成功: {len(items)}件取得\n")
        for i, item in enumerate(items, start=1):
            print(f"[{i}] {item.get('itemName', '')}")
            print(f"価格: {item.get('itemPrice', '')}円")
            print(f"レビュー平均: {item.get('reviewAverage', '')}")
            print(f"レビュー件数: {item.get('reviewCount', '')}")
            print(f"ショップ: {item.get('shopName', '')}")
            print(f"アフィリエイトURL: {item.get('affiliateUrl', '')}")
            print()

        return 0

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            message = parsed.get("error_description") or parsed.get("error") or body
        except json.JSONDecodeError:
            message = body[:500]
        print(f"楽天APIエラー HTTP {exc.code}: {message}")
        return 1
    except urllib.error.URLError as exc:
        print(f"通信エラー: {exc.reason}")
        return 1
    except Exception as exc:
        print(f"エラー: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
