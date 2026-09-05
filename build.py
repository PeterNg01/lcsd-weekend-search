#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載康文署 SmartPLAY 康體活動開放數據，壓縮成靜態檔案供 GitHub Pages 使用。
只保留網頁需要的欄位，並輸出 gzip（供瀏覽器解壓）+ 純 JSON（後備）+ meta.json。

用法（本地預覽或 GitHub Actions）：
    python3 build.py
"""
import gzip
import json
import os
import time
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_URL = "https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/activity-prog/file"
OUT_DIR = os.path.join(BASE, "data")
UA = "Mozilla/5.0 (compatible; lcsd-weekend-search/1.0)"

# 網頁實際用到的欄位（保留原始欄位名稱，避免前端改動）
KEEP = [
    "ACTIVITY_NO", "TC_PGM_NAME", "EN_PGM_NAME", "TC_ACT_TYPE_NAME", "TC_DISTRICT",
    "PGM_START_DATE", "PGM_END_DATE", "TC_DAY", "EN_DAY", "PGM_START_TIME", "PGM_END_TIME",
    "TC_VENUE", "EN_VENUE", "TC_TARGET_GRP", "MIN_AGE", "MAX_AGE", "FEE",
    "QUOTA", "PLACES_LEFT", "ENROL_METHOD", "TC_NOTES", "TC_URL",
]


def main():
    print("[build] 下載最新資料…")
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read()
    except Exception as e:
        print("[build] 下載失敗，保留現有資料，略過更新：", e)
        return 0  # 失敗時不覆蓋既有資料（Actions 中會因無變更而略過 commit）

    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as e:
        print("[build] 解析失敗：", e)
        return 0
    if not isinstance(data, list):
        print("[build] 回傳格式異常（非 list），略過更新")
        return 0

    compact = [{k: rec.get(k) for k in KEEP} for rec in data]
    text = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "activities.json"), "w", encoding="utf-8") as f:
        f.write(text)
    gz = gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0)
    with open(os.path.join(OUT_DIR, "activities.json.gz"), "wb") as f:
        f.write(gz)

    meta = {
        "count": len(compact),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "source": "live",
        "url": DATA_URL,
    }
    with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[build] 完成：{len(compact)} 項活動")
    print(f"[build] activities.json = {len(text)} bytes, activities.json.gz = {len(gz)} bytes")


if __name__ == "__main__":
    raise SystemExit(main())
