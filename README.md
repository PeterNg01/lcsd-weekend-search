# 康文署康體活動搜尋（週末・平日晚間）— GitHub Pages 版

純靜態網頁，可直接部署到 **GitHub Pages**。只顯示**星期六／日**及**平日晚間**的康樂體育活動，並可自選篩選範圍。

資料來源：康樂及文化事務署「社區康樂體育活動」開放數據（SmartPLAY）。

## 為什麼是「快照」而非即時資料？

康文署的開放數據端點沒有開放跨域（CORS），瀏覽器無法直接讀取，而 data.gov.hk 的 filter API 也不接受該資源。因此本版把最新資料**壓縮成靜態檔**（`data/activities.json.gz`，僅約 776 KB），由 GitHub Actions 每日自動下載更新，再推送到 Pages。

## 快速部署到 GitHub Pages

1. 在 GitHub 新建一個 repository，把本資料夾內容推上去：

   ```bash
   cd smartplay-pages
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/<你的帳號>/<repo>.git
   git push -u origin main
   ```

2. 開啟 repository 的 **Settings → Pages**：
   - **Source** 選 `Deploy from a branch`
   - **Branch** 選 `main`，資料夾選 `/ (root)`，按 **Save**

3. 約 1 分鐘後，網站會出現在 `https://<你的帳號>.github.io/<repo>/`。

### 每日自動更新（GitHub Actions）

`.github/workflows/refresh-data.yml` 已設定**每天 10:20（香港時間）**自動執行：
下載最新資料 → 重新產生 `data/` 檔 → 提交回 `main` → Pages 自動重新發布。

- 手動立即更新：repository 的 **Actions → Refresh activity data → Run workflow**。
- 若 Actions 無法自動推送（例如 repository 開啟了分支保護），可改為本機執行：

  ```bash
  python3 build.py        # 產生 data/activities.json(.gz) 與 meta.json
  git add data && git commit -m "refresh" && git push
  ```

## 本機預覽

直接執行 `python3 build.py` 產生資料後，用任意靜態伺服器開啟即可：

```bash
cd smartplay-pages
python3 build.py
python3 -m http.server 8000     # 開啟 http://127.0.0.1:8000/
```

> 直接雙擊開啟 `index.html` 也可運作（本版為同源讀取 `data/`，無跨域問題），
> 但部分瀏覽器對 `file://` 讀取 `.json.gz` 會有限制，建議用上述 http.server 預覽。

## 功能

- **顯示模式**：星期六／日、平日晚間（一至五），可各自勾選；「晚上由…起」可調（17:00–20:00）；兩項皆取消即顯示全部
- **地區**（18 區＋其他場地，多選）、**活動類別**、**對象**、**日期範圍**、**關鍵字**
- **只顯示尚有名額**、**只顯示免費**
- 每張卡片標示「週末／平日晚間」、尚餘名額、費用、報名方式，並附 SmartPLAY 詳情連結

## 檔案結構

```
smartplay-pages/
├── index.html                       # 搜尋網頁（單一檔案，內嵌 CSS/JS）
├── build.py                         # 下載＋壓縮資料（本機或 Actions 執行）
├── README.md
├── .github/workflows/refresh-data.yml  # 每日自動更新
└── data/
    ├── activities.json.gz           # gzip 快照（網頁優先載入，約 776 KB）
    ├── activities.json              # 純 JSON 後備（供不支援解壓的舊瀏覽器）
    └── meta.json                    # 資料筆數與更新時間
```

## 注意事項

- 本工具為獨立製作，**非康文署官方網站**；實際報名仍須經 SmartPLAY。
- 「尚餘名額」以官方資料為準。
- 「平日晚間」以活動**開始時間**≥指定時間作判斷；橫跨日間的比賽／日營不會歸類為晚間活動。
