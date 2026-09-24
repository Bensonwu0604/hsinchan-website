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
| 地址 | 33755 台灣桃園市大園區中正東路三段490號 |
| 地址（英） | No. 490, Sec. 3, Zhongzheng E. Rd., Dayuan District, Taoyuan City 33755, Taiwan |
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

## 現況總覽（2026-09-24 更新）

| # | 項目 | 狀態 | 誰來做 |
|---|------|------|--------|
| 1 | Google 商家檔案 — 註冊、連結網站 | ☑ 已完成 | — |
| 2 | Google 商家檔案 — 說明/開幕日期/類別/照片 | ☐ **未完成** | 你 |
| 3 | Bing Places for Business | ☐ **未完成** | 你 |
| 4 | Wikidata 條目 | ☐ **未完成** | 你 |
| 5 | LinkedIn 公司頁面 | ☐ **未完成** | 你 |
| 6 | Google Search Console | ☑ 已完成（已驗證、sitemap 已提交、有成效數據） | — |
| 7 | Rich Results Test | 🔶 部分完成，見下方說明 | 你（重測）+ 我（已修3個錯誤） |
| 8 | Bing Webmaster Tools 帳號 | ☐ **未完成**（但 IndexNow 已頂替部分功能） | 你 |
| 9 | Taiwantrade | ☐ **未完成** | 你 |
| 10 | ThomasNet | ☐ **未完成** | 你 |
| 11 | EC21 / Alibaba | ☐ **未完成** | 你 |

---

## 優先順序 1（先做這兩個，效益最高、最省時間）

### ☐ Google 商家檔案補完資料
帳號已經在，只是內容沒填滿：
- 「說明」欄目前只有約40字關鍵字列表，離750字上限還很遠——之前對話裡已經給過完整草稿，可直接貼上
- 「開幕日期」空白，填 1996 年
- 「業務類別」目前只有「機械製造商」一個，建議加「工業設備供應商」等相關類別
- 上傳廠房/產品/團隊照片（`photo/` 資料夾裡有現成的 WebP 素材）

### ☐ Bing Places for Business
- 網址：https://www.bingplaces.com
- 可直接從已有的 Google 商家檔案匯入資料，幾分鐘就能完成
- 重要性：Bing 是 ChatGPT 的 Bing 搜尋整合、Microsoft Copilot 的主要資料來源

---

## 優先順序 2（知識圖譜，中期投入）

### ☑ Wikidata 條目 — 已建立（2026-09-24）
- 條目：https://www.wikidata.org/wiki/Q141546907
- 已加入首頁 Organization JSON-LD 的 `sameAs`
- 屬性已正確填寫：instance of / country / inception / coordinates / phone / website / Facebook ID
- ⚠️ 待辦：Label（名稱）目前空白，顯示「No label defined」，需要你回去補上中/英/日三語標籤，否則條目等於沒有名字

### ☐ LinkedIn 公司頁面
- 建立網址：https://www.linkedin.com/company/setup/new/
- 常被各大 LLM 收錄，可同步分享 technology.html 的技術文章

---

## 優先順序 3：技術驗證回頭確認

### ☑ Google Search Console — 已完成
帳號已驗證、sitemap 已提交且讀取成功（13個網頁），之前對話中已一起看過「成效」報表數據（「欣晨工業有限公司」平均排序 1.6）。**現在可以做的**：用「網址檢查」工具重新檢查 products.html / services.html，確認這幾輪新加的 Speakable、Product category、hreflang 都正確被 Google 解析。

### 🔶 Rich Results Test — 部分完成
你先前測出首頁 3 個 Product 錯誤，我已修好並部署。**建議動作**：
1. 重新測 `https://www.hsinchan.com/` 確認錯誤已消失
2. 若想測 `products.html` 或個別產品頁，會看到同類型「必須指定 offers/review/aggregateRating」的警告——這是刻意保留的（見對話紀錄說明：客製報價制沒有固定價格，不會為了消除警告捏造價格或評論），不影響一般收錄與 AI 引用，只影響是否顯示 Google 特定的商品卡片視覺效果

### ☐ Bing Webmaster Tools 帳號
- 網址：https://www.bing.com/webmasters
- ☑ IndexNow 金鑰已設定並已主動推播多個網址（`https://www.hsinchan.com/7e19d612360c86de1ba45b3cd77a568c.txt`），這解決了「即時通知重新索引」的核心需求
- 但要看 Bing 的完整分析報表、手動排查索引問題，還是需要註冊帳號

---

## 優先順序 4（國際 B2B 曝光，效益中等、需要較多時間填資料）

### ☐ Taiwantrade（台灣經貿網）
- 網址：https://www.taiwantrade.com
- 適合「Taiwan heater manufacturer」等英文查詢

### ☐ ThomasNet
- 網址：https://www.thomasnet.com
- 北美最大工業供應商目錄

### ☐ EC21 / Alibaba 企業檔案
- 網址：https://www.ec21.com 、 https://www.alibaba.com
- 覆蓋全球採購商搜尋習慣，與官網三語版本相呼應

---

## 完成後請回報

完成上述項目後，請告知我：
1. 是否取得新的外部連結（LinkedIn 公司頁、Wikidata 條目網址等）
2. 需不需要把新連結加入網站 JSON-LD 的 `sameAs` 欄位（目前已包含 Facebook、YouTube、Google Maps）

---

*本文件由 Claude Code 生成 — 欣晨工業有限公司*
