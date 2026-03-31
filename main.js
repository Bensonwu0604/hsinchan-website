/**
 * 欣晨工業有限公司 — Hsin-Chan Industrial Co., Ltd.
 * main.js · v1.1 · 2026-03-01  (optimized)
 *
 * Modules:
 *  1. i18n          — Language switcher (zh-TW / ja / en)
 *  2. nav           — Sticky header + mobile menu
 *  3. scrollReveal  — IntersectionObserver fade-in
 *  4. counter       — Animated number counting
 *  5. heroCanvas    — Particle network animation
 *  6. productTilt   — Mouse-parallax tilt on product images
 *  7. smoothScroll  — Smooth anchor link scrolling
 *  8. footerYear    — Auto-update copyright year
 */

'use strict';

/* ═══════════════════════════════════════════════════════════════════════════
   1. i18n TRANSLATIONS
   ═══════════════════════════════════════════════════════════════════════════ */
const translations = {
  zh: {
    nav_home: '首頁', nav_about: '公司簡介', nav_products: '產品資訊',
    nav_services: '服務項目', nav_tech: '新技術討論',
    nav_careers: '人力資源', nav_contact: '聯絡我們',

    hero_badge: '以豐田生產哲學淬鍊的製造夥伴 · Since 1975',
    hero_h1_line1: '精密驅動，', hero_h1_line2: '智造未來',
    hero_h2: '以改善、即時生產與自働化為核心，提供精密自動化解決方案',
    cta_products: '查看產品', cta_contact_ask: '聯絡詢問',
    metric_years: '年經驗', metric_products: '大產品線',
    metric_services: '大服務項目', scroll: 'SCROLL',

    adv_title: '以豐田哲學，驅動卓越製造',
    adv_lead: '欣晨工業以豐田生產方式（TPS）三大支柱為核心，為每一位客戶帶來持續精進、零浪費的製造價值。',
    adv_1_title: '即時生產',
    adv_1_desc: '正確的零件、在正確的時間、以正確的數量交付。欣晨以JIT精神規劃每一個自動化項目，消除等待浪費，確保您的生產線流暢無阻。',
    adv_2_title: '持續改善',
    adv_2_desc: '每天比昨天進步一點點。欣晨工業的工程師將「沒有最好，只有更好」內化為工作準則，從設計圖面到現場調機，永不滿足於「夠好」。',
    adv_3_title: '自働化',
    adv_3_desc: '設備能自動偵測異常並停機，讓問題不流向下一道工序。欣晨的視覺檢測與自動化方案，賦予您的產線「能判斷、會停機」的製造智慧。',

    stat_years_label: '年製造經驗', stat_products_label: '大產品線',
    stat_products_sub: '高溫工業耗材', stat_services_label: '大服務項目',
    stat_services_sub: '自動化整合', stat_jobs_label: '職缺招募中',
    stat_jobs_sub: '工程師職位',

    prod_eyebrow: 'FEATURED PRODUCT',
    prod_a_title: '碳化矽保護管',
    prod_a_desc: '採用高純度碳化矽（SiC）製造，耐熱溫度超過 1600°C，耐腐蝕性能卓越。廣泛應用於半導體製程爐管、鋁液熔煉，以及各類高溫工業場景。',
    prod_a_mat: '高純度 SiC', prod_a_app: '半導體 / 鑄造業',
    prod_b_title: '石墨脫氣管',
    prod_b_desc: '高純度石墨材質，專為鋁液精煉脫氣設計。在熔鋁爐中有效去除氫氣與雜質，提升鑄件品質。超長使用壽命，大幅降低換管頻率與停機成本。',
    prod_b_use: '鋁液精煉脫氣', prod_b_merit: '長壽命低耗損',
    spec_temp: '耐溫', spec_mat: '材質', spec_app: '應用',
    spec_purity: '純度', spec_use: '用途', spec_merit: '優勢',
    spec_type: '類型', spec_heat: '溫度', spec_spec: '規格', spec_model: '型號', spec_measure: '量測',
    cta_spec: '查看規格',

    srv_title: '全方位自動化服務',
    srv_lead: '六大服務，從規劃到交機，一站式解決您的自動化需求',
    srv_1_title: '數位雙生自動化設計規劃', srv_1_desc: '虛擬驗證產線，降低建造風險',
    srv_2_title: '機械手臂應用',           srv_2_desc: '搬運、焊接、組裝整合，路徑規劃',
    srv_3_title: '單機自動化設計製造',     srv_3_desc: '需求→設計→製造→調機，一條龍',
    srv_4_title: '視覺檢測',               srv_4_desc: '工業相機 + AI 瑕疵偵測、尺寸量測',
    srv_5_title: '夾治具設計製造',         srv_5_desc: '高精度夾具治具，提升一致性',
    srv_6_title: '設備智能化',             srv_6_desc: '既有設備升級 PLC / HMI / IoT',
    cta_learn: '了解更多', cta_all_services: '了解全部服務',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    tech_title: '豐田哲學 × 精密製造應用',
    tech_tag_semi: '半導體製程', tech_tag_ev: '電動車', tech_tag_robot: '人形機器人',
    tech_1_title: '精密製程的材料關鍵',
    tech_1_desc: '碳化矽保護管在半導體高溫製程中扮演關鍵角色，提供穩定的熱環境與腐蝕防護。',
    tech_2_title: '電池生產熱管理革新',
    tech_2_desc: 'EV 電池芯製造需要精確的熱管理解決方案，欣晨加熱器與感測元件確保生產一致性。',
    tech_3_title: '機器人關節精密加工',
    tech_3_desc: '人形機器人關節需要極高精度的製造工藝，欣晨夾治具設計為此提供精準解決方案。',
    cta_read_more: '閱讀更多', cta_view_all_tech: '查看全部技術主題',

    cta_banner_title: '準備好以豐田哲學優化您的生產線了嗎？',
    cta_banner_desc: '告訴我們您的現場問題，欣晨工業的工程師將親赴現場，以改善精神為您量身設計最佳方案。',
    cta_contact_now: '立即聯絡',

    footer_nav_title: '快速導覽', footer_contact_title: '聯絡資訊',
    footer_years: '51年製造經驗',
    footer_addr: '桃園市大園區中正東路三段490號',
    footer_tel: 'Tel：03-381-4497', footer_fax: 'Fax：03-381-4536',
    footer_tagline_1: '精密驅動', footer_tagline_2: '智造未來',
    footer_est: 'Est. 1975 · 51年製造經驗',

    // About page
    about_banner_title: '公司簡介',
    about_banner_lead: '51年精密製造經驗，深根桃園，服務全台灣工業客戶。以技術立業，以品質興業，以服務創業。',
    about_our_title: '關於我們',
    about_desc_1: '欣晨工業有限公司成立於1975年，座落於桃園市大園工業區。歷經半世紀的積累，我們從早期的工業耗材供應商，逐步發展為涵蓋自動化設備設計、製造、整合及售後服務的全方位製造夥伴。',
    about_desc_2: '公司主要產品涵蓋碳化矽保護管、石墨脫氣管、加熱器、熱電偶等高溫工業耗材，並持續拓展數位雙生規劃、機械手臂應用、視覺檢測等智能自動化服務領域。',
    about_desc_3: '時至今日，欣晨工業仍以豐田生產方式（TPS）的改善精神與精密加工技術為本，為半導體、鑄造、電動車、精密機械等產業提供持續進化的製造解決方案。',
    about_history_eyebrow: '發展歷程',
    about_tl_1_title: '公司創立', about_tl_1_desc: '於桃園大園設立，專注高溫工業耗材製造與供應，服務在地製造業客戶。',
    about_tl_2_title: '產品線擴展', about_tl_2_desc: '導入碳化矽保護管與石墨脫氣管生產技術，服務對象延伸至半導體與鑄造業。',
    about_tl_3_title: '廠房擴建', about_tl_3_desc: '新增加熱器與熱電偶生產線，廠房面積擴建，提升年產能與品管能力。',
    about_tl_4_title: '自動化轉型', about_tl_4_desc: '跨足自動化設備設計製造，提供機械手臂整合、單機自動化及視覺檢測服務。',
    about_tl_5_title: '智能升級', about_tl_5_desc: '引入數位雙生技術，推動既有設備智能化，邁向工業4.0整合服務商。',
    about_phil_title: '經營理念',
    about_phil_lead: '三大核心理念，驅動欣晨51年的穩健成長，也是我們服務每位客戶的承諾。',
    about_phil_1_title: '精密製造', about_phil_1_desc: '51年製造工藝積累，嚴格品質管控體系，每一個零件精準達標。從原材料進料到成品出廠，全程品質追蹤，確保設備穩定可靠運行。',
    about_phil_2_title: '客製服務', about_phil_2_desc: '從需求分析、機構設計到生產交機，全程一對一客製化服務。我們深入了解客戶生產現場，量身打造最適合您生產線的自動化解決方案。',
    about_phil_3_title: '技術支援', about_phil_3_desc: '專業工程師團隊現場調機與技術培訓，完善的售後維護體系。設備交機後持續提供技術諮詢，確保您的生產設備長期穩定高效運行。',
    about_team_title: '經營團隊',
    about_team_lead: '擁有豐富產業經驗的專業團隊，持續推動公司技術創新與服務升級。',
    about_team_1_role: '總經理', about_team_1_desc: '負責公司整體策略規劃與營運管理，帶領團隊持續創新，深耕自動化設備製造領域逾三十年。',
    about_team_2_role: '技術長', about_team_2_desc: '主導研發部門，專精於高溫材料工程與自動化機構設計，具備豐富的半導體製程設備開發經驗。',
    about_team_3_role: '業務總監', about_team_3_desc: '統籌業務開發與客戶關係管理，深入了解客戶需求，為各產業客戶提供最適切的自動化解決方案。',
    about_cta_title: '與我們合作，共創精密未來',
    about_cta_desc: '無論是產品詢價、技術諮詢或專案合作，歡迎聯絡欣晨工業的專業團隊。',
    about_cta_btn: '立即聯絡',

    // Products page
    pp_banner_title: '產品資訊',
    pp_banner_lead: '六大精密耐高溫工業耗材，適用於半導體、鑄造、電動車等先進製程，每一款均可依需求客製化規格。',
    pp_overview_title: '六大產品線', pp_overview_lead: '所有產品均通過嚴格品質管控，適用於高溫、腐蝕性、精密工業環境。',
    pp_p1_tag: '射出成形耗材', pp_p1_title: '一體式料管',
    pp_p1_desc: '採用高品質合金鋼精密加工，一體成型設計消除接縫滲漏風險，提升射出成形機的穩定性與壽命。',
    pp_p1_s1: '材質：氮化鋼', pp_p1_s2: '硬度：HRC 60–65', pp_p1_s3: '客製化尺寸規格', pp_p1_btn: '詢問報價',
    pp_p2_tag: '高溫製程耗材', pp_p2_title: '碳化矽保護管',
    pp_p2_desc: '採用高純度碳化矽（SiC）製造，耐熱溫度超過1600°C，耐腐蝕性能卓越。廣泛應用於半導體爐管、鋁液熔煉等高溫工業場景。',
    pp_p2_s1: '耐溫：＞1600°C', pp_p2_s2: '材質：高純度 SiC', pp_p2_s3: '抗熱衝擊、耐腐蝕', pp_p2_btn: '詢問報價',
    pp_p3_tag: '窯爐工業耗材', pp_p3_title: '耐火材料',
    pp_p3_desc: '高溫穩定性卓越的耐火磚、耐火泥及定形耐火製品，適用於各類冶金爐、工業窯爐及高溫製程設備的爐膛砌築與維修。',
    pp_p3_s1: '耐溫：依材質達1800°C', pp_p3_s2: '抗壓強度高、低熱傳導', pp_p3_s3: '多種材質與規格可選', pp_p3_btn: '詢問報價',
    pp_p4_tag: '鋁合金精煉耗材', pp_p4_title: '石墨脫氣管',
    pp_p4_desc: '高純度石墨材質，專為鋁液精煉脫氣設計，有效去除熔融鋁液中的氫氣與雜質，提升鑄件品質。超長使用壽命大幅降低換管成本。',
    pp_p4_s1: '純度：＞99.9% 高純度石墨', pp_p4_s2: '耐溫：＞900°C、抗氧化', pp_p4_s3: '多種直徑與長度客製化', pp_p4_btn: '詢問報價',
    pp_p5_tag: '精密溫控元件', pp_p5_title: '加熱器',
    pp_p5_desc: '涵蓋電熱管、陶瓷加熱器、紅外線加熱器等多種類型，適用於工業加熱製程、模具預熱、半導體設備等場景，提供精確穩定的加熱控制。',
    pp_p5_s1: '耐溫：依類型達1200°C', pp_p5_s2: '多種功率規格（50W–10kW）', pp_p5_s3: '客製化形狀與接線方式', pp_p5_btn: '詢問報價',
    pp_p6_tag: '精密量測元件', pp_p6_title: '熱電偶',
    pp_p6_desc: '提供K型、J型、N型、S型、R型及B型等多種熱電偶，搭配各類保護管材質，適用於熔爐測溫、半導體製程溫控、食品加工等廣泛工業應用。',
    pp_p6_s1: '測溫範圍：−200°C ～ +1800°C', pp_p6_s2: '多種型號與保護管材質', pp_p6_s3: 'IEC / JIS 規範符合', pp_p6_btn: '詢問報價',
    pp_qa_title: '品質保證', pp_qa_lead: '每一款產品均通過嚴格的品質檢測流程，以確保符合客戶規格與國際標準。',
    pp_qa_1_title: '嚴格品質管控', pp_qa_1_desc: '從原材料進料到成品出廠，全程品管追蹤，確保每一件產品達標。',
    pp_qa_2_title: '客製化規格', pp_qa_2_desc: '提供客製化尺寸、材質與規格服務，滿足各類特殊製程的獨特需求。',
    pp_qa_3_title: '快速交期', pp_qa_3_desc: '完善的庫存管理與生產排程，確保標準品快速出貨，客製品準時交付。',
    pp_cta_title: '找不到合適的規格？',
    pp_cta_desc: '欣晨工業提供全客製化服務，告訴我們您的需求，我們的技術團隊將為您設計最適合的產品規格。',
    pp_cta_btn: '立即詢問',

    // Services page
    srv_page_title: '服務項目',
    srv_page_lead: '六大自動化服務，從數位規劃、機械手臂整合、視覺檢測，到設備智能化升級，一站式滿足您的製造需求。',
    srv_d1_num: 'SERVICE 01', srv_d1_tag: 'Digital Twin', srv_d1_title: '數位雙生自動化設計規劃',
    srv_d1_desc: '在實體建造前，先以數位雙生技術於虛擬環境中完整模擬產線運作。透過3D模型與動態模擬，提前發現設計缺陷，大幅降低建造風險與修改成本。',
    srv_d1_p1: '虛擬產線佈局規劃與動作模擬', srv_d1_p2: '設備干涉檢查與安全評估',
    srv_d1_p3: '節拍時間（Takt Time）分析最佳化', srv_d1_p4: '3D設計圖面與技術規格書提供', srv_d1_btn: '諮詢此服務',
    srv_d2_num: 'SERVICE 02', srv_d2_tag: 'Robot Integration', srv_d2_title: '機械手臂應用',
    srv_d2_desc: '整合各大品牌工業機器人（FANUC、ABB、KUKA、Yaskawa等），提供搬運、焊接、組裝、塗膠等多元應用，搭配末端夾爪設計與路徑規劃，打造高效柔性生產線。',
    srv_d2_p1: '多品牌機械手臂選型與導入', srv_d2_p2: '末端效應器（夾爪/工具）客製設計',
    srv_d2_p3: '離線程式規劃與路徑最佳化', srv_d2_p4: '人機協作（Cobot）安全系統整合', srv_d2_btn: '諮詢此服務',
    srv_d3_num: 'SERVICE 03', srv_d3_tag: 'Custom Automation', srv_d3_title: '單機自動化設計製造',
    srv_d3_desc: '從客戶需求分析、機構概念設計、工程圖面繪製、零件加工製造，到整機組裝、程式撰寫與現場調機，提供完整的一條龍自動化設備設計製造服務。',
    srv_d3_p1: '需求分析與方案可行性評估', srv_d3_p2: '機構設計與3D建模（SolidWorks / Solid Edge）',
    srv_d3_p3: 'PLC / HMI 程式開發（三菱 / 西門子）', srv_d3_p4: '整機測試、現場安裝與人員培訓', srv_d3_btn: '諮詢此服務',
    srv_d4_num: 'SERVICE 04', srv_d4_tag: 'Machine Vision', srv_d4_title: '視覺檢測',
    srv_d4_desc: '結合工業相機、高精度鏡頭與AI影像分析技術，實現產品外觀瑕疵偵測、尺寸量測、條碼辨識及位置引導等功能，取代人工目視，大幅提升檢測效率與一致性。',
    srv_d4_p1: '外觀缺陷偵測（刮傷、污點、缺料）', srv_d4_p2: '高精度尺寸量測（±0.01mm）',
    srv_d4_p3: 'QR Code / Barcode / OCR 辨識', srv_d4_p4: '視覺引導機械手臂定位取料', srv_d4_btn: '諮詢此服務',
    srv_d5_num: 'SERVICE 05', srv_d5_tag: 'Fixture Design', srv_d5_title: '夾治具設計製造',
    srv_d5_desc: '設計並製造高精度工裝夾具與治具，用於自動化組裝、加工、檢測等製程。精確的定位與夾持設計，確保每一件產品的加工位置一致性，提升產品良率。',
    srv_d5_p1: '機加工夾具、焊接治具、組裝工裝', srv_d5_p2: '材質選用：鋁合金、工具鋼、不鏽鋼',
    srv_d5_p3: '重複定位精度：±0.02mm', srv_d5_p4: '快拆設計，縮短換線時間', srv_d5_btn: '諮詢此服務',
    srv_d6_num: 'SERVICE 06', srv_d6_tag: 'Smart Upgrade', srv_d6_title: '設備智能化',
    srv_d6_desc: '為既有傳統設備加裝PLC、HMI、IoT模組，實現遠端監控、資料蒐集與預知保養功能。無需全面換新設備，以最低投資提升舊有產線的數位化水準。',
    srv_d6_p1: 'PLC控制器升級（三菱 iQ-F / iQ-R）', srv_d6_p2: 'HMI人機介面加裝（Pro-face / Weintek）',
    srv_d6_p3: 'IoT資料蒐集與雲端監控儀表板', srv_d6_p4: 'OEE設備效率分析與異常通報系統', srv_d6_btn: '諮詢此服務',
    srv_cta_title: '準備啟動您的自動化專案？',
    srv_cta_desc: '無論是全新產線規劃還是既有設備升級，欣晨工業的工程師團隊都能提供最適合的解決方案。',
    srv_cta_btn: '立即洽詢',

    // Technology page
    tech_page_title: '新技術討論',
    tech_page_lead: '從半導體製程到人形機器人，探討欣晨精密零件與耐高溫材料在六大前沿領域中的關鍵應用與技術貢獻。',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: 'Semiconductor', tech_d1_title: '半導體製程',
    tech_d1_desc: '半導體晶圓製程需要在超高溫、強腐蝕性環境中精準操控熔融金屬與化學材料。欣晨的碳化矽（SiC）保護管與石墨脫氣管，以其卓越的耐熱衝擊性與化學惰性，成為擴散爐管、長晶設備等核心製程設備的關鍵耗材。',
    tech_d1_p1: 'SiC保護管：耐溫達1600°C，抗氧化與抗腐蝕', tech_d1_p2: '石墨脫氣管：有效去除熔融鋁液中的氫氣雜質',
    tech_d1_p3: '一體式料管：確保熔融矽材輸送的純淨無汙染', tech_d1_p4: '客製化尺寸，適配各式長晶爐與PECVD設備', tech_d1_btn: '諮詢應用方案',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: 'Electric Vehicle', tech_d2_title: '電動車',
    tech_d2_desc: '電動車的電池模組、電機與功率電子元件對熱管理有嚴苛要求。欣晨的耐火材料與高精度陶瓷零件，廣泛應用於電池包結構防護、電機定子絕緣及鑄造廠鋁合金電機殼的生產製程中。',
    tech_d2_p1: '電池模組防火隔熱板：阻燃耐高溫結構保護', tech_d2_p2: '鋁合金鑄造製程保護管：電機殼體生產必備',
    tech_d2_p3: '陶瓷熱電偶：精確監控電機運行溫度', tech_d2_p4: '耐高溫絕緣材料：適用功率模組（IGBT/SiC MOSFET）', tech_d2_btn: '諮詢應用方案',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'Silicon Photonics', tech_d3_title: '矽光子',
    tech_d3_desc: '矽光子技術將光學元件整合於矽基板上，實現高速光通訊與AI加速運算。欣晨提供應用於光子晶片封裝製程的高精度陶瓷載具、耐高溫夾治具及製程保護零件。',
    tech_d3_p1: '高精度陶瓷定位夾具：光纖陣列對準夾持', tech_d3_p2: '耐高溫製程載具：鍵合製程穩定承載',
    tech_d3_p3: '氧化鋁陶瓷隔熱板：退火爐製程熱均勻分佈', tech_d3_p4: '客製化規格，配合晶圓廠製程節點需求', tech_d3_btn: '諮詢應用方案',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'Humanoid Robot', tech_d4_title: '人形機器人',
    tech_d4_desc: '人形機器人的關節傳動、末端執行器與感知系統需要兼顧輕量化與高精度的零件製造。欣晨憑藉51年精密加工經驗，提供鋁合金結構件、精密傳動套筒及耐磨陶瓷元件。',
    tech_d4_p1: '關節傳動精密套筒：保持動作重複定位精度', tech_d4_p2: '輕量鋁合金結構件：降低本體重量，提升靈活性',
    tech_d4_p3: '耐磨陶瓷導向件：延長關節使用壽命', tech_d4_p4: '高精度公差管控：±0.01mm 級別加工能力', tech_d4_btn: '諮詢應用方案',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: 'Quantum Computing', tech_d5_title: '量子電腦',
    tech_d5_desc: '量子電腦的稀釋冷凍機需將量子比特維持在接近絕對零度（15 mK）的環境中，對零件的熱傳導性、電磁干擾防護與超精密加工有極端要求。',
    tech_d5_p1: '高純度無氧銅（OFC）精密零件：優異導熱與導電性', tech_d5_p2: '陶瓷隔熱結構件：低溫環境下的熱絕緣設計',
    tech_d5_p3: '超精密加工：表面粗糙度 Ra ≤ 0.4μm', tech_d5_p4: '嚴格潔淨度管控：避免量子態干擾汙染', tech_d5_btn: '諮詢應用方案',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / Drone', tech_d6_title: '無人機',
    tech_d6_desc: '無人機追求極致輕量化與結構強度的平衡，電機座、傳動軸、雲台架等關鍵零件需要精密加工與嚴格品質管控。欣晨為無人機廠商提供高強度鋁合金機構件、碳纖維複合材料嵌件及客製化工裝治具。',
    tech_d6_p1: '航空鋁合金（7075-T6）輕量化結構件', tech_d6_p2: '電機固定座：精密孔位確保馬達同心度',
    tech_d6_p3: '碳纖維複合材料嵌入式金屬螺套', tech_d6_p4: '快速打樣與小批量量產彈性服務', tech_d6_btn: '諮詢應用方案',
    tech_cta_title: '探索精密材料在您領域的應用？',
    tech_cta_desc: '欣晨工業的技術團隊歡迎與各前沿科技領域的廠商共同探討材料解決方案，一起推動技術邊界。',
    tech_cta_btn: '立即聯繫技術團隊',

    // Careers page
    career_page_title: '人力資源',
    career_page_lead: '加入欣晨工業，與我們一同傳承51年精密製造工藝，共同迎接自動化與新材料時代的機遇與挑戰。',
    career_apply_title: '應徵方式',
    career_apply_lead: '歡迎有志加入欣晨工業的朋友，將您的履歷表與自傳寄送至以下信箱，我們的人資團隊將於收到資料後三個工作日內與您聯繫。',
    career_apply_label: 'Email 應徵',
    career_apply_note: '請於主旨標明「應徵職位名稱 ＋ 姓名」，並附上完整履歷與自傳',
    career_jobs_title: '目前開缺職位',
    career_j1_tag: '工程製造', career_j1_title: '精密機械加工員',
    career_j1_p1: '操作CNC車床、銑床等精密加工設備', career_j1_p2: '依據工程圖面進行零件加工與品質自主檢驗',
    career_j1_p3: '學歷：高中職以上，機械相關科系尤佳', career_j1_p4: '具有加工經驗者優先錄用，可接受訓練生', career_j1_btn: '立即應徵',
    career_j2_tag: '業務行銷', career_j2_title: '業務工程師',
    career_j2_p1: '開發與維護國內外客戶關係', career_j2_p2: '解讀客戶技術需求並提供材料解決方案',
    career_j2_p3: '學歷：大專以上，工程或化工相關背景佳', career_j2_p4: '具備日文或英文溝通能力者優先', career_j2_btn: '立即應徵',
    career_j3_tag: '自動化技術', career_j3_title: '自動化設備工程師',
    career_j3_p1: '規劃、設計及整合自動化生產設備', career_j3_p2: 'PLC程式設計（三菱 iQ-F / iQ-R）與HMI整合',
    career_j3_p3: '學歷：大專以上，電機、機電或自控相關科系', career_j3_p4: '具機械手臂整合或視覺系統經驗者尤佳', career_j3_btn: '立即應徵',
    career_ben_title: '員工福利',
    career_ben_lead: '欣晨工業重視每一位員工的工作品質與職涯發展，提供完善的福利制度與成長環境。',
    career_ben_1_title: '勞保', career_ben_1_desc: '依法投保勞工保險，保障員工職災、傷病、老年、失業等各項給付，守護職場安全。',
    career_ben_2_title: '健保', career_ben_2_desc: '依法投保全民健康保險，員工及眷屬享有完整醫療保障，照顧全家人的健康。',
    career_ben_3_title: '全勤獎金', career_ben_3_desc: '當月全勤者發放全勤獎金，肯定員工認真負責的工作態度與敬業精神。',
    career_ben_4_title: '年節獎金', career_ben_4_desc: '春節、端午、中秋三節發放節慶獎金，與員工共享傳統佳節的喜悅與溫情。',
    career_ben_5_title: '員工生日禮金', career_ben_5_desc: '員工生日時致贈生日禮金，表達公司對每一位成員的重視、關懷與祝福。',
    career_ben_6_title: '年終獎金', career_ben_6_desc: '依年度績效發放年終獎金，肯定員工全年努力貢獻，分享公司成長的豐碩成果。',
    career_ben_7_title: '員工團保', career_ben_7_desc: '額外提供員工團體保險，涵蓋意外及醫療保障，給予員工更全面的安全保障。',
    career_ben_8_title: '國內旅遊', career_ben_8_desc: '定期舉辦國內員工旅遊，讓同仁放鬆充電、增進情誼，打造凝聚力強的工作團隊。',
    career_ben_9_title: '尾牙', career_ben_9_desc: '年末舉辦尾牙宴，感謝員工一整年的辛勞付出，共同歡慶豐收、迎接嶄新一年。',
    career_cta_title: '準備好加入欣晨了嗎？',
    career_cta_desc: '將您的履歷寄送至 hc3814497@gmail.com，我們期待與您共同創造欣晨的下一個50年。',
    career_cta_btn: '立即投遞履歷',

    // Contact page
    contact_page_title: '聯絡我們',
    contact_page_lead: '無論是產品詢價、技術合作或服務洽談，歡迎透過以下方式與欣晨工業聯繫，我們將於1-2個工作日內回覆。',
    contact_info_title: '公司資訊',
    contact_label_addr: '地址', contact_addr_value: '33841 桃園市大園區中正東路三段490號',
    contact_label_tel: '電話', contact_label_email: 'Email', contact_label_fax: '傳真',
    contact_label_fb: 'Facebook', contact_fb_value: '欣晨工業有限公司',
    contact_hours_title: '營業時間',
    contact_hours_weekday: '週一至週五　08:00 – 17:30',
    contact_hours_weekend: '週六、週日　公休',
    contact_form_title: '線上詢問',
    contact_form_lead: '請填寫以下資料，我們將於1-2個工作日內與您聯繫回覆。',
    contact_form_name_label: '姓名', contact_form_company_label: '公司 ／ 單位',
    contact_form_tel_label: '電話', contact_form_email_label: 'Email', contact_form_msg_label: '詢問內容',
    contact_form_name_ph: '請輸入您的姓名', contact_form_company_ph: '請輸入公司或單位名稱',
    contact_form_tel_ph: '例：02-1234-5678', contact_form_email_ph: 'example@company.com',
    contact_form_msg_ph: '請描述您的需求，例如：產品規格詢問、報價需求、技術合作洽談等…',
    contact_form_submit: '送出詢問',
  },

  ja: {
    nav_home: 'ホーム', nav_about: '会社概要', nav_products: '製品情報',
    nav_services: 'サービス', nav_tech: '新技術', nav_careers: '採用情報',
    nav_contact: 'お問い合わせ',

    hero_badge: '精密自動化ソリューション · Since 1975',
    hero_h1_line1: '精密が駆動する、', hero_h1_line2: '未来を創る',
    hero_h2: 'カイゼン・JIT・自働化を核に、精密自動化ソリューションを提供',
    cta_products: '製品を見る', cta_contact_ask: 'お問い合わせ',
    metric_years: '年の経験', metric_products: '製品ライン',
    metric_services: 'サービス項目', scroll: 'SCROLL',

    adv_title: 'トヨタ哲学が駆動する、卓越した製造',
    adv_lead: '欣晨工業はトヨタ生産方式（TPS）の三大支柱を核心に、すべてのお客様に継続的改善とムダゼロの製造価値を提供します。',
    adv_1_title: 'ジャスト・イン・タイム',
    adv_1_desc: '必要な部品を、必要な時に、必要な数量で。欣晨はJIT精神に基づきすべての自動化プロジェクトを設計し、待機のムダを排除して生産ラインのスムーズな稼働を確保します。',
    adv_2_title: 'カイゼン（改善）',
    adv_2_desc: '毎日、昨日より一歩前進する。欣晨のエンジニアは「最善はなく、さらに良くなれる」を信念とし、図面設計から現場調整まで「十分」に満足せず改善を追求し続けます。',
    adv_3_title: '自働化（ジドウカ）',
    adv_3_desc: '設備が自律的に異常を検知して停止し、不良品が次工程に流れるのを防止します。欣晨の画像検査・自動化ソリューションが、生産ラインに「判断・停止」の製造知性をもたらします。',

    stat_years_label: '年の製造経験', stat_products_label: '製品ライン',
    stat_products_sub: '高温工業用消耗品', stat_services_label: 'サービス項目',
    stat_services_sub: '自動化統合', stat_jobs_label: '求人募集中',
    stat_jobs_sub: 'エンジニアポジション',

    prod_eyebrow: 'FEATURED PRODUCT',
    prod_a_title: '炭化ケイ素保護管',
    prod_a_desc: '高純度炭化ケイ素（SiC）製造、耐熱温度1600°C超、優れた耐腐食性。半導体製造炉管、アルミ溶解など高温工業用途に広く使用。',
    prod_a_mat: '高純度 SiC', prod_a_app: '半導体 / 鋳造業',
    prod_b_title: '黒鉛脱ガス管',
    prod_b_desc: '高純度黒鉛素材、アルミニウム液精錬脱ガス専用設計。溶解炉で水素・不純物を効果的に除去し、鋳造品質を向上。超長寿命で交換頻度とコストを大幅削減。',
    prod_b_use: 'アルミ液脱ガス精錬', prod_b_merit: '長寿命・低消耗',
    spec_temp: '耐熱温度', spec_mat: '材質', spec_app: '用途',
    spec_purity: '純度', spec_use: '使用目的', spec_merit: '優位性',
    spec_type: 'タイプ', spec_heat: '温度', spec_spec: '仕様', spec_model: '型番', spec_measure: '測定範囲',
    cta_spec: '仕様を見る',

    srv_title: '総合自動化サービス',
    srv_lead: '6つのサービスで計画から納品まで、ワンストップで自動化ニーズに対応',
    srv_1_title: 'デジタルツイン自動化設計', srv_1_desc: '仮想ライン検証でリスク低減',
    srv_2_title: 'ロボットアーム応用',       srv_2_desc: '搬送・溶接・組立統合、経路計画',
    srv_3_title: '単機自動化設計製造',       srv_3_desc: '要件→設計→製造→調整、一貫対応',
    srv_4_title: '画像検査',                 srv_4_desc: '産業カメラ + AI欠陥検出・寸法測定',
    srv_5_title: '治具設計製造',             srv_5_desc: '高精度治具で品質一貫性向上',
    srv_6_title: '設備インテリジェント化',   srv_6_desc: '既存設備を PLC / HMI / IoT へアップグレード',
    cta_learn: '詳しく見る', cta_all_services: 'すべてのサービスを見る',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    tech_title: 'トヨタ哲学 × 精密製造の応用',
    tech_tag_semi: '半導体プロセス', tech_tag_ev: '電気自動車', tech_tag_robot: 'ヒューマノイドロボット',
    tech_1_title: '精密製造における材料の鍵',
    tech_1_desc: 'SiC保護管は半導体高温プロセスで重要な役割を担い、安定した熱環境と腐食防護を提供します。',
    tech_2_title: 'EV電池生産の熱管理革新',
    tech_2_desc: 'EV電池セル製造には精密な熱管理が必要です。欣晨のヒーターとセンサー素子が生産一貫性を確保します。',
    tech_3_title: 'ロボット関節精密加工',
    tech_3_desc: 'ヒューマノイドロボット関節には高精度製造が必要です。欣晨の治具設計が精密ソリューションを提供します。',
    cta_read_more: '続きを読む', cta_view_all_tech: 'すべての技術テーマを見る',

    cta_banner_title: 'トヨタ哲学で生産ラインを最適化する準備はできましたか？',
    cta_banner_desc: '現場の課題をお聞かせください。欣晨工業のエンジニアが現地を訪問し、改善精神で最適なソリューションを設計します。',
    cta_contact_now: 'お問い合わせ',

    footer_nav_title: 'クイックナビ', footer_contact_title: '連絡先',
    footer_years: '51年の製造経験',
    footer_addr: '桃園市大園区中正東路三段490号',
    footer_tel: 'Tel：03-381-4497', footer_fax: 'Fax：03-381-4536',
    footer_tagline_1: '精密が駆動する', footer_tagline_2: '未来を創る',
    footer_est: 'Est. 1975 · 製造51年の歴史',

    about_banner_title: '会社概要',
    about_banner_lead: '51年の精密製造経験、桃園を拠点に台湾全土の産業顧客にサービスを提供。技術・品質・サービスを事業の礎に。',
    about_our_title: '私たちについて',
    about_desc_1: '欣晨工業有限公司は1975年に創業し、桃園市大園工業区に位置しています。半世紀の積み重ねにより、初期の産業用消耗品サプライヤーから、自動化設備の設計・製造・統合・アフターサービスを含む総合製造パートナーへと発展しました。',
    about_desc_2: '主な製品は炭化ケイ素保護管、黒鉛脱ガス管、ヒーター、熱電対などの高温工業用消耗品です。また、デジタルツイン計画、ロボットアーム応用、画像検査などのインテリジェント自動化サービス分野にも継続的に拡大しています。',
    about_desc_3: '現在に至るまで、欣晨工業はトヨタ生産方式（TPS）の改善精神と精密加工技術を基盤に、半導体・鋳造・電気自動車・精密機械などの産業に向けて、継続的に進化する製造ソリューションを提供し続けています。',
    about_history_eyebrow: '歩みの歴史',
    about_tl_1_title: '会社設立', about_tl_1_desc: '桃園大園に設立。高温工業用消耗品の製造・供給に特化し、地元製造業顧客にサービスを提供。',
    about_tl_2_title: '製品ライン拡大', about_tl_2_desc: '炭化ケイ素保護管と黒鉛脱ガス管の生産技術を導入。サービス対象を半導体・鋳造業へと拡大。',
    about_tl_3_title: '工場拡張', about_tl_3_desc: 'ヒーターと熱電対の生産ラインを追加し、工場面積を拡張。年間生産能力と品質管理能力を向上。',
    about_tl_4_title: '自動化への転換', about_tl_4_desc: '自動化設備の設計・製造に進出。ロボットアーム統合、単機自動化、画像検査サービスを提供。',
    about_tl_5_title: 'インテリジェント化', about_tl_5_desc: 'デジタルツイン技術を導入し、既存設備のインテリジェント化を推進。工業4.0統合サービス会社へ。',
    about_phil_title: '経営理念',
    about_phil_lead: '三大理念が欣晨の51年の安定した成長を支え、すべての顧客へのサービスにおける約束でもあります。',
    about_phil_1_title: '精密製造', about_phil_1_desc: '51年の製造技術の蓄積と厳格な品質管理体制により、すべての部品が基準を正確に満たします。原材料の入荷から完成品の出荷まで、全工程の品質追跡で安定した稼働を確保します。',
    about_phil_2_title: 'カスタムサービス', about_phil_2_desc: '要件分析から機構設計、生産・納品まで、一対一のカスタムサービスを提供。顧客の生産現場を深く理解し、最適な自動化ソリューションをお届けします。',
    about_phil_3_title: '技術サポート', about_phil_3_desc: '専門エンジニアチームによる現場調整と技術研修、充実したアフターサービス体制。納品後も継続的に技術支援を提供し、設備の長期安定稼働を保証します。',
    about_team_title: '経営チーム',
    about_team_lead: '豊富な業界経験を持つプロフェッショナルチームが、技術革新とサービス向上を継続的に推進します。',
    about_team_1_role: '総経理', about_team_1_desc: '会社全体の戦略立案と運営管理を担当。チームを率いて継続的に革新し、自動化設備製造分野に30年以上従事しています。',
    about_team_2_role: '技術長', about_team_2_desc: '研究開発部門を主導。高温材料工学と自動化機構設計を専門とし、半導体プロセス設備開発の豊富な経験を持ちます。',
    about_team_3_role: '営業部長', about_team_3_desc: '営業開発と顧客関係管理を統括。顧客ニーズを深く理解し、各産業の顧客に最適な自動化ソリューションを提供します。',
    about_cta_title: '共に精密な未来を創りましょう',
    about_cta_desc: '製品の見積もり、技術相談、プロジェクト協力など、欣晨工業の専門チームへお気軽にご連絡ください。',
    about_cta_btn: 'お問い合わせ',

    pp_banner_title: '製品情報',
    pp_banner_lead: '6種の精密高温工業用消耗品。半導体・鋳造・電気自動車などの先端プロセスに対応し、すべて仕様のカスタマイズが可能です。',
    pp_overview_title: '6つの製品ライン', pp_overview_lead: 'すべての製品は厳格な品質管理を経ており、高温・腐食性・精密工業環境に対応しています。',
    pp_p1_tag: '射出成形消耗品', pp_p1_title: '一体型バレル',
    pp_p1_desc: '高品質合金鋼の精密加工による一体成型設計で、継ぎ目からの漏れリスクを排除し、射出成形機の安定性と寿命を向上させます。',
    pp_p1_s1: '材質：窒化鋼', pp_p1_s2: '硬度：HRC 60–65', pp_p1_s3: 'カスタムサイズ対応', pp_p1_btn: '見積依頼',
    pp_p2_tag: '高温プロセス消耗品', pp_p2_title: '炭化ケイ素保護管',
    pp_p2_desc: '高純度炭化ケイ素（SiC）製。耐熱温度1600°C超え、優れた耐食性。半導体炉管やアルミ溶解などの高温工業用途に広く使用されています。',
    pp_p2_s1: '耐熱：＞1600°C', pp_p2_s2: '材質：高純度 SiC', pp_p2_s3: '耐熱衝撃・耐食性', pp_p2_btn: '見積依頼',
    pp_p3_tag: '窯炉工業消耗品', pp_p3_title: '耐火材料',
    pp_p3_desc: '高温安定性に優れた耐火レンガ、耐火モルタル、定形耐火製品。各種冶金炉、工業窯炉および高温プロセス設備の炉壁構築・補修に適しています。',
    pp_p3_s1: '耐熱：材質により最大1800°C', pp_p3_s2: '高圧縮強度・低熱伝導', pp_p3_s3: '多種材質・規格から選択可能', pp_p3_btn: '見積依頼',
    pp_p4_tag: 'アルミニウム精錬消耗品', pp_p4_title: '黒鉛脱ガス管',
    pp_p4_desc: '高純度黒鉛素材、アルミニウム液の精錬脱ガス専用設計。溶融アルミ液中の水素や不純物を効果的に除去し、鋳造品質を向上。超長寿命でコスト削減。',
    pp_p4_s1: '純度：＞99.9% 高純度黒鉛', pp_p4_s2: '耐熱：＞900°C・耐酸化', pp_p4_s3: '径・長さのカスタマイズ可', pp_p4_btn: '見積依頼',
    pp_p5_tag: '精密温度制御部品', pp_p5_title: 'ヒーター',
    pp_p5_desc: '電熱管、セラミックヒーター、赤外線ヒーターなど多種類。工業加熱プロセス、金型予熱、半導体設備などに対応し、精確で安定した加熱制御を提供します。',
    pp_p5_s1: '耐熱：タイプにより最大1200°C', pp_p5_s2: '多種出力規格（50W–10kW）', pp_p5_s3: 'カスタム形状・配線方式', pp_p5_btn: '見積依頼',
    pp_p6_tag: '精密計測部品', pp_p6_title: '熱電対',
    pp_p6_desc: 'K型・J型・N型・S型・R型・B型など多種類の熱電対を提供。各種保護管素材と組み合わせ、溶炉温度測定・半導体製造温度管理・食品加工など幅広い用途に対応。',
    pp_p6_s1: '測温範囲：−200°C ～ +1800°C', pp_p6_s2: '多種型番・保護管素材', pp_p6_s3: 'IEC / JIS 規格適合', pp_p6_btn: '見積依頼',
    pp_qa_title: '品質保証', pp_qa_lead: 'すべての製品は厳格な品質検査プロセスを経て、顧客仕様と国際基準への適合を確認しています。',
    pp_qa_1_title: '厳格な品質管理', pp_qa_1_desc: '原材料の入荷から完成品の出荷まで、全工程品質追跡でゼロ不良を目指します。',
    pp_qa_2_title: 'カスタム仕様', pp_qa_2_desc: 'サイズ・材質・仕様のカスタマイズサービスを提供。特殊プロセスの独自ニーズに対応します。',
    pp_qa_3_title: '迅速納期', pp_qa_3_desc: '充実した在庫管理と生産スケジュールにより、標準品の迅速出荷とカスタム品の納期遵守を実現。',
    pp_cta_title: '仕様が見当たらない場合は？',
    pp_cta_desc: '欣晨工業は完全カスタムサービスを提供します。ニーズをお聞かせください。技術チームが最適な製品仕様を設計します。',
    pp_cta_btn: '今すぐお問い合わせ',

    srv_page_title: 'サービス項目',
    srv_page_lead: '6つの自動化サービス。デジタル計画からロボットアーム統合・画像検査・設備インテリジェント化まで、製造ニーズをワンストップで満たします。',
    srv_d1_num: 'SERVICE 01', srv_d1_tag: 'デジタルツイン', srv_d1_title: 'デジタルツイン自動化設計',
    srv_d1_desc: '実体構築前にデジタルツイン技術で仮想環境において生産ラインの運用を完全シミュレーション。3Dモデルと動的シミュレーションで設計上の欠陥を事前に発見し、建設リスクと修正コストを大幅に削減します。',
    srv_d1_p1: '仮想ライン配置計画と動作シミュレーション', srv_d1_p2: '設備干渉チェックと安全評価',
    srv_d1_p3: 'タクトタイム分析と最適化', srv_d1_p4: '3D設計図面と技術仕様書の提供', srv_d1_btn: 'このサービスについて相談',
    srv_d2_num: 'SERVICE 02', srv_d2_tag: 'ロボット統合', srv_d2_title: 'ロボットアーム応用',
    srv_d2_desc: '主要ブランドの産業用ロボット（FANUC・ABB・KUKA・Yaskawa等）を統合し、搬送・溶接・組立・塗布など多様な用途に対応。エンドエフェクター設計と経路計画で高効率フレキシブル生産ラインを構築します。',
    srv_d2_p1: 'マルチブランドロボット選定と導入', srv_d2_p2: 'エンドエフェクター（グリッパー/ツール）カスタム設計',
    srv_d2_p3: 'オフラインプログラミングと経路最適化', srv_d2_p4: '協働ロボット（Cobot）安全システム統合', srv_d2_btn: 'このサービスについて相談',
    srv_d3_num: 'SERVICE 03', srv_d3_tag: 'カスタム自動化', srv_d3_title: '単機自動化設計製造',
    srv_d3_desc: '顧客要件分析・機構概念設計・工程図面作成・部品加工製造から、完成機組立・プログラム作成・現場調整まで、完全一貫の自動化設備設計製造サービスを提供します。',
    srv_d3_p1: '要件分析と実現可能性評価', srv_d3_p2: '機構設計と3Dモデリング（SolidWorks / Solid Edge）',
    srv_d3_p3: 'PLC / HMI プログラム開発（三菱 / シーメンス）', srv_d3_p4: '完成機テスト・現場設置・人員研修', srv_d3_btn: 'このサービスについて相談',
    srv_d4_num: 'SERVICE 04', srv_d4_tag: '画像検査', srv_d4_title: '視覚検査',
    srv_d4_desc: '産業用カメラ・高精度レンズ・AI画像解析を組み合わせ、製品外観の欠陥検出・寸法測定・バーコード識別・位置誘導を実現。目視検査に代わり、検査効率と一貫性を大幅に向上させます。',
    srv_d4_p1: '外観欠陥検出（傷・汚れ・欠け）', srv_d4_p2: '高精度寸法測定（±0.01mm）',
    srv_d4_p3: 'QR コード / バーコード / OCR 識別', srv_d4_p4: '視覚誘導ロボットアームによる位置決め・ピック', srv_d4_btn: 'このサービスについて相談',
    srv_d5_num: 'SERVICE 05', srv_d5_tag: '治具設計', srv_d5_title: '治具設計製造',
    srv_d5_desc: '自動化組立・加工・検査プロセス向けの高精度工作治具・固定具を設計・製造。精確な位置決めとクランプ設計により、すべての製品の加工位置の一貫性を確保し、良品率を向上させます。',
    srv_d5_p1: '機械加工治具・溶接治具・組立工具', srv_d5_p2: '材質：アルミ合金・工具鋼・ステンレス',
    srv_d5_p3: '繰り返し位置決め精度：±0.02mm', srv_d5_p4: 'クイックチェンジ設計で段取り替え時間を短縮', srv_d5_btn: 'このサービスについて相談',
    srv_d6_num: 'SERVICE 06', srv_d6_tag: 'スマートアップグレード', srv_d6_title: '設備インテリジェント化',
    srv_d6_desc: '既存の従来型設備にPLC・HMI・IoTモジュールを追加し、遠隔監視・データ収集・予知保全機能を実現。設備を全面更新することなく、最小限の投資で生産ラインのデジタル化レベルを向上させます。',
    srv_d6_p1: 'PLCコントローラーアップグレード（三菱 iQ-F / iQ-R）', srv_d6_p2: 'HMIタッチパネル設置（Pro-face / Weintek）',
    srv_d6_p3: 'IoTデータ収集とクラウド監視ダッシュボード', srv_d6_p4: 'OEE設備効率分析と異常通報システム', srv_d6_btn: 'このサービスについて相談',
    srv_cta_title: '自動化プロジェクトを始めませんか？',
    srv_cta_desc: '新規ライン計画から既存設備アップグレードまで、欣晨工業のエンジニアチームが最適なソリューションを提供します。',
    srv_cta_btn: '今すぐ相談する',

    tech_page_title: '新技術の展望',
    tech_page_lead: '半導体プロセスからヒューマノイドロボットまで、欣晨の精密部品・耐高温材料の6大先端分野における重要な応用と技術貢献を探ります。',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: '半導体', tech_d1_title: '半導体製造プロセス',
    tech_d1_desc: '半導体ウェーハ製造は超高温・強腐食環境での精密な制御が必要です。欣晨のSiC保護管と黒鉛脱ガス管は、優れた耐熱衝撃性と化学的不活性により、拡散炉管・結晶成長装置などの核心製造設備の重要消耗品となっています。',
    tech_d1_p1: 'SiC保護管：耐熱1600°C、耐酸化・耐食性', tech_d1_p2: '黒鉛脱ガス管：溶融アルミ液中の水素不純物を効果的に除去',
    tech_d1_p3: '一体型バレル：溶融シリコン搬送時の純度・無汚染を確保', tech_d1_p4: 'カスタム寸法、各種結晶成長炉とPECVD設備に適合', tech_d1_btn: '応用ソリューションについて相談',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: '電気自動車', tech_d2_title: '電気自動車（EV）',
    tech_d2_desc: 'EV電池モジュール・モーター・パワーエレクトロニクス部品は熱管理に厳しい要件があります。欣晨の耐火材料・高精度セラミック部品は、電池パック構造保護・モーターステーター絶縁・鋳造工場でのアルミ合金モーターシェル製造に広く使用されています。',
    tech_d2_p1: '電池モジュール防火断熱板：難燃・耐高温構造保護', tech_d2_p2: 'アルミ鋳造プロセス保護管：モーターシェル製造に必須',
    tech_d2_p3: 'セラミック熱電対：モーター動作温度の精確な監視', tech_d2_p4: '耐高温絶縁材料：パワーモジュール（IGBT/SiC MOSFET）対応', tech_d2_btn: '応用ソリューションについて相談',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'シリコンフォトニクス', tech_d3_title: 'シリコンフォトニクス',
    tech_d3_desc: 'シリコンフォトニクス技術は光学部品をシリコン基板上に統合し、高速光通信とAI加速演算を実現します。欣晨は光子チップ封止プロセス向けの高精度セラミック治具・耐高温治具・プロセス保護部品を提供します。',
    tech_d3_p1: '高精度セラミック位置決め治具：光ファイバーアレイ位置合わせ', tech_d3_p2: '耐高温プロセスキャリア：ボンディングプロセスの安定した搭載',
    tech_d3_p3: 'アルミナセラミック断熱板：アニール炉の均一熱分布', tech_d3_p4: 'カスタム仕様、ファウンドリのプロセスノード要件に対応', tech_d3_btn: '応用ソリューションについて相談',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'ヒューマノイドロボット', tech_d4_title: 'ヒューマノイドロボット',
    tech_d4_desc: 'ヒューマノイドロボットの関節駆動・エンドエフェクター・センシングシステムは軽量化と高精度を兼ね備えた部品製造を必要とします。欣晨は51年の精密加工経験を活かし、アルミ合金構造部品・精密駆動スリーブ・耐摩耗セラミック部品を提供します。',
    tech_d4_p1: '関節駆動精密スリーブ：動作繰り返し位置決め精度を維持', tech_d4_p2: '軽量アルミ合金構造部品：本体重量を削減し機敏性を向上',
    tech_d4_p3: '耐摩耗セラミックガイド部品：関節寿命を延長', tech_d4_p4: '高精度公差管理：±0.01mm 級加工能力', tech_d4_btn: '応用ソリューションについて相談',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: '量子コンピューター', tech_d5_title: '量子コンピューター',
    tech_d5_desc: '量子コンピューターの希釈冷凍機は量子ビットを絶対零度近く（15 mK）に保つ必要があり、部品の熱伝導性・電磁障害防護・超精密加工に極限の要求があります。欣晨は低温環境対応の高純度無酸素銅部品と精密セラミック断熱部品を提供します。',
    tech_d5_p1: '高純度無酸素銅（OFC）精密部品：優れた熱伝導・電気伝導性', tech_d5_p2: 'セラミック断熱構造部品：低温環境での熱絶縁設計',
    tech_d5_p3: '超精密加工：表面粗さ Ra ≤ 0.4μm', tech_d5_p4: '厳格な清潔度管理：量子状態への干渉汚染を回避', tech_d5_btn: '応用ソリューションについて相談',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / ドローン', tech_d6_title: '無人機（UAV/ドローン）',
    tech_d6_desc: 'ドローンは極限の軽量化と構造強度のバランスを追求し、モーターマウント・駆動軸・ジンバルフレームなどの重要部品は精密加工と厳格な品質管理が必要です。欣晨はドローンメーカー向けに高強度アルミ合金機構部品・炭素繊維複合材インサート・カスタム工作治具を提供します。',
    tech_d6_p1: '航空アルミ合金（7075-T6）軽量化構造部品', tech_d6_p2: 'モーターマウント：精密孔位でモーター同心度を確保',
    tech_d6_p3: '炭素繊維複合材料埋込み式金属インサート', tech_d6_p4: '迅速試作と小ロット量産の柔軟なサービス', tech_d6_btn: '応用ソリューションについて相談',
    tech_cta_title: 'あなたの分野での精密材料応用を探りませんか？',
    tech_cta_desc: '欣晨工業の技術チームは、各先端技術分野のメーカーと材料ソリューションを共に探求し、技術の限界を共に押し広げることを歓迎します。',
    tech_cta_btn: '技術チームに今すぐ連絡',

    career_page_title: '採用情報',
    career_page_lead: '欣晨工業に加わり、51年の精密製造技術を受け継ぎ、自動化と新材料時代の機会と挑戦を共に迎えましょう。',
    career_apply_title: '応募方法',
    career_apply_lead: '欣晨工業への参加を志す方は、履歴書と自己紹介文を以下のメールアドレスへご送付ください。人事チームが資料受領後3営業日以内にご連絡します。',
    career_apply_label: 'メール応募',
    career_apply_note: '件名に「応募職位名＋氏名」を記載し、完全な履歴書と自己紹介文を添付してください',
    career_jobs_title: '現在の求人',
    career_j1_tag: '製造エンジニアリング', career_j1_title: '精密機械加工員',
    career_j1_p1: 'CNC旋盤・フライス盤などの精密加工設備を操作', career_j1_p2: '工程図面に基づき部品加工と品質自主検査を実施',
    career_j1_p3: '学歴：高校卒業以上、機械系学科優遇', career_j1_p4: '加工経験者優先採用、訓練生も歓迎', career_j1_btn: '今すぐ応募',
    career_j2_tag: '営業・マーケティング', career_j2_title: '営業エンジニア',
    career_j2_p1: '国内外の顧客関係を開拓・維持', career_j2_p2: '顧客の技術ニーズを解読し材料ソリューションを提供',
    career_j2_p3: '学歴：短大卒以上、工学・化学系専攻優遇', career_j2_p4: '日本語または英語のコミュニケーション能力者優先', career_j2_btn: '今すぐ応募',
    career_j3_tag: '自動化技術', career_j3_title: '自動化設備エンジニア',
    career_j3_p1: '自動化生産設備の計画・設計・統合', career_j3_p2: 'PLCプログラミング（三菱 iQ-F / iQ-R）とHMI統合',
    career_j3_p3: '学歴：短大卒以上、電気・機電・自動制御系専攻', career_j3_p4: 'ロボットアーム統合または視覚システム経験者優遇', career_j3_btn: '今すぐ応募',
    career_ben_title: '従業員福利厚生',
    career_ben_lead: '欣晨工業はすべての従業員の職場の質とキャリア発展を重視し、充実した福利厚生制度と成長環境を提供します。',
    career_ben_1_title: '労働保険', career_ben_1_desc: '法律に基づき労働保険に加入。労災・傷病・老齢・失業等の各種給付を保障し、職場の安全を守ります。',
    career_ben_2_title: '健康保険', career_ben_2_desc: '全民健康保険に加入。従業員とその家族に包括的な医療保障を提供し、全員の健康を見守ります。',
    career_ben_3_title: '皆勤手当', career_ben_3_desc: '当月皆勤の従業員に皆勤手当を支給。責任感ある勤務態度と真摯な仕事ぶりを称えます。',
    career_ben_4_title: '節季手当', career_ben_4_desc: '旧正月・端午節・中秋節の三大節に賞与を支給。伝統的な佳節の喜びと温かさを従業員と分かち合います。',
    career_ben_5_title: '誕生日祝い金', career_ben_5_desc: '誕生日に祝い金を贈呈。会社が各メンバーを大切にし、心からの祝福を伝えます。',
    career_ben_6_title: '年末賞与', career_ben_6_desc: '年間業績に応じた年末賞与を支給。一年間の貢献を称え、会社の成長の成果を共に分かち合います。',
    career_ben_7_title: '団体保険', career_ben_7_desc: '従業員団体保険を追加提供。傷害・医療保障をカバーし、より包括的な安全保障を提供します。',
    career_ben_8_title: '国内旅行', career_ben_8_desc: '定期的に国内社員旅行を実施。リフレッシュし仲間の絆を深め、結束力の強い職場チームを育てます。',
    career_ben_9_title: '忘年会', career_ben_9_desc: '年末に忘年会を開催。一年間の労をねぎらい、豊かな収穫を共に祝い、新たな年を迎えます。',
    career_cta_title: '欣晨に加わる準備はできましたか？',
    career_cta_desc: '履歴書を hc3814497@gmail.com へお送りください。欣晨の次の50年を共に創ることを楽しみにしています。',
    career_cta_btn: '今すぐ履歴書を送る',

    contact_page_title: 'お問い合わせ',
    contact_page_lead: '製品の見積もり、技術協力、サービス交渉など、以下の方法で欣晨工業へご連絡ください。1〜2営業日以内にご回答します。',
    contact_info_title: '会社情報',
    contact_label_addr: '住所', contact_addr_value: '桃園市大園区中正東路三段490号',
    contact_label_tel: '電話', contact_label_email: 'メール', contact_label_fax: 'FAX',
    contact_label_fb: 'Facebook', contact_fb_value: '欣晨工業有限公司（フェイスブック）',
    contact_hours_title: '営業時間',
    contact_hours_weekday: '月曜〜金曜　08:00 – 17:30',
    contact_hours_weekend: '土曜・日曜　定休日',
    contact_form_title: 'オンライン問い合わせ',
    contact_form_lead: '以下の情報をご記入ください。1〜2営業日以内にご連絡します。',
    contact_form_name_label: 'お名前', contact_form_company_label: '会社 / 組織名',
    contact_form_tel_label: '電話番号', contact_form_email_label: 'メールアドレス', contact_form_msg_label: 'お問い合わせ内容',
    contact_form_name_ph: 'お名前をご入力ください', contact_form_company_ph: '会社名または組織名をご入力ください',
    contact_form_tel_ph: '例：03-1234-5678', contact_form_email_ph: 'example@company.com',
    contact_form_msg_ph: 'ご要望をご記入ください（例：製品仕様のお問い合わせ、見積依頼、技術提携など）',
    contact_form_submit: '送信する',
  },

  en: {
    nav_home: 'Home', nav_about: 'About Us', nav_products: 'Products',
    nav_services: 'Services', nav_tech: 'Technology', nav_careers: 'Careers',
    nav_contact: 'Contact',

    hero_badge: 'Precision Automation Solutions · Since 1975',
    hero_h1_line1: 'Precision Drives,', hero_h1_line2: 'Future Forged',
    hero_h2: 'Precision automation rooted in Kaizen, Just-In-Time, and Jidoka.',
    cta_products: 'View Products', cta_contact_ask: 'Contact Us',
    metric_years: 'Years Experience', metric_products: 'Product Lines',
    metric_services: 'Service Areas', scroll: 'SCROLL',

    adv_title: 'Toyota Philosophy Driving Manufacturing Excellence',
    adv_lead: 'Hsin-Chan Industrial Co., Ltd. is built on the three pillars of the Toyota Production System (TPS) — delivering continuous improvement and zero-waste manufacturing value to every client.',
    adv_1_title: 'Just-In-Time',
    adv_1_desc: 'The right parts, at the right time, in the right quantity. Hsin-Chan plans every automation project with the JIT spirit — eliminating waiting waste and keeping your production line running smoothly.',
    adv_2_title: 'Kaizen',
    adv_2_desc: 'Improve a little more than yesterday, every single day. Our engineers have internalized "there is no best, only better" — from design drawings to on-site commissioning, never satisfied with "good enough."',
    adv_3_title: 'Jidoka',
    adv_3_desc: 'Equipment that automatically detects abnormalities and stops, preventing defects from reaching the next process. Our machine vision and automation solutions give your production line the intelligence to detect, judge, and stop.',

    stat_years_label: 'Years of Manufacturing', stat_products_label: 'Product Lines',
    stat_products_sub: 'High-Temp Industrial', stat_services_label: 'Service Areas',
    stat_services_sub: 'Automation Integration', stat_jobs_label: 'Open Positions',
    stat_jobs_sub: 'Engineering Roles',

    prod_eyebrow: 'FEATURED PRODUCT',
    prod_a_title: 'Silicon Carbide Protection Tube',
    prod_a_desc: 'Manufactured from high-purity silicon carbide (SiC), rated above 1600°C with excellent corrosion resistance. Widely used in semiconductor process furnace tubes, aluminum smelting, and high-temperature industrial applications.',
    prod_a_mat: 'High-purity SiC', prod_a_app: 'Semiconductor / Foundry',
    prod_b_title: 'Graphite Degassing Tube',
    prod_b_desc: 'High-purity graphite material designed for aluminum melt refining and degassing. Effectively removes hydrogen and impurities in melting furnaces to improve casting quality. Extended service life significantly reduces replacement frequency and downtime costs.',
    prod_b_use: 'Aluminum Melt Refining', prod_b_merit: 'Long Life, Low Wear',
    spec_temp: 'Max Temp', spec_mat: 'Material', spec_app: 'Application',
    spec_purity: 'Purity', spec_use: 'Purpose', spec_merit: 'Advantage',
    spec_type: 'Type', spec_heat: 'Temperature', spec_spec: 'Spec', spec_model: 'Model', spec_measure: 'Measurement',
    cta_spec: 'View Specs',

    srv_title: 'Full-Spectrum Automation Services',
    srv_lead: 'Six services from planning to handover — your one-stop automation partner',
    srv_1_title: 'Digital Twin Automation Planning', srv_1_desc: 'Virtual line validation to reduce construction risk',
    srv_2_title: 'Robotic Arm Applications',         srv_2_desc: 'Handling, welding, assembly integration with path planning',
    srv_3_title: 'Custom Machine Design & Build',    srv_3_desc: 'Requirements → Design → Build → Commission, end-to-end',
    srv_4_title: 'Machine Vision Inspection',        srv_4_desc: 'Industrial cameras + AI defect detection & measurement',
    srv_5_title: 'Fixture & Jig Design',             srv_5_desc: 'High-precision fixtures for consistent quality',
    srv_6_title: 'Equipment Intelligence Upgrade',   srv_6_desc: 'Retrofit existing equipment with PLC / HMI / IoT',
    cta_learn: 'Learn More', cta_all_services: 'View All Services',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    tech_title: 'Toyota Philosophy × Precision Manufacturing',
    tech_tag_semi: 'Semiconductor', tech_tag_ev: 'Electric Vehicle', tech_tag_robot: 'Humanoid Robotics',
    tech_1_title: 'Material Science in Precision Processes',
    tech_1_desc: 'SiC protection tubes play a critical role in high-temperature semiconductor processes, providing stable thermal environments and corrosion protection.',
    tech_2_title: 'Thermal Management in EV Battery Production',
    tech_2_desc: 'EV cell manufacturing demands precise thermal management. Hsin-Chan Industrial Co., Ltd. heaters and sensing elements ensure production consistency.',
    tech_3_title: 'Precision Machining for Robot Joints',
    tech_3_desc: "Humanoid robot joints require ultra-high precision manufacturing. Hsin-Chan Industrial Co., Ltd.'s fixture design provides accurate solutions for this challenge.",
    cta_read_more: 'Read More', cta_view_all_tech: 'View All Topics',

    cta_banner_title: 'Ready to Optimize Your Production Line with Toyota Philosophy?',
    cta_banner_desc: 'Tell us your on-site challenges. Our engineers will visit your facility and design the optimal solution with the spirit of Kaizen.',
    cta_contact_now: 'Contact Us Now',

    footer_nav_title: 'Quick Navigation', footer_contact_title: 'Contact Info',
    footer_years: '51 Years of Manufacturing',
    footer_addr: '490, Sec. 3, Zhongzheng E. Rd., Dayuan Dist., Taoyuan City, Taiwan',
    footer_tel: 'Tel: 03-381-4497', footer_fax: 'Fax: 03-381-4536',
    footer_tagline_1: 'Precision Drives', footer_tagline_2: 'Future Forged',
    footer_est: 'Est. 1975 · 51 Years of Manufacturing',

    about_banner_title: 'About Us',
    about_banner_lead: '51 years of precision manufacturing expertise, rooted in Taoyuan, serving industrial clients across Taiwan. Built on technology, quality, and service.',
    about_our_title: 'About Us',
    about_desc_1: 'Founded in 1975, Hsin-Chan Industrial Co., Ltd. is located in the Dayuan Industrial District, Taoyuan. Over half a century, we have evolved from an industrial consumables supplier into a full-service manufacturing partner encompassing automation equipment design, manufacturing, integration, and after-sales support.',
    about_desc_2: 'Our core products include silicon carbide protection tubes, graphite degassing tubes, heaters, and thermocouples — high-temperature industrial consumables. We continue expanding into intelligent automation services including digital twin planning, robotic arm applications, and machine vision inspection.',
    about_desc_3: 'To this day, Hsin-Chan Industrial continues to evolve, grounded in the Toyota Production System (TPS) spirit of Kaizen and precision manufacturing — delivering continuously improving solutions to semiconductor, foundry, EV, and precision machinery industries.',
    about_history_eyebrow: 'Our History',
    about_tl_1_title: 'Founded', about_tl_1_desc: 'Established in Dayuan, Taoyuan. Focused on high-temperature industrial consumables manufacturing and supply for local manufacturers.',
    about_tl_2_title: 'Product Expansion', about_tl_2_desc: 'Introduced SiC protection tube and graphite degassing tube production. Extended service scope to semiconductor and foundry industries.',
    about_tl_3_title: 'Factory Expansion', about_tl_3_desc: 'Added heater and thermocouple production lines, expanded factory floor space, increasing annual capacity and quality control capabilities.',
    about_tl_4_title: 'Automation Transition', about_tl_4_desc: 'Entered automation equipment design and manufacturing. Offering robotic arm integration, standalone automation, and machine vision inspection.',
    about_tl_5_title: 'Smart Upgrade', about_tl_5_desc: 'Introduced digital twin technology, driving existing equipment intelligence. Moving toward Industry 4.0 integrated service provider.',
    about_phil_title: 'Our Philosophy',
    about_phil_lead: 'Three core principles have driven Hsin-Chan Industrial Co., Ltd.\'s steady 51-year growth, and represent our commitment to every client we serve.',
    about_phil_1_title: 'Precision Manufacturing', about_phil_1_desc: '51 years of accumulated manufacturing expertise and rigorous quality management ensure every component meets exact specifications. Full traceability from raw materials to finished products guarantees reliable equipment performance.',
    about_phil_2_title: 'Custom Solutions', about_phil_2_desc: 'From requirements analysis and mechanism design to production and delivery, we provide one-on-one custom service. We deeply understand each client\'s production environment to deliver the most suitable automation solution.',
    about_phil_3_title: 'Technical Support', about_phil_3_desc: 'Expert engineering teams provide on-site commissioning and technical training, backed by comprehensive after-sales maintenance. Ongoing technical consultation after delivery ensures long-term, stable, high-efficiency equipment operation.',
    about_team_title: 'Leadership Team',
    about_team_lead: 'A professional team with extensive industry experience, continuously driving technological innovation and service advancement.',
    about_team_1_role: 'General Manager', about_team_1_desc: 'Responsible for overall corporate strategy and operational management, leading the team in continuous innovation with over 30 years in automation equipment manufacturing.',
    about_team_2_role: 'Chief Engineer', about_team_2_desc: 'Leads the R&D department, specializing in high-temperature material engineering and automation mechanism design, with extensive experience in semiconductor process equipment development.',
    about_team_3_role: 'Sales Director', about_team_3_desc: 'Oversees business development and client relationship management, deeply understanding client needs to provide the most suitable automation solutions across industries.',
    about_cta_title: 'Partner With Us for a Precision Future',
    about_cta_desc: 'Whether for product quotations, technical consultation, or project collaboration, contact Hsin-Chan Industrial Co., Ltd.\'s expert team.',
    about_cta_btn: 'Contact Us',

    pp_banner_title: 'Products',
    pp_banner_lead: 'Six precision, high-temperature industrial consumables for semiconductor, foundry, EV, and advanced manufacturing processes — all available in custom specifications.',
    pp_overview_title: 'Six Product Lines', pp_overview_lead: 'All products pass rigorous quality control and are designed for high-temperature, corrosive, and precision industrial environments.',
    pp_p1_tag: 'Injection Molding Consumables', pp_p1_title: 'One-Piece Barrel',
    pp_p1_desc: 'Precision-machined from high-quality alloy steel, the one-piece design eliminates seam leakage risk and extends injection molding machine stability and service life.',
    pp_p1_s1: 'Material: Nitrided Steel', pp_p1_s2: 'Hardness: HRC 60–65', pp_p1_s3: 'Custom dimensions available', pp_p1_btn: 'Request Quote',
    pp_p2_tag: 'High-Temp Process Consumables', pp_p2_title: 'SiC Protection Tube',
    pp_p2_desc: 'Made from high-purity silicon carbide (SiC), rated above 1600°C with excellent corrosion resistance. Widely used in semiconductor furnace tubes and aluminum smelting.',
    pp_p2_s1: 'Max Temp: >1600°C', pp_p2_s2: 'Material: High-purity SiC', pp_p2_s3: 'Thermal shock & corrosion resistant', pp_p2_btn: 'Request Quote',
    pp_p3_tag: 'Kiln Industrial Consumables', pp_p3_title: 'Refractory Materials',
    pp_p3_desc: 'High-temperature stable refractory bricks, mortars, and shaped refractory products for furnace lining construction and repair in metallurgical and industrial kilns.',
    pp_p3_s1: 'Max Temp: up to 1800°C by grade', pp_p3_s2: 'High compressive strength, low thermal conductivity', pp_p3_s3: 'Multiple grades and sizes available', pp_p3_btn: 'Request Quote',
    pp_p4_tag: 'Aluminum Refining Consumables', pp_p4_title: 'Graphite Degassing Tube',
    pp_p4_desc: 'High-purity graphite designed for aluminum melt refining and degassing. Effectively removes hydrogen and impurities from molten aluminum to improve casting quality. Extended service life reduces replacement costs.',
    pp_p4_s1: 'Purity: >99.9% high-purity graphite', pp_p4_s2: 'Max Temp: >900°C, oxidation resistant', pp_p4_s3: 'Custom diameter and length available', pp_p4_btn: 'Request Quote',
    pp_p5_tag: 'Precision Temperature Components', pp_p5_title: 'Heater',
    pp_p5_desc: 'Includes electric heating tubes, ceramic heaters, and infrared heaters for industrial heating processes, mold preheating, and semiconductor equipment — providing precise, stable heating control.',
    pp_p5_s1: 'Max Temp: up to 1200°C by type', pp_p5_s2: 'Multiple power ratings (50W–10kW)', pp_p5_s3: 'Custom shape and wiring configuration', pp_p5_btn: 'Request Quote',
    pp_p6_tag: 'Precision Measurement Components', pp_p6_title: 'Thermocouple',
    pp_p6_desc: 'Offers K, J, N, S, R, and B type thermocouples with various protection tube materials for furnace temperature measurement, semiconductor process control, food processing, and broad industrial applications.',
    pp_p6_s1: 'Range: −200°C to +1800°C', pp_p6_s2: 'Multiple types and sheath materials', pp_p6_s3: 'IEC / JIS compliant', pp_p6_btn: 'Request Quote',
    pp_qa_title: 'Quality Assurance', pp_qa_lead: 'Every product undergoes rigorous quality inspection to ensure compliance with customer specifications and international standards.',
    pp_qa_1_title: 'Rigorous Quality Control', pp_qa_1_desc: 'End-to-end quality traceability from raw materials to finished goods ensures every product meets specifications.',
    pp_qa_2_title: 'Custom Specifications', pp_qa_2_desc: 'Custom sizes, materials, and specifications to meet the unique requirements of specialized manufacturing processes.',
    pp_qa_3_title: 'Fast Delivery', pp_qa_3_desc: 'Excellent inventory management and production scheduling ensure rapid delivery of standard products and on-time fulfillment of custom orders.',
    pp_cta_title: 'Can\'t Find the Right Specification?',
    pp_cta_desc: 'Hsin-Chan Industrial Co., Ltd. offers fully custom services. Tell us your requirements and our technical team will design the optimal product specification for you.',
    pp_cta_btn: 'Enquire Now',

    srv_page_title: 'Services',
    srv_page_lead: 'Six automation services covering digital planning, robotic arm integration, machine vision inspection, and equipment intelligence upgrades — one-stop manufacturing solutions.',
    srv_d1_num: 'SERVICE 01', srv_d1_tag: 'Digital Twin', srv_d1_title: 'Digital Twin Automation Planning',
    srv_d1_desc: 'Before physical construction, simulate the entire production line operation virtually using digital twin technology. 3D models and dynamic simulation identify design flaws early, significantly reducing construction risk and modification costs.',
    srv_d1_p1: 'Virtual line layout planning and motion simulation', srv_d1_p2: 'Equipment interference checking and safety assessment',
    srv_d1_p3: 'Takt time analysis and optimization', srv_d1_p4: '3D design drawings and technical specifications provided', srv_d1_btn: 'Enquire About This Service',
    srv_d2_num: 'SERVICE 02', srv_d2_tag: 'Robot Integration', srv_d2_title: 'Robotic Arm Applications',
    srv_d2_desc: 'Integrating major brand industrial robots (FANUC, ABB, KUKA, Yaskawa, etc.) for handling, welding, assembly, and dispensing applications, combined with end-effector design and path planning to build efficient, flexible production lines.',
    srv_d2_p1: 'Multi-brand robot selection and deployment', srv_d2_p2: 'Custom end-effector (gripper/tool) design',
    srv_d2_p3: 'Offline programming and path optimization', srv_d2_p4: 'Collaborative robot (Cobot) safety system integration', srv_d2_btn: 'Enquire About This Service',
    srv_d3_num: 'SERVICE 03', srv_d3_tag: 'Custom Automation', srv_d3_title: 'Custom Machine Design & Build',
    srv_d3_desc: 'From customer requirements analysis, mechanism design, engineering drawings, and component manufacturing to complete assembly, programming, and on-site commissioning — full turnkey automation equipment design and manufacturing.',
    srv_d3_p1: 'Requirements analysis and feasibility assessment', srv_d3_p2: 'Mechanism design and 3D modeling (SolidWorks / Solid Edge)',
    srv_d3_p3: 'PLC / HMI program development (Mitsubishi / Siemens)', srv_d3_p4: 'Complete machine testing, on-site installation, and personnel training', srv_d3_btn: 'Enquire About This Service',
    srv_d4_num: 'SERVICE 04', srv_d4_tag: 'Machine Vision', srv_d4_title: 'Machine Vision Inspection',
    srv_d4_desc: 'Combining industrial cameras, high-precision lenses, and AI image analysis to achieve product appearance defect detection, dimensional measurement, barcode recognition, and position guidance — replacing manual inspection.',
    srv_d4_p1: 'Appearance defect detection (scratches, stains, missing material)', srv_d4_p2: 'High-precision dimensional measurement (±0.01mm)',
    srv_d4_p3: 'QR Code / Barcode / OCR recognition', srv_d4_p4: 'Vision-guided robotic arm positioning and picking', srv_d4_btn: 'Enquire About This Service',
    srv_d5_num: 'SERVICE 05', srv_d5_tag: 'Fixture Design', srv_d5_title: 'Fixture & Jig Design',
    srv_d5_desc: 'Designing and manufacturing high-precision fixtures and jigs for automated assembly, machining, and inspection processes. Precise positioning and clamping ensures consistent machining positions for every product, improving yield rates.',
    srv_d5_p1: 'Machining fixtures, welding jigs, assembly tooling', srv_d5_p2: 'Materials: Aluminum alloy, tool steel, stainless steel',
    srv_d5_p3: 'Repeatability: ±0.02mm', srv_d5_p4: 'Quick-change design to reduce line changeover time', srv_d5_btn: 'Enquire About This Service',
    srv_d6_num: 'SERVICE 06', srv_d6_tag: 'Smart Upgrade', srv_d6_title: 'Equipment Intelligence Upgrade',
    srv_d6_desc: 'Retrofit existing traditional equipment with PLC, HMI, and IoT modules to enable remote monitoring, data collection, and predictive maintenance — upgrading legacy production lines digitally with minimal investment.',
    srv_d6_p1: 'PLC controller upgrade (Mitsubishi iQ-F / iQ-R)', srv_d6_p2: 'HMI panel installation (Pro-face / Weintek)',
    srv_d6_p3: 'IoT data collection and cloud monitoring dashboard', srv_d6_p4: 'OEE equipment efficiency analysis and anomaly alert system', srv_d6_btn: 'Enquire About This Service',
    srv_cta_title: 'Ready to Launch Your Automation Project?',
    srv_cta_desc: 'Whether it\'s a new production line or upgrading existing equipment, Hsin-Chan Industrial Co., Ltd.\'s engineering team will deliver the most suitable solution.',
    srv_cta_btn: 'Contact Us Now',

    tech_page_title: 'Technology Insights',
    tech_page_lead: 'From semiconductor processes to humanoid robots, exploring Hsin-Chan Industrial Co., Ltd.\'s precision components and high-temperature materials across six cutting-edge application fields.',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: 'Semiconductor', tech_d1_title: 'Semiconductor Process',
    tech_d1_desc: 'Semiconductor wafer processing requires precise control of molten metals and chemical materials in ultra-high-temperature, highly corrosive environments. Hsin-Chan Industrial Co., Ltd.\'s SiC protection tubes and graphite degassing tubes serve as critical consumables in diffusion furnace tubes and crystal growth equipment.',
    tech_d1_p1: 'SiC protection tube: rated to 1600°C, oxidation and corrosion resistant', tech_d1_p2: 'Graphite degassing tube: effectively removes hydrogen impurities from molten aluminum',
    tech_d1_p3: 'One-piece barrel: ensures pure, contamination-free transport of molten silicon', tech_d1_p4: 'Custom dimensions to fit various crystal growth furnaces and PECVD equipment', tech_d1_btn: 'Enquire About Applications',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: 'Electric Vehicle', tech_d2_title: 'Electric Vehicle',
    tech_d2_desc: 'EV battery modules, motors, and power electronics components demand rigorous thermal management. Hsin-Chan Industrial Co., Ltd.\'s refractory materials and precision ceramic components are widely used in battery pack structural protection, motor stator insulation, and aluminum alloy motor housing production processes.',
    tech_d2_p1: 'Battery module fire-resistant insulation panels for structural protection', tech_d2_p2: 'Aluminum casting process protection tubes for motor housing production',
    tech_d2_p3: 'Ceramic thermocouples for precise motor operating temperature monitoring', tech_d2_p4: 'High-temperature insulation materials for power modules (IGBT/SiC MOSFET)', tech_d2_btn: 'Enquire About Applications',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'Silicon Photonics', tech_d3_title: 'Silicon Photonics',
    tech_d3_desc: 'Silicon photonics integrates optical components on silicon substrates for high-speed optical communications and AI acceleration. Hsin-Chan Industrial Co., Ltd. provides high-precision ceramic carriers, high-temperature fixtures, and process protection components for photonic chip packaging.',
    tech_d3_p1: 'High-precision ceramic positioning fixtures for fiber array alignment', tech_d3_p2: 'High-temperature process carriers for stable bonding support',
    tech_d3_p3: 'Alumina ceramic insulation for uniform heat distribution in annealing furnaces', tech_d3_p4: 'Custom specifications to match foundry process node requirements', tech_d3_btn: 'Enquire About Applications',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'Humanoid Robot', tech_d4_title: 'Humanoid Robot',
    tech_d4_desc: 'Humanoid robot joint drives, end effectors, and sensing systems require parts that balance lightweight construction with high precision. Hsin-Chan Industrial Co., Ltd.\'s 51 years of precision machining experience delivers aluminum alloy structural parts, precision drive sleeves, and wear-resistant ceramic components.',
    tech_d4_p1: 'Precision joint drive sleeves to maintain motion repeatability', tech_d4_p2: 'Lightweight aluminum alloy structural parts to reduce body weight and improve agility',
    tech_d4_p3: 'Wear-resistant ceramic guide components to extend joint service life', tech_d4_p4: 'High-precision tolerance control: ±0.01mm class machining capability', tech_d4_btn: 'Enquire About Applications',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: 'Quantum Computing', tech_d5_title: 'Quantum Computing',
    tech_d5_desc: 'Quantum computer dilution refrigerators must maintain qubits near absolute zero (15 mK), placing extreme demands on component thermal conductivity, EMI protection, and ultra-precision machining. Hsin-Chan Industrial Co., Ltd. provides high-purity oxygen-free copper components and precision ceramic insulation for low-temperature environments.',
    tech_d5_p1: 'High-purity oxygen-free copper (OFC) precision parts with excellent thermal and electrical conductivity', tech_d5_p2: 'Ceramic insulation structural components designed for low-temperature thermal isolation',
    tech_d5_p3: 'Ultra-precision machining: surface roughness Ra ≤ 0.4μm', tech_d5_p4: 'Strict cleanliness control to avoid contamination affecting quantum states', tech_d5_btn: 'Enquire About Applications',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / Drone', tech_d6_title: 'UAV / Drone',
    tech_d6_desc: 'Drones pursue the ultimate balance of lightweight construction and structural strength. Critical components like motor mounts, drive shafts, and gimbal frames require precision machining and strict quality control. Hsin-Chan Industrial Co., Ltd. provides high-strength aluminum alloy structural parts, carbon fiber composite inserts, and custom tooling.',
    tech_d6_p1: 'Aerospace aluminum alloy (7075-T6) lightweight structural parts', tech_d6_p2: 'Motor mounts with precision bores to ensure motor concentricity',
    tech_d6_p3: 'Carbon fiber composite embedded metal inserts', tech_d6_p4: 'Rapid prototyping and flexible small-batch production services', tech_d6_btn: 'Enquire About Applications',
    tech_cta_title: 'Explore Precision Material Applications in Your Field?',
    tech_cta_desc: 'Hsin-Chan Industrial Co., Ltd.\'s technical team welcomes collaboration with manufacturers across cutting-edge technology fields to explore material solutions and push the boundaries of technology together.',
    tech_cta_btn: 'Contact the Technical Team',

    career_page_title: 'Careers',
    career_page_lead: 'Join Hsin-Chan Industrial Co., Ltd., carry forward 51 years of precision manufacturing craftsmanship, and embrace the opportunities and challenges of the automation and new materials era together.',
    career_apply_title: 'How to Apply',
    career_apply_lead: 'If you\'re interested in joining Hsin-Chan Industrial Co., Ltd., please send your resume and personal statement to the email below. Our HR team will contact you within 3 business days of receiving your application.',
    career_apply_label: 'Apply by Email',
    career_apply_note: 'Please include "Position Title + Name" in the subject line, with your complete resume and personal statement',
    career_jobs_title: 'Current Openings',
    career_j1_tag: 'Manufacturing Engineering', career_j1_title: 'Precision Machinist',
    career_j1_p1: 'Operate CNC lathes, milling machines, and other precision machining equipment', career_j1_p2: 'Perform parts machining and quality self-inspection per engineering drawings',
    career_j1_p3: 'Education: High school or above; mechanical-related major preferred', career_j1_p4: 'Experienced machinists preferred; trainee applicants welcome', career_j1_btn: 'Apply Now',
    career_j2_tag: 'Sales & Marketing', career_j2_title: 'Sales Engineer',
    career_j2_p1: 'Develop and maintain domestic and international client relationships', career_j2_p2: 'Interpret customer technical requirements and provide material solutions',
    career_j2_p3: 'Education: College degree or above; engineering or chemical background preferred', career_j2_p4: 'Japanese or English communication skills preferred', career_j2_btn: 'Apply Now',
    career_j3_tag: 'Automation Technology', career_j3_title: 'Automation Equipment Engineer',
    career_j3_p1: 'Plan, design, and integrate automated production equipment', career_j3_p2: 'PLC programming (Mitsubishi iQ-F / iQ-R) and HMI integration',
    career_j3_p3: 'Education: College degree or above; electrical, mechatronics, or automation major', career_j3_p4: 'Robot arm integration or vision system experience preferred', career_j3_btn: 'Apply Now',
    career_ben_title: 'Employee Benefits',
    career_ben_lead: 'Hsin-Chan Industrial Co., Ltd. values every employee\'s work quality and career development, providing comprehensive benefits and a growth-oriented environment.',
    career_ben_1_title: 'Labor Insurance', career_ben_1_desc: 'Statutory labor insurance covering workplace injuries, illness, retirement, and unemployment — safeguarding every employee.',
    career_ben_2_title: 'Health Insurance', career_ben_2_desc: 'National health insurance providing comprehensive medical coverage for employees and their families.',
    career_ben_3_title: 'Perfect Attendance Bonus', career_ben_3_desc: 'Monthly bonus awarded to employees with perfect attendance, recognizing dedication and a responsible work ethic.',
    career_ben_4_title: 'Holiday Bonus', career_ben_4_desc: 'Seasonal bonuses for Lunar New Year, Dragon Boat Festival, and Mid-Autumn Festival — celebrating traditional holidays together.',
    career_ben_5_title: 'Birthday Gift', career_ben_5_desc: 'A birthday gift for every employee to express the company\'s care, appreciation, and heartfelt wishes for each individual.',
    career_ben_6_title: 'Year-End Bonus', career_ben_6_desc: 'Performance-based year-end bonus recognizing annual contributions and sharing in the company\'s growth.',
    career_ben_7_title: 'Group Insurance', career_ben_7_desc: 'Supplemental group insurance covering accidents and medical expenses — providing an extra layer of comprehensive protection.',
    career_ben_8_title: 'Domestic Travel', career_ben_8_desc: 'Regular company-organized domestic trips to recharge, strengthen bonds, and build a cohesive, spirited team.',
    career_ben_9_title: 'Year-End Banquet', career_ben_9_desc: 'Annual year-end banquet to thank employees for their hard work, celebrate accomplishments, and welcome the new year.',
    career_cta_title: 'Ready to Join Hsin-Chan Industrial Co., Ltd.?',
    career_cta_desc: 'Send your resume to hc3814497@gmail.com — we look forward to building Hsin-Chan Industrial Co., Ltd.\'s next 50 years together with you.',
    career_cta_btn: 'Submit Your Resume Now',

    contact_page_title: 'Contact Us',
    contact_page_lead: 'Whether for product quotations, technical collaboration, or service discussions, contact Hsin-Chan Industrial Co., Ltd. through the methods below. We respond within 1–2 business days.',
    contact_info_title: 'Company Information',
    contact_label_addr: 'Address', contact_addr_value: 'No. 490, Sec. 3, Zhongzheng E. Rd., Dayuan Dist., Taoyuan City 33841, Taiwan',
    contact_label_tel: 'Phone', contact_label_email: 'Email', contact_label_fax: 'Fax',
    contact_label_fb: 'Facebook', contact_fb_value: 'Hsin-Chan Industrial Co., Ltd.',
    contact_hours_title: 'Business Hours',
    contact_hours_weekday: 'Monday – Friday　08:00 – 17:30',
    contact_hours_weekend: 'Saturday & Sunday　Closed',
    contact_form_title: 'Online Enquiry',
    contact_form_lead: 'Please fill in the details below. We will contact you within 1–2 business days.',
    contact_form_name_label: 'Full Name', contact_form_company_label: 'Company / Organization',
    contact_form_tel_label: 'Phone', contact_form_email_label: 'Email Address', contact_form_msg_label: 'Message',
    contact_form_name_ph: 'Enter your full name', contact_form_company_ph: 'Enter company or organization name',
    contact_form_tel_ph: 'e.g. 02-1234-5678', contact_form_email_ph: 'example@company.com',
    contact_form_msg_ph: 'Describe your needs, e.g. product specification inquiry, quotation request, technical collaboration…',
    contact_form_submit: 'Send Enquiry',
  },
};

/* ═══════════════════════════════════════════════════════════════════════════
   2. i18n LANGUAGE SWITCHER
   ═══════════════════════════════════════════════════════════════════════════ */
const i18n = (() => {
  const STORAGE_KEY = 'xinchen-lang';
  const DEFAULT     = 'zh';
  const SUPPORTED   = ['zh', 'ja', 'en'];
  const LANG_ATTR   = { zh: 'zh-TW', ja: 'ja', en: 'en' };

  let current = DEFAULT;

  function apply(lang) {
    if (!SUPPORTED.includes(lang)) lang = DEFAULT;
    current = lang;

    document.documentElement.lang = LANG_ATTR[lang];

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key  = el.getAttribute('data-i18n');
      const text = translations[lang][key];
      if (text !== undefined) el.textContent = text;
    });

    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
      const key  = el.getAttribute('data-i18n-ph');
      const text = translations[lang][key];
      if (text !== undefined) el.placeholder = text;
    });

    // Sync ALL lang-btn groups (header + footer)
    document.querySelectorAll('.lang-btn').forEach(btn => {
      const active = btn.getAttribute('data-lang') === lang;
      btn.classList.toggle('lang-btn--active', active);
      btn.setAttribute('aria-pressed', String(active));
    });

    try { localStorage.setItem(STORAGE_KEY, lang); } catch (_) {}
  }

  function saved() {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      return SUPPORTED.includes(v) ? v : DEFAULT;
    } catch (_) { return DEFAULT; }
  }

  function init() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.addEventListener('click', () => apply(btn.getAttribute('data-lang')));
    });
    apply(saved());
  }

  return { init, apply, current: () => current };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   3. NAV — Sticky header + mobile menu
   ═══════════════════════════════════════════════════════════════════════════ */
const nav = (() => {
  const header = document.getElementById('site-header');
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('navMenu');

  let isOpen = false;
  let lastScrollY = 0;
  const THRESHOLD = 60;
  const HIDE_THRESHOLD = 300;

  const updateScroll = () => {
    const y = window.scrollY;
    header.classList.toggle('is-scrolled', y > THRESHOLD);
    if (y > HIDE_THRESHOLD) {
      header.classList.toggle('is-hidden', y > lastScrollY);
    } else {
      header.classList.remove('is-hidden');
    }
    lastScrollY = y;
  };

  function open() {
    isOpen = true;
    menu.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', '關閉選單');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    isOpen = false;
    menu.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', '開啟選單');
    document.body.style.overflow = '';
  }

  function init() {
    if (!header || !toggle || !menu) return;

    window.addEventListener('scroll', updateScroll, { passive: true });
    updateScroll();

    toggle.addEventListener('click', () => isOpen ? close() : open());

    menu.querySelectorAll('.nav__link').forEach(l => l.addEventListener('click', close));

    document.addEventListener('click', e => {
      if (isOpen && !header.contains(e.target)) close();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && isOpen) { close(); toggle.focus(); }
    });

    window.matchMedia('(min-width: 1367px)').addEventListener('change', e => {
      if (e.matches && isOpen) close();
    });
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   4. SCROLL REVEAL — IntersectionObserver
   ═══════════════════════════════════════════════════════════════════════════ */
const scrollReveal = (() => {
  function init() {
    const els = document.querySelectorAll('[data-reveal]');
    if (!els.length) return;

    // Apply stagger delays from data-reveal-delay attribute
    els.forEach(el => {
      const delay = el.getAttribute('data-reveal-delay');
      if (delay) el.style.transitionDelay = `${delay}ms`;
    });

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -50px 0px', threshold: 0.1 }
    );

    els.forEach(el => observer.observe(el));
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   5. COUNTER — Animated number increment with easing
   ═══════════════════════════════════════════════════════════════════════════ */
const counter = (() => {
  // easeOutExpo for crisp deceleration
  function ease(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }

  function animate(el, target, suffix, duration) {
    const start = performance.now();
    const run = now => {
      const p = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(ease(p) * target) + suffix;
      if (p < 1) requestAnimationFrame(run);
      else {
        el.textContent = target + suffix;
        el.classList.add('stat-card__num--done');
        el.addEventListener('animationend', () => el.classList.remove('stat-card__num--done'), { once: true });
      }
    };
    requestAnimationFrame(run);
  }

  function init() {
    const els = document.querySelectorAll('[data-count]');
    if (!els.length) return;

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          const el     = entry.target;
          const target = parseInt(el.getAttribute('data-count'), 10);
          const suffix = el.getAttribute('data-suffix') || '';
          animate(el, target, suffix, 1600);
          observer.unobserve(el);
        });
      },
      { threshold: 0.5 }
    );

    els.forEach(el => observer.observe(el));
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   6. HERO CANVAS — Particle network with performance safeguards
   ═══════════════════════════════════════════════════════════════════════════ */
const heroCanvas = (() => {
  function init() {
    const canvas = document.getElementById('heroCanvas');
    if (!canvas) return;

    // Skip animation if user prefers reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      canvas.style.display = 'none';
      return;
    }

    const ctx = canvas.getContext('2d');
    let W, H, particles, animId;
    const w = window.innerWidth;
    const N = w < 640 ? 20 : w < 1024 ? 40 : w < 1920 ? 60 : 80;
    const DIST = 130;

    class Particle {
      reset() {
        this.x  = Math.random() * W;
        this.y  = Math.random() * H;
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = (Math.random() - 0.5) * 0.3;
        this.r  = Math.random() * 1.4 + 0.4;
        this.a  = Math.random() * 0.35 + 0.08;
      }
      constructor() { this.reset(); }
      update() {
        this.x += this.vx; this.y += this.vy;
        if (this.x < -20) this.x = W + 20;
        if (this.x > W + 20) this.x = -20;
        if (this.y < -20) this.y = H + 20;
        if (this.y > H + 20) this.y = -20;
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(43,75,107,${this.a})`;
        ctx.fill();
      }
    }

    function resize() {
      // Use offsetWidth/Height after layout
      W = canvas.width  = canvas.offsetWidth  || canvas.parentElement.offsetWidth;
      H = canvas.height = canvas.offsetHeight || canvas.parentElement.offsetHeight;
    }

    function build() {
      particles = Array.from({ length: N }, () => new Particle());
    }

    function connections() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d  = Math.sqrt(dx * dx + dy * dy);
          if (d < DIST) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(43,75,107,${(1 - d / DIST) * 0.1})`;
            ctx.lineWidth = 0.7;
            ctx.stroke();
          }
        }
      }
    }

    function loop() {
      ctx.clearRect(0, 0, W, H);
      particles.forEach(p => { p.update(); p.draw(); });
      connections();
      animId = requestAnimationFrame(loop);
    }

    // Pause when tab is hidden to save CPU
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) cancelAnimationFrame(animId);
      else if (!heroHidden) loop();
    });

    // Pause when hero section is scrolled out of view
    let heroHidden = false;
    const heroSection = canvas.closest('#hero') || canvas.closest('section');
    if (heroSection) {
      const heroIO = new IntersectionObserver(entries => {
        heroHidden = !entries[0].isIntersecting;
        if (heroHidden) cancelAnimationFrame(animId);
        else if (!document.hidden) loop();
      }, { threshold: 0 });
      heroIO.observe(heroSection);
    }

    const ro = new ResizeObserver(() => { resize(); build(); });
    ro.observe(canvas.parentElement);

    // Defer init one frame so layout is complete
    requestAnimationFrame(() => {
      resize();
      build();
      loop();
    });
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   7. PRODUCT TILT — Mouse parallax on product highlight images
   ═══════════════════════════════════════════════════════════════════════════ */
const productTilt = (() => {
  const MAX_TILT = 6; // degrees

  function applyTilt(el) {
    el.addEventListener('mousemove', e => {
      const rect   = el.getBoundingClientRect();
      const x      = (e.clientX - rect.left) / rect.width  - 0.5;
      const y      = (e.clientY - rect.top)  / rect.height - 0.5;
      const rotX   = -y * MAX_TILT;
      const rotY   =  x * MAX_TILT;
      el.style.transform = `perspective(600px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale(1.015)`;
    });

    el.addEventListener('mouseleave', () => {
      el.style.transform = '';
      el.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      setTimeout(() => { el.style.transition = ''; }, 650);
    });
  }

  function init() {
    // Skip on touch devices (tilt is meaningless without mouse)
    if (window.matchMedia('(hover: none)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.product-hl__img').forEach(applyTilt);
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   8. SMOOTH SCROLL — Anchor links with offset for fixed header
   ═══════════════════════════════════════════════════════════════════════════ */
const smoothScroll = (() => {
  function init() {
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', e => {
        const id     = link.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (!target) return;

        e.preventDefault();

        const navH   = parseInt(
          getComputedStyle(document.documentElement).getPropertyValue('--nav-h'),
          10
        ) || 72;
        const top    = target.getBoundingClientRect().top + window.scrollY - navH - 16;

        window.scrollTo({ top, behavior: 'smooth' });
      });
    });
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   9. STAT CARD REVEAL — Trigger top-border animation on intersection
   ═══════════════════════════════════════════════════════════════════════════ */
const statReveal = (() => {
  function init() {
    const cards = document.querySelectorAll('.stat-card');
    if (!cards.length) return;

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );

    cards.forEach(c => observer.observe(c));
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   10. FOOTER YEAR
   ═══════════════════════════════════════════════════════════════════════════ */
function updateYear() {
  const el = document.getElementById('footerYear');
  if (el) el.textContent = new Date().getFullYear();
}

/* ═══════════════════════════════════════════════════════════════════════════
   11. SCROLL PROGRESS BAR — Thin gradient bar at top of viewport
   ═══════════════════════════════════════════════════════════════════════════ */
const scrollProgress = (() => {
  function init() {
    const bar = document.createElement('div');
    bar.id = 'scroll-progress';
    document.body.prepend(bar);

    window.addEventListener('scroll', () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      if (total <= 0) return;
      bar.style.width = (window.scrollY / total * 100) + '%';
    }, { passive: true });
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   12. CURSOR GLOW — Subtle radial glow following mouse (desktop only)
   ═══════════════════════════════════════════════════════════════════════════ */
const cursorGlow = (() => {
  function init() {
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const el = document.createElement('div');
    el.id = 'cursor-glow';
    document.body.appendChild(el);

    document.addEventListener('mousemove', e => {
      el.style.opacity = '1';
      el.style.transform = `translate(calc(${e.clientX}px - 50%), calc(${e.clientY}px - 50%))`;
    }, { passive: true });

    document.addEventListener('mouseleave', () => { el.style.opacity = '0'; });
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   INIT — Bootstrap all modules
   ═══════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  i18n.init();
  nav.init();
  scrollReveal.init();
  counter.init();
  heroCanvas.init();
  productTilt.init();
  smoothScroll.init();
  statReveal.init();
  scrollProgress.init();
  cursorGlow.init();
  updateYear();
  contentApi.init();
  contactForm.init();
});

/* ═══════════════════════════════════════════════════════════════════════════
   CONTENT API — 從 content.json 動態載入 FAQ 與 SEO 內容
   ─────────────────────────────────────────────────────────────────────────
   【如何更新文字】
   直接編輯 content.json 的 "faq" 陣列即可新增 / 修改 / 刪除問答，
   無需更動任何 HTML 或 JS 程式碼。
   ═══════════════════════════════════════════════════════════════════════════ */
const contentApi = (() => {
  const FAQ_LIST = document.getElementById('faqList');

  /**
   * 安全 HTML 轉義 — 防止 XSS（所有來自 JSON 的文字都必須過此函式）
   * 將 & < > " ' 轉換為 HTML 實體，使任何 HTML 標籤無法被執行
   */
  function esc(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  /**
   * 驗證 FAQ 資料結構，防止格式異常資料進入 DOM
   * 確保 id 僅包含英數字與連字號（防止 id 注入）
   */
  function validateFaqItem(item) {
    if (typeof item !== 'object' || item === null) return false;
    if (typeof item.question !== 'string' || !item.question.trim()) return false;
    if (typeof item.answer !== 'string' || !item.answer.trim()) return false;
    if (typeof item.id !== 'string' || !/^[a-z0-9-]+$/.test(item.id)) return false;
    return true;
  }

  /** 渲染單一 FAQ 項目（純 DOM API，無 innerHTML，防 XSS） */
  function renderFaqItem(item, index) {
    const safeId  = esc(item.id);
    const btnId   = `faq-btn-${safeId}`;
    const bodyId  = `faq-body-${safeId}`;

    // ── 外層容器 ──────────────────────────────────────────────────────────
    const li = document.createElement('div');
    li.className = 'faq-item';
    li.setAttribute('role', 'listitem');
    li.setAttribute('data-reveal', '');
    li.setAttribute('data-reveal-delay', String(index * 60));

    // ── 按鈕 ──────────────────────────────────────────────────────────────
    const btn = document.createElement('button');
    btn.className = 'faq-item__btn';
    btn.id = btnId;
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', bodyId);

    const qSpan = document.createElement('span');
    qSpan.className = 'faq-item__question';
    qSpan.textContent = item.question;   // textContent — 完全安全
    btn.appendChild(qSpan);

    if (item.category) {
      const tag = document.createElement('span');
      tag.className = 'faq-item__tag';
      tag.setAttribute('aria-hidden', 'true');
      tag.textContent = item.category;   // textContent — 完全安全
      btn.appendChild(tag);
    }

    // SVG 圖示（靜態，不包含任何使用者資料）
    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'faq-item__icon');
    svg.setAttribute('viewBox', '0 0 16 16');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('aria-hidden', 'true');
    const path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', 'M8 2v12M2 8h12');
    path.setAttribute('stroke-linecap', 'round');
    svg.appendChild(path);
    btn.appendChild(svg);

    // ── 展開區域 ──────────────────────────────────────────────────────────
    const body = document.createElement('div');
    body.className = 'faq-item__body';
    body.id = bodyId;
    body.setAttribute('role', 'region');
    body.setAttribute('aria-labelledby', btnId);

    const inner = document.createElement('div');
    inner.className = 'faq-item__inner';

    const answer = document.createElement('p');
    answer.className = 'faq-item__answer';
    answer.textContent = item.answer;    // textContent — 完全安全

    inner.appendChild(answer);
    body.appendChild(inner);

    li.appendChild(btn);
    li.appendChild(body);

    // ── 手風琴互動 ────────────────────────────────────────────────────────
    btn.addEventListener('click', () => {
      const isOpen = li.classList.contains('is-open');
      FAQ_LIST.querySelectorAll('.faq-item.is-open').forEach(el => {
        el.classList.remove('is-open');
        el.querySelector('.faq-item__btn').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        li.classList.add('is-open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });

    return li;
  }

  /** 將 FAQ 資料注入 JSON-LD FAQPage schema（SSE / AI 爬蟲可讀） */
  function injectFaqSchema(faqItems) {
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      'mainEntity': faqItems.map(item => ({
        '@type': 'Question',
        'name': item.question,
        'acceptedAnswer': {
          '@type': 'Answer',
          'text': item.answer
        }
      }))
    };
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.id = 'faq-schema';
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }

  async function init() {
    if (!FAQ_LIST) return;
    try {
      const res = await fetch('content.json');
      if (!res.ok) throw new Error('content.json fetch failed');
      const data = await res.json();
      // 驗證並過濾格式不正確的項目，防止畸形 JSON 造成 DOM 異常
      const items = (data.faq || []).filter(validateFaqItem).slice(0, 30); // 最多30則
      if (!items.length) return;

      const fragment = document.createDocumentFragment();
      items.forEach((item, i) => fragment.appendChild(renderFaqItem(item, i)));
      FAQ_LIST.appendChild(fragment);

      // 觀察動態新增的 FAQ 項目（加入滾動顯示動畫）
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-visible');
          obs.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -40px 0px', threshold: 0.1 });
      FAQ_LIST.querySelectorAll('[data-reveal]').forEach(el => {
        const d = el.getAttribute('data-reveal-delay');
        if (d) el.style.transitionDelay = `${d}ms`;
        obs.observe(el);
      });

      injectFaqSchema(items);
    } catch (e) {
      // content.json 不可用時靜默略過（不影響其他功能）
      if (FAQ_LIST) FAQ_LIST.closest('section')?.remove();
    }
  }

  return { init };
})();

/* ═══════════════════════════════════════════════════════════════════════════
   CONTACT FORM — 客戶端驗證 + Honeypot 防機器人
   ═══════════════════════════════════════════════════════════════════════════ */
const contactForm = (() => {
  // Email 格式驗證（RFC 5321 簡化版）
  const EMAIL_RE = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$/;
  // 電話格式：7-30 碼，允許數字、空格、+、-、()
  const TEL_RE   = /^[\d\s\+\-\(\)]{7,30}$/;

  function setError(inputEl, errId, msg) {
    inputEl.classList.add('is-invalid');
    inputEl.classList.remove('is-valid');
    const errEl = document.getElementById(errId);
    if (errEl) errEl.textContent = msg;
  }

  function clearError(inputEl, errId) {
    inputEl.classList.remove('is-invalid');
    inputEl.classList.add('is-valid');
    const errEl = document.getElementById(errId);
    if (errEl) errEl.textContent = '';
  }

  function validateField(input) {
    const v   = input.value.trim();
    const id  = input.id;
    const err = id.replace('contact-', '') + '-error';

    if (input.required && !v) {
      setError(input, err, '此欄位為必填');
      return false;
    }
    if (id === 'contact-name' && v.length < 2) {
      setError(input, err, '姓名至少需2個字');
      return false;
    }
    if (id === 'contact-email' && v && !EMAIL_RE.test(v)) {
      setError(input, err, '請輸入有效的 Email 格式（例：name@company.com）');
      return false;
    }
    if (id === 'contact-tel' && v && !TEL_RE.test(v)) {
      setError(input, err, '電話格式不正確（例：03-381-4497）');
      return false;
    }
    if (id === 'contact-message' && v.length < 10) {
      setError(input, err, '詢問內容至少需10個字');
      return false;
    }
    clearError(input, err);
    return true;
  }

  function init() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    // 字數計數器（詢問內容）
    const msgArea  = document.getElementById('contact-message');
    const msgCount = document.getElementById('msgCount');
    if (msgArea && msgCount) {
      const MAX = parseInt(msgArea.getAttribute('maxlength') || '2000', 10);
      const updateCount = () => {
        const len = msgArea.value.length;
        msgCount.textContent = `${len} / ${MAX}`;
        msgCount.classList.toggle('is-near-limit', len >= MAX * 0.85 && len < MAX);
        msgCount.classList.toggle('is-at-limit',   len >= MAX);
      };
      msgArea.addEventListener('input', updateCount);
    }

    // 即時驗證（離開欄位時）
    form.querySelectorAll('.form-input, .form-textarea').forEach(input => {
      input.addEventListener('blur', () => validateField(input));
      input.addEventListener('input', () => {
        if (input.classList.contains('is-invalid')) validateField(input);
      });
    });

    // 送出驗證
    form.addEventListener('submit', e => {
      // Honeypot 偵測：若蜜罐欄位有值，代表是機器人，靜默阻止
      const honey = form.querySelector('#contact-url');
      if (honey && honey.value) {
        e.preventDefault();
        return;
      }

      // 逐欄驗證
      const fields  = form.querySelectorAll('.form-input, .form-textarea');
      const allOk   = Array.from(fields).map(f => validateField(f)).every(Boolean);
      if (!allOk) {
        e.preventDefault();
        // 捲動到第一個錯誤欄位
        const firstError = form.querySelector('.is-invalid');
        if (firstError) firstError.focus();
      }
    });
  }

  return { init };
})();
