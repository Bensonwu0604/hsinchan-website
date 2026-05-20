/**
 * 欣晨工業 — 每日智慧製造 Facebook 自動發文
 * 使用 Claude API 生成文案，透過 Facebook Graph API 發文
 */

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ── 60 個智慧製造題材（2個月不重複）────────────────────────────────────────
const TOPICS = [
  // TPS / 精實製造
  { tag: 'Kaizen',       zh: '改善文化',       prompt: '今天聊Kaizen持續改善：如何讓工廠每天比昨天好一點點，從消除七大浪費到VSM價值流圖，分享一個實際的工廠改善思維與做法。' },
  { tag: 'JIT',          zh: '即時生產',       prompt: '今天聊JIT即時生產：「在正確的時間、以正確的數量交付正確的東西」—— 這個豐田哲學如何在現代工廠中被落實，拉式生產系統的核心邏輯。' },
  { tag: 'Jidoka',       zh: '自働化',         prompt: '今天聊Jidoka自働化（智慧自動化）：設備能自動偵測異常並停機的哲學，如何讓製造系統「能判斷、會停機」，從源頭阻止不良品流入下一工序。' },
  { tag: '現地現物',      zh: '現地現物',       prompt: '今天聊現地現物（Genchi Genbutsu）：豐田最核心的現場哲學 — 不信二手報告，親自到現場用眼確認、用手丈量。為什麼這個簡單原則是解決90%工廠問題的關鍵？' },
  { tag: 'Poka-yoke',    zh: '防呆設計',       prompt: '今天聊Poka-yoke防呆設計：如何用機構設計從源頭杜絕人為錯誤？從汽車裝配線到半導體製程，防呆思維讓零缺陷生產成為可能。' },
  { tag: 'SMED',         zh: '快速換模',       prompt: '今天聊SMED快速換模（Single-Minute Exchange of Die）：如何把換線時間從數小時縮短到10分鐘以內？精實製造中換線效率對整體OEE的影響。' },
  { tag: '5S',           zh: '5S職場管理',     prompt: '今天聊5S（整理/整頓/清掃/清潔/素養）：很多工廠把5S當清潔活動在做，但真正的5S是一種視覺管理系統，讓異常在30秒內被任何人一眼看穿。' },
  { tag: 'OEE',          zh: 'OEE設備效率',    prompt: '今天聊OEE（整體設備效率）：世界級工廠OEE目標是85%，而台灣中小製造業平均只有55-65%。可用率×性能效率×良品率，每個數字背後都是改善機會。' },
  { tag: '標準化',        zh: '標準作業SOP',    prompt: '今天聊SOP標準作業程序：為什麼「有SOP」和「SOP真的被執行」是兩件完全不同的事？好的SOP如何降低人員替換成本並確保品質一致性。' },
  { tag: '看板',          zh: '看板系統',       prompt: '今天聊看板（Kanban）：從豐田工廠到軟體開發再到現代製造業，看板系統如何讓生產可視化、流動順暢？物料補充的「拉式」邏輯。' },

  // 工業自動化
  { tag: '機械手臂',      zh: '工業機器人',     prompt: '今天聊工業機器人最新趨勢：2024-2025年全球工業機器人出貨量創新高，FANUC、ABB、KUKA在台灣製造業的應用現況，以及關節型機器人vs協作機器人的選型邏輯。' },
  { tag: 'Cobot',        zh: '協作機器人',     prompt: '今天聊協作機器人（Cobot）：UR、FANUC CRX、KUKA LBR — 協作機器人不是要取代工人，而是把人從危險單調的工作解放出來。ISO/TS 15066安全規範解析。' },
  { tag: '第七軸',        zh: '機器人第七軸',   prompt: '今天聊機器人第七軸線性走行軸：讓機械手臂從「定點作業」升級為「移動作業」，大幅擴展工作範圍，適合多站點製程整合的設計重點。' },
  { tag: 'PLC',          zh: 'PLC控制系統',    prompt: '今天聊PLC控制器在智慧製造中的角色：從三菱iQ-R到西門子S7-1500，現代PLC如何整合運動控制、視覺、IoT？SSCNET III/H高速伺服通訊的優勢。' },
  { tag: '伺服系統',      zh: '伺服驅動',       prompt: '今天聊高性能伺服系統：三菱MR-J5系列、YASKAWA Sigma-7的技術突破 — 更快的電流響應、AI自適應調諧，讓精密定位精度達到±0.001mm。' },
  { tag: 'AMR',          zh: '自主移動機器人',  prompt: '今天聊AMR自主移動機器人：不需要固定軌道、可動態重新規劃路徑的倉儲物流機器人，正在改變工廠物料搬運的遊戲規則。' },

  // AI & 視覺
  { tag: 'AOI',          zh: '視覺檢測AOI',    prompt: '今天聊AOI自動光學檢測：工業相機+深度學習如何達到人眼看不到的缺陷偵測精度？從半導體到電子封裝，AOI系統如何取代人工目視品檢，讓良率突破天花板。' },
  { tag: '機器視覺',      zh: '機器視覺應用',   prompt: '今天聊機器視覺的五大應用：瑕疵偵測、尺寸量測（±0.01mm精度）、QR/Barcode辨識、OCR字元讀取、機器人視覺引導定位 — 每個場景的相機選型與打光技術。' },
  { tag: '深度學習AOI',   zh: 'AI瑕疵分類',    prompt: '今天聊深度學習在AOI的突破：傳統AOI用規則演算法，容易因光線變化誤判。CNN深度學習模型如何讓瑕疵分類準確率從90%提升到99.5%以上？' },
  { tag: '工業AI',        zh: '工業人工智慧',   prompt: '今天聊工業AI（Industrial AI）的實際落地：不是所有工廠問題都需要AI，但預測性維護、品質預測、製程優化這三個場景AI已經帶來ROI可量化的成效。' },
  { tag: '邊緣AI',        zh: '邊緣運算AI',     prompt: '今天聊Edge AI邊緣運算：把AI推論放在設備端（而非雲端）的優勢 — 低延遲、隱私保護、網路斷線也能運作。NVIDIA Jetson、Intel OpenVINO在工廠的應用。' },

  // 工業4.0 & 數位化
  { tag: '數位雙生',      zh: '數位孿生',       prompt: '今天聊數位雙生（Digital Twin）：為設備建立即時虛擬模型，讓工廠在虛擬世界先跑模擬，再在真實世界執行。如何用IoT感測器讓數位雙生「活起來」？' },
  { tag: '預測性維護',    zh: '預測性維護',     prompt: '今天聊預測性維護（PdM）：振動分析、熱像儀診斷、電流頻譜分析 — 如何在設備壞掉之前就知道它快壞了？設備剩餘使用壽命（RUL）預測的技術邏輯。' },
  { tag: 'IoT',          zh: '工業IoT',        prompt: '今天聊工業物聯網（IIoT）：OPC-UA、MQTT、Modbus TCP這些通訊協定的選型邏輯，以及如何從零開始建立工廠數據蒐集架構，讓既有設備也能「說話」。' },
  { tag: '工業4.0',      zh: '工業4.0',        prompt: '今天聊工業4.0在台灣中小製造業的現實：不是每家都需要完整的智慧工廠，「工業3.5」的漸進升級策略 — 從最有痛點的環節開始，逐步數位化。' },
  { tag: 'MES',          zh: '製造執行系統',    prompt: '今天聊MES製造執行系統：ERP管計畫，MES管現場。為什麼很多工廠有ERP卻沒有MES？製令追蹤、WIP管控、製程參數記錄 — MES如何讓生產透明化。' },
  { tag: 'SCADA',        zh: 'SCADA監控',      prompt: '今天聊SCADA監控系統與工廠儀表板：從Grafana到各大SCADA平台，如何設計一個讓廠長10秒看清現場狀況的製造監控畫面？KPI可視化的設計原則。' },
  { tag: 'OPC-UA',       zh: 'OPC-UA通訊',     prompt: '今天聊OPC-UA（Unified Architecture）：工業4.0時代的通訊骨幹，如何讓不同品牌設備「說同一種語言」？與MQTT的差異，以及為何它是工廠垂直整合的標準。' },

  // 精密製造技術
  { tag: 'CNC加工',      zh: 'CNC精密加工',    prompt: '今天聊CNC精密加工的突破：五軸加工中心、高速鋼切削、微米級公差管控 — 台灣精密機械加工業如何在全球供應鏈中維持競爭力？' },
  { tag: '表面處理',      zh: '表面處理技術',   prompt: '今天聊精密零件表面處理：硬陽極處理（鋁合金）、鍍硬鉻、氮化處理（料管/模具）、DLC塗層 — 每種表面處理對耐磨性、耐腐蝕性的影響與選型邏輯。' },
  { tag: '夾治具',        zh: '夾治具設計',     prompt: '今天聊高精度夾治具設計：重複定位精度±0.02mm是如何實現的？快拆設計縮短換線（SMED），模組化工裝降低治具開發成本 — 治具是自動化系統的基石。' },
  { tag: '量測技術',      zh: '精密量測',       prompt: '今天聊精密量測技術：三次元量測機（CMM）、雷射掃描儀、非接觸光學量測 — 從尺寸量測到幾何公差分析（GD&T），精密製造如何確保「每件都達標」。' },

  // 高溫製程 & 材料
  { tag: '高溫材料',      zh: '工業高溫材料',   prompt: '今天聊工業高溫材料：碳化矽（SiC）、高純度石墨、耐火材料在製造業中的角色 — 為什麼1600°C以上的製程環境對材料選擇如此嚴苛？鋁鑄造與半導體的差異。' },
  { tag: '熱管理',        zh: '工業熱管理',     prompt: '今天聊工業製程熱管理：溫度控制的精度對產品品質的影響，從PID溫控器到多點溫度分佈均勻性，加熱+測溫的整體解決方案思維。' },
  { tag: '鋁鑄造',        zh: '鋁合金鑄造',     prompt: '今天聊鋁合金壓鑄製程優化：熔液脫氣率如何影響鑄件氣孔缺陷率？旋轉脫氣（RDU）+即時溫度監控，是提升鑄件緻密度的關鍵組合。' },
  { tag: '射出成型',      zh: '射出成型優化',   prompt: '今天聊射出成型製程優化：料管溫度均勻性、螺桿背壓設定、保壓時間 — 微小的製程參數偏差如何導致翹曲、縮水、熔接線等不良？數位化製程監控的價值。' },
  { tag: '溫控精度',      zh: '溫度控制精度',   prompt: '今天聊溫度控制精度對製程的影響：半導體擴散爐需要±0.5°C的溫度均勻性，食品殺菌需要精確的巴斯德曲線 — 不同場景對溫控精度的要求與解決方案。' },

  // 產業應用
  { tag: '半導體',        zh: '半導體製程自動化',prompt: '今天聊半導體製程自動化：台灣半導體產業（TSMC供應鏈）對精密設備的要求 — 晶圓搬運機器人、製程爐管材料、亞微米級尺寸控制，這些技術如何支撐摩爾定律繼續前進。' },
  { tag: '電動車',        zh: 'EV電動車製造',   prompt: '今天聊電動車製造的自動化挑戰：電池模組組裝（精密點焊+視覺定位）、電機殼鑄造、動力單元熱管理 — EV時代對台灣零件製造商帶來哪些機會與挑戰？' },
  { tag: '矽光子',        zh: '矽光子技術',     prompt: '今天聊矽光子（Silicon Photonics）：光學與半導體技術的融合，如何解決AI資料中心的互連頻寬瓶頸？精密光纖陣列對準夾具是製程中的關鍵挑戰。' },
  { tag: '人形機器人',    zh: '人形機器人製造',  prompt: '今天聊人形機器人的精密製造需求：關節傳動精度、輕量化鋁合金結構件、耐磨陶瓷導向件 — Tesla Optimus、Figure、Unitree的崛起帶來哪些新的精密加工需求？' },
  { tag: '航太製造',      zh: '航太精密加工',   prompt: '今天聊航太級精密加工：7075-T6航空鋁合金、鈦合金切削、碳纖維複合材料嵌件 — 為什麼航太零件的公差要求是民用工業的10倍嚴？無人機零件製造的技術門檻。' },

  // 供應鏈 & 管理
  { tag: '供應鏈韌性',    zh: '製造業供應鏈',   prompt: '今天聊製造業供應鏈韌性：COVID後時代，台灣製造業如何在「效率」與「風險分散」之間找平衡？近岸採購、庫存緩衝策略、供應商多元化的實務做法。' },
  { tag: '碳中和',        zh: '製造業淨零碳排',  prompt: '今天聊製造業碳中和轉型：工廠用電占台灣碳排放的很大比例。能源監控（ISO 50001）、設備效率提升、廢熱回收 — 精實製造如何同時節省成本與碳排？' },
  { tag: '品質管理',      zh: '製造品質管理',   prompt: '今天聊SPC統計製程控制：如何用Cp/Cpk指數量化製程能力？為什麼「檢驗」永遠比「預防」貴？把品質管制從結果端移到製程端的思維革命。' },
  { tag: '精實供應鏈',    zh: '精實供應鏈管理',  prompt: '今天聊精實供應鏈（Lean Supply Chain）：從JIT原則延伸到整個供應網絡 — 如何讓供應商也「精實化」？VMI供應商管理庫存如何降低整體鏈條浪費。' },
  { tag: '人才培訓',      zh: '製造業人才培育',  prompt: '今天聊製造業人才斷層危機：台灣精密製造業正面臨老師傅退休潮，數位化工具如何幫助知識傳承？技能矩陣、OJT在職訓練、AR輔助訓練的應用。' },

  // 智慧工廠趨勢
  { tag: '燈塔工廠',      zh: 'WEF燈塔工廠',    prompt: '今天聊WEF全球燈塔工廠：世界經濟論壇評選的全球製造業燈塔工廠，台灣有哪些入選？這些工廠的共同特徵是什麼？普通中小企業能從他們身上學到什麼？' },
  { tag: '低碼平台',      zh: '工廠低碼開發',   prompt: '今天聊低碼/無碼（Low-code/No-code）在工廠的應用：讓製造工程師不需要寫程式也能建立IoT儀表板、設備警報系統和生產報表，民主化工廠數位化。' },
  { tag: 'ChatGPT製造',   zh: 'AI大語言模型製造', prompt: '今天聊生成式AI在製造業的實際應用：用LLM分析設備異常報告、自動生成SOP文件、優化維修派工 — 哪些製造場景最適合導入生成式AI？' },
  { tag: '數位製造',      zh: '數位製造轉型',   prompt: '今天聊數位製造（Digital Manufacturing）的四個層次：連結（設備上網）→可視（即時儀表板）→分析（AI診斷）→自主（閉環優化）。大多數台灣工廠目前在第幾層？' },
  { tag: '工廠設計',      zh: '未來工廠設計',   prompt: '今天聊未來工廠（Factory of the Future）設計：從廠房佈局到物料流動路線，如何用「數位雙生」在工廠蓋好之前就模擬最優佈局？避免建好才發現效率問題。' },
  { tag: 'AR輔助',        zh: 'AR擴增實境維修',  prompt: '今天聊AR擴增實境在工廠維修的應用：工程師戴上AR眼鏡，系統即時標示設備故障位置、顯示維修步驟 — 讓新手工程師擁有老師傅的現場判斷力。' },

  // 台灣製造業觀點
  { tag: '台灣製造',      zh: '台灣製造業優勢',  prompt: '今天聊台灣製造業的核心競爭力：彈性、速度、技術深度 — 台灣中小企業如何在全球供應鏈中找到無法被取代的位置？「工具機王國」到「智慧製造王國」的路。' },
  { tag: '桃園製造',      zh: '桃園工業生態',   prompt: '今天聊桃園工業聚落：從航空城到大園工業區，桃園為什麼是台灣製造業的核心腹地？半導體、航太、精密機械、汽車零件的完整供應鏈生態系。' },
  { tag: '製造創新',      zh: '製造業創新思維',  prompt: '今天分享一個製造業創新案例：不一定需要砸大錢換設備，有時候改變一個工作方式、優化一道工序、導入一個小工具，就能創造出可量化的效益。精實創新的本質。' },
  { tag: '自動化ROI',     zh: '自動化投資報酬',  prompt: '今天聊工廠自動化的ROI計算：如何說服老闆批自動化預算？人力成本節省、不良品率下降、設備利用率提升 — 一個讓決策者看懂的自動化投資回收計算框架。' },
  { tag: '小批量生產',    zh: '小批量多樣化製造', prompt: '今天聊小批量多樣化（High-Mix Low-Volume, HMLV）製造的挑戰：台灣很多工廠面臨這個問題 — 換線頻繁、庫存多、排程複雜。彈性製造系統（FMS）如何破解？' },
];

// ── 工具函數 ─────────────────────────────────────────────────────────────────

function getTodayTopic() {
  const now = new Date();
  // 台灣時間
  const twOffset = 8 * 60 * 60 * 1000;
  const twDate = new Date(now.getTime() + twOffset);
  const dayOfYear = Math.floor(
    (twDate - new Date(twDate.getUTCFullYear(), 0, 0)) / 86400000
  );
  const topic = TOPICS[dayOfYear % TOPICS.length];
  const dateStr = twDate.toISOString().split('T')[0];
  console.log(`📅 日期：${dateStr}（年第${dayOfYear}天）`);
  console.log(`📌 今日題材：${topic.zh}（#${topic.tag}）`);
  return { topic, dateStr };
}

function buildPrompt(topic) {
  return `你是欣晨工業有限公司的社群媒體編輯，負責在 Facebook 粉絲專頁發布智慧製造相關貼文。

欣晨工業基本資料：
- 台灣桃園市大園區的B2B精密自動化設備製造商
- 1975年創立，51年製造經驗
- 以豐田生產方式（TPS）為核心哲學：Kaizen改善、JIT即時生產、Jidoka自働化
- 產品：工業加熱器（1200°C）、熱電偶、一體式料管、碳化矽保護管、石墨脫氣管、耐火材料
- 服務：機械手臂整合（FANUC/ABB/KUKA）、視覺檢測AOI、數位雙生、夾治具設計、設備智能化

今日題材：${topic.zh}
方向：${topic.prompt}

請依照以下固定格式撰寫 Facebook 貼文：

【題目】
📌 ${topic.zh}（用一句有衝擊力的副標題，15字以內）

【內容】
說明這個主題的核心重點，以編號項次列出 3-5 點：
① 第一點（30-40字，含具體數字或案例）
② 第二點（30-40字）
③ 第三點（30-40字）
④ 第四點（選填，30-40字）
⑤ 第五點（選填，30-40字）

【如何執行】
給製造業從業人員 2-3 個可立刻行動的具體步驟：
▶ 步驟一：（20-30字，具體可操作）
▶ 步驟二：（20-30字）
▶ 步驟三：（20-30字）

最後附上 1 個開放性問題邀請互動，以及 5-7 個 hashtag。

風格：專業不說教，繁體中文，不過度推銷欣晨，讓讀者自然聯想到欣晨的專業。
直接輸出貼文，不要加任何前言說明。`;
}

async function generatePost(topic) {
  console.log('🤖 呼叫 Claude API 生成文案...');
  const message = await client.messages.create({
    model: 'claude-haiku-4-5',
    max_tokens: 1024,
    messages: [
      { role: 'user', content: buildPrompt(topic) }
    ],
  });
  const content = message.content[0].text.trim();
  console.log(`✅ 文案生成完成（${content.length} 字）`);
  return content;
}

async function postToFacebook(message) {
  const pageId = process.env.FB_PAGE_ID;
  const accessToken = process.env.FB_ACCESS_TOKEN;

  if (!pageId || !accessToken) {
    throw new Error('缺少 FB_PAGE_ID 或 FB_ACCESS_TOKEN 環境變數');
  }

  const url = `https://graph.facebook.com/v21.0/${pageId}/feed`;
  const body = new URLSearchParams({
    message,
    access_token: accessToken,
  });

  console.log('📤 發送至 Facebook...');
  const res = await fetch(url, { method: 'POST', body });
  const data = await res.json();

  if (!res.ok || data.error) {
    const errMsg = data.error?.message || `HTTP ${res.status}`;
    throw new Error(`Facebook API 錯誤：${errMsg}`);
  }

  console.log(`✅ 發文成功！Post ID：${data.id}`);
  return data.id;
}

// ── 主程式 ───────────────────────────────────────────────────────────────────

async function main() {
  console.log('═══════════════════════════════════════════');
  console.log('  欣晨工業 — 每日智慧製造 Facebook 自動發文');
  console.log('═══════════════════════════════════════════');

  const isDryRun = process.env.DRY_RUN === 'true';
  if (isDryRun) console.log('⚠️  DRY RUN 模式：只產生文案，不實際發文\n');

  const { topic, dateStr } = getTodayTopic();
  const postContent = await generatePost(topic);

  console.log('\n──── 產生的貼文內容 ────────────────────────');
  console.log(postContent);
  console.log('────────────────────────────────────────────\n');

  if (isDryRun) {
    console.log('✅ Dry run 完成。');
    return;
  }

  const postId = await postToFacebook(postContent);
  console.log(`🎉 完成！${dateStr} 貼文已發布。`);
}

main().catch(err => {
  console.error('❌ 執行失敗：', err.message);
  process.exit(1);
});
