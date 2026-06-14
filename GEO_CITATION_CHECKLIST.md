# 欣晨工業 — AI 引用與外部曝光檢核清單
## 提升 Gemini / ChatGPT / Claude / Perplexity 等 AI 助理的引用與搜尋曝光

---

## 為什麼這份清單重要？

AI 助理在回答「桃園自動化設備廠商」「工業加熱器製造商」「機械手臂整合廠商」等問題時，主要依據兩類資料來源：

1. **網站本身的結構化資料**（已完成）— robots.txt 開放 AI 爬蟲、llms.txt / llms-full.txt、JSON-LD（Organization、Product、Service、FAQPage、Speakable）、hreflang 多語言版本等。
2. **第三方權威平台**上對公司名稱、地址、電話（NAP）、業務描述的一致記載 — 這是 AI 模型訓練資料與即時檢索（Perplexity、Gemini 的 Google 搜尋整合、ChatGPT 的 Bing 搜尋整合）的重要依據。

本清單列出需要**手動**註冊或更新的外部平台，依優先順序排列。這些動作需要公司帳號/聯絡資訊，agent 無法代為操作，請依序完成。完成後告知我，我可協助將新取得的連結加入網站的 `sameAs` 結構化資料中，進一步強化 AI 對「欣晨工業」這個實體的辨識。

---

## 公司基本資料（NAP，請所有平台保持完全一致）

| 項目 | 內容 |
|---|---|
| 公司名稱（中） | 欣晨工業有限公司 |
| 公司名稱（英） | Hsin-Chan Industrial Co., Ltd. |
| 地址 | 33841 台灣桃園市大園區中正東路三段490號 |
| 地址（英） | No. 490, Sec. 3, Zhongzheng E. Rd., Dayuan District, Taoyuan City 33841, Taiwan |
| 電話 | +886-3-381-4497（03-381-4497） |
| 傳真 | 03-381-4536 |
| Email | hc3814497@gmail.com |
| 網站 | https://www.hsinchan.com |
| 成立年 | 1996年（30年以上製造經驗） |
| 營業時間 | 週一至週五 08:00–17:30 |
| 一句話介紹 | 欣晨工業有限公司 — 以豐田生產哲學（TPS）為核心的精密自動化設備製造商，提供加熱器、熱電偶、一體式料管等高溫工業耗材，以及機械手臂整合、AOI視覺檢測、數位雙生等自動化服務。 |
| Facebook | https://www.facebook.com/people/%E6%AC%A3%E6%99%A8%E5%B7%A5%E6%A5%AD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8/100069099361989/ |
| YouTube | @欣晨工業有限公司 |

> ⚠️ 各平台填寫的公司名稱、地址、電話務必逐字一致（含全半角符號、路名寫法）。NAP 資訊不一致會降低 Google / Bing 對商家資料的信任度，間接影響 AI 引用時的準確度。

---

## 優先順序 1：搜尋引擎商家檔案（最高優先）

### ☐ Google 商家檔案 (Google Business Profile)
- 註冊網址：https://business.google.com
- 重要性：Gemini 與 Google AI Overview 直接讀取 GBP 資料；也影響 Google 地圖與本地搜尋結果
- 填寫重點：
  - 主類別建議：「Industrial Equipment Supplier」或對應「自動化設備製造商」
  - 完整地址、電話、營業時間（同上表）
  - 網站連結 → https://www.hsinchan.com
  - 上傳廠房、產品、團隊照片（可用 `photo/` 資料夾現有素材，如 `ST01.png`、`Robot夾具.jpg`）
  - 服務項目可填：機械手臂整合、AOI視覺檢測、數位雙生、加熱器/熱電偶客製
  - 完成電話或明信片驗證

### ☐ Bing Places for Business
- 註冊網址：https://www.bingplaces.com
- 重要性：Bing 是 ChatGPT（Bing 搜尋整合）與 Microsoft Copilot 的主要資料來源之一
- 填寫重點：可直接從 Google 商家檔案匯入資料，加快流程

---

## 優先順序 2：產業 B2B 平台（國際曝光）

### ☐ Taiwantrade（台灣經貿網）
- 網址：https://www.taiwantrade.com
- 重要性：台灣官方外貿平台，內容常被收錄於各類語料中；適合「Taiwan heater manufacturer」「Taiwan automation equipment」等英文查詢

### ☐ ThomasNet
- 網址：https://www.thomasnet.com
- 重要性：北美最大工業供應商目錄，提升英文/北美市場曝光

### ☐ EC21 / Alibaba 企業檔案
- 網址：https://www.ec21.com 、 https://www.alibaba.com
- 重要性：覆蓋全球採購商搜尋習慣，補強多語言（中/英/日）曝光，與官網的三語版本相呼應

---

## 優先順序 3：專業社群與知識圖譜

### ☐ LinkedIn 公司頁面
- 建立網址：https://www.linkedin.com/company/setup/new/
- 重要性：LinkedIn 企業頁面內容常被各大 LLM 收錄；可同步分享 technology.html 的技術文章、產品更新

### ☐ Wikidata 條目
- 網址：https://www.wikidata.org
- 重要性：Wikidata 是多數 LLM 知識圖譜的核心資料來源之一。建立公司條目（Q-item）並連結官網、Facebook、YouTube、地址等，有助 AI 將「欣晨工業」與正確實體資訊綁定

---

## 優先順序 4：技術驗證（確認結構化資料正確被讀取）

### ☐ Google Search Console
- 網址：https://search.google.com/search-console
- 動作：
  1. 加入並驗證 https://www.hsinchan.com
  2. 提交 sitemap：`https://www.hsinchan.com/sitemap.xml`
  3. 用「網址檢查」工具確認首頁 FAQPage / Organization 結構化資料被正確解析（無錯誤或警告）

### ☐ Rich Results Test
- 網址：https://search.google.com/test/rich-results
- 動作：貼上 https://www.hsinchan.com，確認 FAQPage（13 題）、Organization、Speakable 等 JSON-LD 全部通過驗證

### ☐ Bing Webmaster Tools
- 網址：https://www.bing.com/webmasters
- 動作：加入網站、提交 sitemap.xml；可啟用 IndexNow 即時通知 Bing 內容更新，加快 ChatGPT/Copilot 取得最新資料

---

## 完成後請回報

完成上述項目後，請告知我：
1. 是否取得新的外部連結（LinkedIn 公司頁、Wikidata 條目網址等）
2. 是否需要將新連結加入網站 JSON-LD 的 `sameAs` 欄位（目前 index.html 的 Organization schema 已包含 Facebook 與 YouTube，可一併補上其他平台連結，進一步強化 AI 對「欣晨工業」實體的辨識）

---

*本文件由 Claude Code 生成 — 欣晨工業有限公司*
