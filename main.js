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

    hero_badge: '以豐田生產哲學淬鍊的製造夥伴 · Since 1996',
    hero_h1_line1: '精密驅動，', hero_h1_line2: '智造未來',
    hero_h2: '欣晨工業有限公司 — 以改善、即時生產與自働化為核心，提供精密自動化解決方案',
    cta_products: '查看產品', cta_contact_ask: '聯絡詢問',
    metric_years: '年經驗', metric_products: '大產品線',
    metric_services: '大服務項目', scroll: 'SCROLL',

    idx_eyebrow_tps: 'TOYOTA PRODUCTION SYSTEM',
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
    prod_b_title: '高濃度奈米氣泡流體模組',
    prod_b_desc: '產生高濃度奈米氣泡流體，氣泡尺寸小於100nm。應用於半導體製程用水、生醫設備清洗與液冷系統，節能、高密度、免化學添加，大幅降低化學品成本與環境負擔。',
    prod_b_use: '半導體 / 生醫 / 液冷', prod_b_merit: '節能 / 高密度 / 免化學添加',
    spec_temp: '耐溫', spec_mat: '材質', spec_app: '應用',
    spec_purity: '氣泡尺寸', spec_use: '用途', spec_merit: '優勢',
    spec_type: '類型', spec_heat: '溫度', spec_spec: '規格', spec_model: '型號', spec_measure: '量測', spec_industry: '產業',
    cta_spec: '查看規格',

    idx_eyebrow_services: 'FULL-SPECTRUM AUTOMATION',
    srv_title: '全方位自動化服務',
    srv_lead: '七大服務，從規劃到交機，一站式解決您的自動化需求',
    srv_1_title: '數位雙生自動化設計規劃', srv_1_desc: '虛擬驗證產線，降低建造風險',
    srv_2_title: '機械手臂應用',           srv_2_desc: '搬運、焊接、組裝整合，路徑規劃',
    srv_3_title: '單機自動化設計製造',     srv_3_desc: '需求→設計→製造→調機，一條龍',
    srv_4_title: '視覺檢測',               srv_4_desc: '工業相機 + AI 瑕疵偵測、尺寸量測',
    srv_5_title: '夾治具設計製造',         srv_5_desc: '高精度夾具治具，提升一致性',
    srv_6_title: '設備智能化',             srv_6_desc: '既有設備升級 PLC / HMI / IoT',
    srv_7_title: '高濃度奈米氣泡流體產業應用', srv_7_desc: '半導體、生醫、液冷免化學導入',
    cta_learn: '了解更多', cta_all_services: '了解全部服務',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    idx_eyebrow_tps_insights: 'TPS INSIGHTS',
    tech_title: '豐田哲學 × 精密製造應用',
    tech_tag_semi: '半導體製程', tech_tag_ev: '電動車', tech_tag_robot: '人形機器人',
    tech_1_title: '精密製程的材料關鍵',
    tech_1_desc: '碳化矽保護管在半導體高溫製程中扮演關鍵角色，提供穩定的熱環境與腐蝕防護。',
    tech_2_title: '電池生產熱管理革新',
    tech_2_desc: 'EV 電池芯製造需要精確的熱管理解決方案，欣晨加熱器與感測元件確保生產一致性。',
    tech_3_title: '機器人關節精密加工',
    tech_3_desc: '人形機器人關節需要極高精度的製造工藝，欣晨夾治具設計為此提供精準解決方案。',
    cta_read_more: '閱讀更多', cta_view_all_tech: '查看全部技術主題',

    idx_eyebrow_cta: 'START TODAY',
    cta_banner_title: '準備好以豐田哲學優化您的生產線了嗎？',
    cta_banner_desc: '告訴我們您的現場問題，欣晨工業的工程師將親赴現場，以改善精神為您量身設計最佳方案。',
    cta_contact_now: '立即聯絡',

    footer_nav_title: '快速導覽', footer_contact_title: '聯絡資訊',
    footer_years: '30年製造經驗',
    footer_addr: '桃園市大園區中正東路三段490號',
    footer_tel: 'Tel：03-381-4497', footer_fax: 'Fax：03-381-4536',
    footer_tagline_1: '精密驅動', footer_tagline_2: '智造未來',
    footer_est: 'Est. 1996 · 30年製造經驗',

    // About page
    about_banner_title: '欣晨工業 公司簡介',
    about_banner_lead: '欣晨工業有限公司 — 30年精密製造經驗，深根桃園大園，服務全台灣工業客戶。以技術立業，以品質興業，以服務創業。',
    about_eyebrow_top: 'ABOUT US',
    about_eyebrow_story: 'OUR STORY',
    about_our_title: '關於欣晨工業',
    about_desc_1: '欣晨工業有限公司（Hsin-Chan Industrial Co., Ltd.）成立於1996年，座落於台灣桃園市大園區中正東路三段490號。歷經超過30年的積累，欣晨工業從早期的工業耗材供應商，逐步發展為涵蓋自動化設備設計、製造、整合及售後服務的全方位製造夥伴。',
    about_desc_2: '欣晨工業的核心產品涵蓋碳化矽保護管、高濃度奈米氣泡流體模組、加熱器、熱電偶等高溫工業耗材，並持續拓展數位雙生規劃、機械手臂應用、視覺檢測等智能自動化服務領域。欣晨工業的加熱器最高工作溫度可達1200°C，廣泛應用於射出成型、鋁鑄造與工業爐等製程。',
    about_desc_3: '時至今日，欣晨工業仍秉持「精密、客製、支援」三大核心，為半導體、鑄造、電動車、精密機械等產業提供可靠的製造解決方案。欣晨工業服務範圍涵蓋台灣全島及日本、東南亞，具備中文、日文、英文三語服務能力。',
    about_desc_4: '欣晨工業以豐田生產方式（TPS）為核心哲學，將改善（Kaizen）、即時生產（JIT）、自働化（Jidoka）落實於每一個製造環節。欣晨工業相信，透過持續改善與精密製造，能為客戶創造最大的生產效益，並共同迎接工業4.0的智造時代。',
    about_history_eyebrow: '發展歷程',
    about_tl_1_title: '公司創立', about_tl_1_desc: '於桃園大園設立，專注高溫工業耗材製造與供應，服務在地製造業客戶。',
    about_tl_2_title: '產品線擴展', about_tl_2_desc: '導入碳化矽保護管生產技術，服務對象延伸至半導體與鑄造業。',
    about_tl_3_title: '廠房擴建', about_tl_3_desc: '新增加熱器與熱電偶生產線，廠房面積擴建，提升年產能與品管能力。',
    about_tl_4_title: '自動化轉型', about_tl_4_desc: '跨足自動化設備設計製造，提供機械手臂整合、單機自動化及視覺檢測服務。',
    about_tl_5_title: '智能升級', about_tl_5_desc: '引入數位雙生技術，推動既有設備智能化，邁向工業4.0整合服務商。',
    about_eyebrow_philosophy: 'PHILOSOPHY',
    about_mgmt_title: '經營理念',
    about_mgmt_lead_1: '欣晨工業的經營哲學深受日本京瓷株式會社創辦人', about_mgmt_name: '稻盛和夫', about_mgmt_lead_2: '先生的啟發。他畢生相信，企業存在的意義在於追求全體成員物心兩面的幸福，並以此為基礎，為人類與社會的進步做出貢獻。這份信念，始終是欣晨工業前行的座右銘。',
    about_mgmt_quote_main: '敬天愛人',
    about_mgmt_quote_sub: 'けいてんあいじん',
    about_mgmt_quote_cite: '稻盛和夫（Inamori Kazuo）— 京瓷株式會社、KDDI 創辦人',
    about_mgmt_c1_title: '利他之心', about_mgmt_c1_concept: '利他即是利己',
    about_mgmt_c1_desc: '稻盛和夫認為，真正的成功來自「為他人著想」的利他之心。欣晨工業在每一次客戶溝通中，優先思考的是：什麼方案對客戶的生產最有益？而非單純販售產品。為客戶創造真實價值，才是長久合作的基石。',
    about_mgmt_c2_title: '敬天愛人', about_mgmt_c2_concept: '依循正道，以誠待人',
    about_mgmt_c2_desc: '「敬天」意謂遵從自然與事物的本質法則，不走捷徑、不欺瞞；「愛人」則是以真誠關懷面對每一位夥伴、客戶與員工。欣晨工業堅守誠信透明的原則，無論報價、交期或品質承諾，皆言出必行，從不讓客戶帶著疑慮離場。',
    about_mgmt_c3_title: '持續精進', about_mgmt_c3_concept: '付出不亞於任何人的努力',
    about_mgmt_c3_desc: '稻盛六項精進的首要條目，是「付出不亞於任何人的努力」。欣晨的工程師每天在車間磨練工藝，不滿足於「夠用」，追求的是「最好」。從圖面設計、零件加工到整機調試，每一道工序都比昨天精確一點、再精確一點。',
    about_mgmt_c4_title: '工作即修行', about_mgmt_c4_concept: '在勞動中磨練靈魂',
    about_mgmt_c4_desc: '稻盛和夫說：「工作是磨練靈魂最好的方式。」製造業的每一個零件、每一台設備，都是人的心血與意志的具體化。欣晨工業相信，全心投入工作不僅是對客戶負責，更是每一位員工自我成長、成就人格的途徑。',
    about_phil_title: '經營理念',
    about_phil_lead: '三大核心理念，驅動欣晨30年的穩健成長，也是我們服務每位客戶的承諾。',
    about_phil_1_title: '精密製造', about_phil_1_desc: '30年製造工藝積累，嚴格品質管控體系，每一個零件精準達標。從原材料進料到成品出廠，全程品質追蹤，確保設備穩定可靠運行。',
    about_phil_2_title: '客製服務', about_phil_2_desc: '從需求分析、機構設計到生產交機，全程一對一客製化服務。我們深入了解客戶生產現場，量身打造最適合您生產線的自動化解決方案。',
    about_phil_3_title: '技術支援', about_phil_3_desc: '專業工程師團隊現場調機與技術培訓，完善的售後維護體系。設備交機後持續提供技術諮詢，確保您的生產設備長期穩定高效運行。',
    about_team_title: '經營團隊',
    about_team_lead: '擁有豐富產業經驗的專業團隊，持續推動公司技術創新與服務升級。',
    about_team_1_role: '總經理', about_team_1_desc: '負責公司整體策略規劃與營運管理，帶領團隊持續創新，深耕自動化設備製造領域逾三十年。',
    about_team_2_role: '技術長', about_team_2_desc: '主導研發部門，專精於高溫材料工程與自動化機構設計，具備豐富的半導體製程設備開發經驗。',
    about_team_3_role: '業務總監', about_team_3_desc: '統籌業務開發與客戶關係管理，深入了解客戶需求，為各產業客戶提供最適切的自動化解決方案。',
    about_eyebrow_cta: 'CONTACT US',
    about_cta_title: '與欣晨工業合作，共創精密未來',
    about_cta_desc: '無論是產品詢價、技術諮詢或專案合作，歡迎聯絡欣晨工業有限公司的專業團隊。欣晨工業承諾1-2個工作日內回覆。',
    about_cta_btn: '立即聯絡',

    // Products page
    pp_eyebrow_top: 'PRODUCTS', pp_eyebrow_lineup: 'PRODUCT LINEUP', pp_eyebrow_qa: 'QUALITY ASSURANCE', pp_eyebrow_quote: 'REQUEST QUOTE',
    pp_banner_title: '欣晨工業 產品資訊',
    pp_banner_lead: '欣晨工業有限公司六大高溫工業耗材產品線，為半導體、鑄造、能源等產業提供嚴苛環境下的可靠材料解決方案。',
    pp_overview_title: '六大產品線', pp_overview_lead: '所有產品均通過嚴格品質管控，適用於高溫、腐蝕性、精密工業環境。',
    pp_p1_tag: '射出成形耗材', pp_p1_title: '一體式料管',
    pp_p1_desc: '採用一體成型製程，無接縫設計大幅降低熔湯滲漏風險。廣泛應用於鋁壓鑄、鎂合金壓鑄及各類非鐵金屬的射出成型製程。',
    pp_p1_s1: '材質：氮化鋼', pp_p1_s2: '硬度：HRC 60–65', pp_p1_s3: '客製化尺寸規格', pp_p1_btn: '詢問報價',
    pp_p1_app: '壓鑄機（宇部/東芝/芝浦）/ 射出成型', pp_p1_mat: 'SKD61 工具鋼', pp_p1_vtag: 'Integral Tube',
    pp_p2_tag: '高溫製程耗材', pp_p2_title: '碳化矽保護管',
    pp_p2_desc: '採用高純度碳化矽（SiC）製造，耐熱溫度超過1600°C，耐腐蝕性卓越。廣泛應用於半導體製程爐管、鋁液熔煉及各類高溫工業場景。',
    pp_p2_s1: '耐溫：＞1600°C', pp_p2_s2: '材質：高純度 SiC', pp_p2_s3: '抗熱衝擊、耐腐蝕', pp_p2_btn: '詢問報價',
    pp_p2_app: '半導體 / 鑄造業', pp_p2_mat: '高純度 SiC', pp_p2_vtag: 'SiC Tube · 1600°C',
    pp_p3_tag: '窯爐工業耗材', pp_p3_title: '耐火材料',
    pp_p3_desc: '各類高溫窯爐用耐火磚、澆注料及隔熱棉等材料，提供優異的隔熱保溫性能，延長窯爐使用壽命，降低能耗損失。',
    pp_p3_s1: '耐溫：依材質達1800°C', pp_p3_s2: '抗壓強度高、低熱傳導', pp_p3_s3: '多種材質與規格可選', pp_p3_btn: '詢問報價',
    pp_p3_type: '耐火磚 / 澆注料 / 隔熱棉', pp_p3_app: '窯爐 / 熔煉爐 / 熱處理爐', pp_p3_temp: '1200°C～1800°C', pp_p3_vtag: 'Refractory',
    pp_p4_tag: '半導體製程模組', pp_p4_title: '高濃度奈米氣泡流體模組',
    pp_p4_desc: '產生高濃度奈米氣泡流體，氣泡尺寸小於100nm。應用於半導體製程用水、生醫設備清洗與液冷系統，節能、高密度、免化學添加。',
    pp_p4_s1: '氣泡尺寸：< 100nm 高濃度奈米氣泡', pp_p4_s2: '應用：半導體 / 生醫 / 液冷系統', pp_p4_s3: '優勢：節能、高密度、免化學添加', pp_p4_btn: '詢問報價',
    pp_p4_use: '半導體 / 生醫 / 液冷', pp_p4_merit: '節能 / 高密度 / 免化學添加', pp_p4_vtag: 'Nano-Bubble · <100nm',
    pp_p5_tag: '精密溫控元件', pp_p5_title: '加熱器',
    pp_p5_desc: '多種規格工業電熱元件，包含碳化矽加熱棒、矽碳棒、鉬矽加熱器等。依客戶需求客製規格，適用於高溫爐管、熱處理設備及各類工業窯爐。',
    pp_p5_s1: '耐溫：依類型達1200°C', pp_p5_s2: '多種功率規格（50W–10kW）', pp_p5_s3: '客製化形狀與接線方式', pp_p5_btn: '詢問報價',
    pp_p5_type: 'SiC棒 / MoSi₂ / 鉑金絲', pp_p5_heat: '至 1800°C', pp_p5_spec: '鋼鐵業 / 玻璃業 / 鑄造業', pp_p5_vtag: 'Heater',
    pp_p6_tag: '精密量測元件', pp_p6_title: '熱電偶',
    pp_p6_desc: '工業用溫度感測器，提供K、J、R、S、B等多種型號。適用於各類高溫製程量測，反應速度快、精度高，搭配保護管使用耐用性更佳。',
    pp_p6_s1: '測溫範圍：−200°C ～ +1800°C', pp_p6_s2: '多種型號與保護管材質', pp_p6_s3: 'IEC / JIS 規範符合', pp_p6_btn: '詢問報價',
    pp_p6_model: 'K / J / R / S / B 型', pp_p6_measure: '至 1750°C', pp_p6_spec: '標準 / 客製', pp_p6_vtag: 'Thermocouple',

    // ── 產品詳細頁共用 (Product Detail Pages Shared) ──
    pd_eyebrow_specs: 'SPECIFICATIONS', pd_specs_title: '產品規格',
    pd_custom_title: '需要客製化規格？', pd_custom_desc: '欣晨工業提供完整客製化服務，告訴我們您的需求，工程師 1-2 個工作日內回覆。',
    pd_contact_btn: '聯絡我們', pd_contact_tel_label: '電話：', pd_contact_email_label: 'Email：',
    pd_contact_hours_label: '營業時間：', pd_contact_hours_val: '週一至週五 08:00–17:30',
    pd_eyebrow_types: 'PRODUCT TYPES', pd_types_title: '產品類型',
    pd_eyebrow_industries: 'INDUSTRIES', pd_industries_title: '應用產業',
    pd_eyebrow_faq: 'FAQ', pd_faq_title: '常見問題',
    pd_eyebrow_related: 'RELATED PRODUCTS', pd_related_title: '相關產品',
    pd_viewall: '查看全部產品', pd_viewall_desc: '六大高溫工業耗材',
    pd_eyebrow_quote: 'GET A QUOTE', pd_quote_btn: '立即詢價',

    // ── product-thermocouple.html ──
    pth_eyebrow: 'THERMOCOUPLES', pth_title: '熱電偶', pth_breadcrumb: '工業熱電偶',
    pth_lead: '全系列工業熱電偶，K、J、T、E、R、S、B 型，測溫範圍 -200°C ～ +1820°C，符合 IEC 584 國際標準。',
    pth_spec1_label: '支援型號', pth_spec1_val: 'K / J / T / E / R / S / B 型',
    pth_spec2_label: '測溫範圍', pth_spec2_val: '-200°C ～ +1820°C（依型號）',
    pth_spec3_label: '符合標準', pth_spec3_val: 'IEC 584（國際）、JIS C 1602（日本）',
    pth_spec4_label: '保護管材質', pth_spec4_val: '不鏽鋼 / 碳化矽（SiC）/ 高純度陶瓷 / 石英',
    pth_spec5_label: '接線方式', pth_spec5_val: '端子台式 / 接頭式 / 引線式',
    pth_spec6_label: '精度等級', pth_spec6_val: 'Class 1 / Class 2（依 IEC 584）',
    pth_spec7_label: '客製選項', pth_spec7_val: '長度、外徑、接頭、保護管均可客製',
    pth_type1_name: 'K型（鎳鉻-鎳矽）', pth_type1_desc: '最通用，-200°C ～ +1372°C，抗氧化性佳，工業標準首選。',
    pth_type2_name: 'J型（鐵-康銅）', pth_type2_desc: '-40°C ～ +750°C，適合還原性氣氛，成本低。',
    pth_type3_name: 'T型（銅-康銅）', pth_type3_desc: '-270°C ～ +400°C，低溫精度高，適合食品冷藏、冷凍。',
    pth_type4_name: 'E型（鎳鉻-康銅）', pth_type4_desc: '-270°C ～ +1000°C，靈敏度最高，適合低溫高精度。',
    pth_type5_name: 'R/S型（鉑銠-鉑）', pth_type5_desc: '0°C ～ +1767°C，貴金屬，高精度，適合精密高溫製程。',
    pth_type6_name: 'B型（鉑銠30%-鉑銠6%）', pth_type6_desc: '0°C ～ +1820°C，最高溫型號，適合高溫氧化氣氛。',
    pth_ind1: '射出成型 — 料管溫度監控、模具溫度量測',
    pth_ind2: '鋁合金鑄造 — 熔爐溫度、澆注溫度即時監控',
    pth_ind3: '半導體製程 — 擴散爐溫控、CVD 製程溫度監控',
    pth_ind4: '熱處理 — 退火爐、淬火爐溫度記錄',
    pth_ind5: '食品加工 — 巴斯德殺菌、烘焙爐溫控（T型）',
    pth_ind6: '電動車電池製造 — 電池模組溫度監控',
    pth_faq1_q: 'K型和J型熱電偶有什麼差別，我該選哪種？',
    pth_faq1_a: 'K型適合一般工業環境（氧化氣氛，最高 1372°C），是市場最通用型號，備品取得容易。J型適合還原性或真空氣氛，最高 750°C，成本較低。射出成型廠多使用 K型；鐵基金屬熱處理有時選 J型。',
    pth_faq2_q: '熱電偶保護管材質怎麼選？',
    pth_faq2_a: '不鏽鋼（SUS304/316）：一般工業環境，抗腐蝕，100-1100°C。碳化矽（SiC）：鋁液熔煉、高腐蝕性環境，耐衝擊，最高 1600°C。高純度陶瓷（Al₂O₃）：高溫、腐蝕性氣體環境，最高 1700°C。',
    pth_faq3_q: '欣晨工業的熱電偶能否搭配我現有的溫控器使用？',
    pth_faq3_a: '可以。欣晨熱電偶符合 IEC 584 國際標準，與市售各品牌溫控器（Omron、Yokogawa、Shinko 等）相容。訂購時請告知溫控器型號，我們協助確認接線方式。',
    pth_faq4_q: '客製化熱電偶的交期多久？',
    pth_faq4_a: '標準型號庫存品 3-5 工作日。客製化尺寸通常 7-14 工作日。請提供應用場景、溫度範圍、安裝空間等資訊，我們協助選型。',
    pth_rel1_title: '工業加熱器', pth_rel1_desc: '搭配熱電偶使用的加熱元件',
    pth_rel2_title: '碳化矽保護管', pth_rel2_desc: '高溫熔液場景的保護管',
    pth_cta_title: '需要熱電偶的規格與報價？',
    pth_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    // ── product-heater.html ──
    phe_eyebrow: 'INDUSTRIAL HEATERS', phe_title: '工業加熱器', phe_breadcrumb: '工業加熱器',
    phe_lead: '精密加熱元件，從射出成型到鋁鑄造，最高工作溫度 1200°C，支援全客製化規格。',
    phe_spec1_label: '最高工作溫度', phe_spec1_val: '1,200°C',
    phe_spec2_label: '功率範圍', phe_spec2_val: '50W ～ 10kW',
    phe_spec3_label: '電壓規格', phe_spec3_val: '110V / 220V / 380V（可客製）',
    phe_spec4_label: '加熱管材質', phe_spec4_val: '鎳鉻合金（Ni-Cr）/ FeCrAl / Kanthal A-1',
    phe_spec5_label: '絕緣材質', phe_spec5_val: '氧化鎂（MgO）粉末填充',
    phe_spec6_label: '外護材質', phe_spec6_val: 'SUS304 / SUS316 不鏽鋼',
    phe_spec7_label: '安裝方式', phe_spec7_val: '法蘭式 / 螺牙式 / 插入式',
    phe_spec8_label: '客製選項', phe_spec8_val: '外徑、長度、引線位置、功率均可客製',
    phe_type1_name: '射出成型機加熱圈（加熱帶）', phe_type1_desc: '環繞料管外側，提供均勻加熱，適用各種射出成型機規格。',
    phe_type2_name: '工業加熱棒', phe_type2_desc: '插入式設計，精確點加熱，適用模具預熱、熱流道系統。',
    phe_type3_name: '陶瓷加熱器', phe_type3_desc: '高溫耐衝擊，適用工業爐、半導體設備、退火爐等場景。',
    phe_type4_name: '紅外線加熱器', phe_type4_desc: '非接觸式加熱，適用塑膠預熱、食品加工、表面處理。',
    phe_type5_name: '工業爐加熱管', phe_type5_desc: '高功率耐高溫設計，適用鋁鑄造澆注系統、熱處理爐。',
    phe_ind1: '射出成型（Injection Molding）— 料管加熱圈、模具加熱棒',
    phe_ind2: '鋁合金鑄造（Die Casting）— 澆注系統加熱管、保溫爐加熱元件',
    phe_ind3: '半導體製程 — 擴散爐、氧化爐周邊加熱系統',
    phe_ind4: '工業熱處理 — 退火爐、回火爐、烘箱加熱元件',
    phe_ind5: '電動車製造 — 電池極片烘乾、電機定子預熱',
    phe_faq1_q: '欣晨工業的加熱器最高可承受幾度？',
    phe_faq1_a: '工業電熱管最高工作溫度為 1200°C（鎳鉻合金材質）。陶瓷加熱器依型號可達 800-1200°C。紅外線加熱器通常在 400-700°C。請依實際使用環境選擇適當型號。',
    phe_faq2_q: '如何訂購客製化加熱器？',
    phe_faq2_a: '請電話 03-381-4497 或填寫線上詢問表單，說明：外徑規格、長度、電壓、功率、安裝方式、材質需求。我們承諾 1-2 個工作日回覆報價。',
    phe_faq3_q: '加熱圈和加熱棒有什麼差別？',
    phe_faq3_a: '加熱圈（加熱帶）環繞在料管外側，提供均勻的圓周加熱，是射出成型機標準配備。加熱棒為插入式設計，適合模具內部的精確點加熱。兩者可搭配熱電偶溫控系統使用。',
    phe_faq4_q: '交期多久？',
    phe_faq4_a: '標準品庫存規格通常 3-5 個工作日出貨。客製化規格依複雜程度 7-14 個工作日，急件可加急處理，請洽業務確認。',
    phe_rel1_title: '熱電偶', phe_rel1_desc: '搭配加熱器使用的溫度感測元件',
    phe_rel2_title: '一體式料管', phe_rel2_desc: '整合加熱圈的射出成型機料管',
    phe_cta_title: '需要工業加熱器的規格與報價？',
    phe_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    // ── product-sic-tube.html ──
    psic_eyebrow: 'SiC PROTECTION TUBES', psic_title: '碳化矽保護管', psic_breadcrumb: '碳化矽保護管',
    psic_lead: '高純度碳化矽（SiC），耐溫超過 1600°C，抗熱衝擊、抗氧化、抗腐蝕，適用半導體製程與鋁鑄造高溫環境。',
    psic_spec1_label: '材質', psic_spec1_val: '高純度碳化矽（SiC）',
    psic_spec2_label: '純度', psic_spec2_val: '> 99%',
    psic_spec3_label: '最高使用溫度', psic_spec3_val: '> 1,600°C（連續使用）',
    psic_spec4_label: '抗熱衝擊性', psic_spec4_val: '優異，可承受急冷急熱',
    psic_spec5_label: '抗氧化性', psic_spec5_val: '優（高溫氧化氣氛中）',
    psic_spec6_label: '抗腐蝕性', psic_spec6_val: '優（強酸鹼除外）',
    psic_spec7_label: '硬度', psic_spec7_val: 'HV 2,500（莫氏硬度 9+）',
    psic_spec8_label: '客製選項', psic_spec8_val: '外徑、內徑、長度、端部形狀均可客製',
    psic_type1_name: '反應燒結 SiC（RBSiC）', psic_type1_desc: '成本較低，適合鋁液熔煉等一般高溫保護場景。',
    psic_type2_name: '重結晶 SiC（ReSiC）', psic_type2_desc: '高純度、高強度，適合半導體擴散爐等超高溫製程。',
    psic_type3_name: '氮化矽結合 SiC（NSiC）', psic_type3_desc: '優異抗熱衝擊，適合急冷急熱頻繁的場景。',
    psic_ind1: '半導體製程 — 擴散爐（Diffusion Furnace）爐管保護、LPCVD 製程',
    psic_ind2: '鋁合金鑄造 — 熔融鋁液中熱電偶保護管、澆注導管',
    psic_ind3: '長晶爐 — 矽晶棒生長設備構件',
    psic_ind4: '陶瓷燒結爐 — 高溫燒結保護件',
    psic_ind5: '化工設備 — 耐腐蝕高溫管道保護',
    psic_faq1_q: '碳化矽保護管和不鏽鋼保護管有什麼差別？',
    psic_faq1_a: '不鏽鋼保護管上限約 1100-1200°C，在高溫下強度下降，且與鋁液接觸時容易被侵蝕。SiC 保護管耐溫超過 1600°C，在鋁液環境中化學惰性佳，使用壽命是不鏽鋼的 3-10 倍，是鋁鑄造廠的首選。',
    psic_faq2_q: '碳化矽保護管能否用於半導體製程中的氫氣氣氛？',
    psic_faq2_a: '在氧化氣氛下 SiC 性能優異。在還原性或氫氣氣氛下，高純度的重結晶 SiC（ReSiC）表現較好。請提供您的具體製程條件，我們協助選型。',
    psic_faq3_q: '如何訂購客製化碳化矽保護管？',
    psic_faq3_a: '請提供：外徑（mm）、內徑（mm）、長度（mm）、使用溫度、使用環境（氣氛、接觸介質）、數量。電話 03-381-4497 或線上詢問表單，我們 1-2 個工作日回覆報價。',
    psic_rel1_title: '熱電偶', psic_rel1_desc: '搭配SiC保護管使用的溫度感測器',
    psic_rel2_title: '耐火材料', psic_rel2_desc: '高溫爐體砌築材料',
    psic_cta_title: '需要碳化矽保護管的規格與報價？',
    psic_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    // ── product-refractory.html ──
    pref_eyebrow: 'REFRACTORY MATERIALS', pref_title: '耐火材料', pref_breadcrumb: '耐火材料',
    pref_lead: '耐火磚、耐火泥及定形耐火製品，耐溫達 1800°C，適用各類冶金爐、工業窯爐及高溫製程設備。',
    pref_spec1_label: '最高使用溫度', pref_spec1_val: '達 1,800°C（依材質）',
    pref_spec2_label: '耐火磚類型', pref_spec2_val: '高鋁磚 / 矽磚 / 鎂磚 / 碳化矽磚',
    pref_spec3_label: '不定形耐火材', pref_spec3_val: '澆注料 / 可塑料 / 噴射料 / 塗抹料',
    pref_spec4_label: '抗壓強度', pref_spec4_val: '高（依材質規格）',
    pref_spec5_label: '熱傳導率', pref_spec5_val: '低（良好隔熱性）',
    pref_spec6_label: '熱穩定性', pref_spec6_val: '優（急熱急冷耐性強）',
    pref_spec7_label: '客製服務', pref_spec7_val: '依爐型設計提供砌築方案',
    pref_type1_name: '高鋁磚', pref_type1_desc: 'Al₂O₃含量>45%，耐溫1400-1800°C，強度高，適用電弧爐、感應爐內壁。',
    pref_type2_name: '矽磚', pref_type2_desc: 'SiO₂含量>93%，耐溫1600-1700°C，適用焦爐、玻璃窯爐。',
    pref_type3_name: '鎂磚', pref_type3_desc: 'MgO含量>85%，耐鹼性熔渣，適用鋼鐵冶煉轉爐、電弧爐爐底。',
    pref_type4_name: '碳化矽耐火磚', pref_type4_desc: '高強度、高熱導率，適用燃燒器套管、窯車棚板。',
    pref_type5_name: '不定形耐火材（澆注料）', pref_type5_desc: '可澆注成型任意形狀，適合異型爐膛修補與整體砌築。',
    pref_ind1: '鋼鐵冶煉 — 電弧爐、轉爐、鋼包爐膛砌築',
    pref_ind2: '有色金屬冶煉 — 鋁、銅、鋅熔爐砌築',
    pref_ind3: '工業窯爐 — 陶瓷窯、玻璃窯、水泥窯',
    pref_ind4: '化工設備 — 高溫反應爐、燃燒爐',
    pref_ind5: '鑄造業 — 沖天爐、感應爐、澆注槽',
    pref_faq1_q: '該如何選擇耐火磚的材質？',
    pref_faq1_a: '主要考慮：①使用溫度（確認所需耐火度）；②爐渣性質（酸性渣選矽磚，鹼性渣選鎂磚）；③機械負荷（高負荷選高鋁磚）；④施工方式（整體砌築選定形磚，異型部位選澆注料）。我們提供免費諮詢，協助選材。',
    pref_faq2_q: '耐火材料如何保養？',
    pref_faq2_a: '避免急速升降溫（遵守烘爐曲線）；定期檢查磚縫是否滲漏；發現局部損壞應即時修補。欣晨提供爐後維護諮詢服務。',
    pref_faq3_q: '請問最小訂購量是多少？',
    pref_faq3_a: '請電話 03-381-4497 洽詢，依產品型號與規格而定。標準規格品可少量訂購，大宗採購有優惠。',
    pref_rel1_title: '碳化矽保護管', pref_rel1_desc: '爐內高溫保護管件',
    pref_rel2_title: '工業加熱器', pref_rel2_desc: '窯爐加熱元件',
    pref_cta_title: '需要耐火材料的規格與報價？',
    pref_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    // ── product-integrated-barrel.html ──
    pib_eyebrow: 'INTEGRATED BARRELS', pib_title: '一體式料管', pib_breadcrumb: '一體式料管',
    pib_lead: '一體成型無接縫設計，消除傳統料管滲漏風險。雙金屬合金與氮化合金材質，高耐磨、高耐腐蝕。',
    pib_spec1_label: '設計特點', pib_spec1_val: '一體成型，無接縫，消除滲漏風險',
    pib_spec2_label: '材質選項', pib_spec2_val: '氮化鋼 / 雙金屬合金 / 高速鋼塗層',
    pib_spec3_label: '氮化鋼硬度', pib_spec3_val: 'HRC 60–65',
    pib_spec4_label: '雙金屬合金硬度', pib_spec4_val: 'HRC 60–68',
    pib_spec5_label: '高速鋼塗層硬度', pib_spec5_val: 'HRC 62–66',
    pib_spec6_label: '適用材料', pib_spec6_val: '一般塑料 / 玻纖填充料 / 工程塑料 / 腐蝕性材料（PVC）',
    pib_spec7_label: '客製選項', pib_spec7_val: '內徑、外徑、長度、加熱圈整合均可客製',
    pib_type1_name: '氮化鋼料管', pib_type1_desc: '適合一般塑料，高耐磨，表面硬度 HRC 60-65，CP 值高。',
    pib_type2_name: '雙金屬合金料管', pib_type2_desc: '內壁鑄入高合金耐磨層，適合玻纖、礦填充等磨耗性高的工程塑料。',
    pib_type3_name: '高速鋼塗層料管', pib_type3_desc: '適合 PVC、阻燃料等腐蝕性材料，兼顧耐磨與耐腐蝕。',
    pib_ind1: '射出成型工廠 — 各種塑膠製品生產',
    pib_ind2: '汽車零件製造 — 高強度工程塑料射出',
    pib_ind3: '電子零件 — 精密小型射出成型',
    pib_ind4: '包裝材料 — 高速射出、高產能需求',
    pib_ind5: '醫療器材 — 高潔淨度要求料管',
    pib_faq1_q: '一體式料管和普通料管有什麼差別？',
    pib_faq1_a: '一體式料管採用整體鑄造或鍛造，不存在接縫。傳統分段式料管有多處接縫，長期使用後容易因熱脹冷縮導致滲料、漏料。一體式設計大幅提升密封性，減少換模停機次數，延長使用壽命。',
    pib_faq2_q: '如何知道我的射出成型機需要更換料管？',
    pib_faq2_a: '以下情況需考慮更換：①螺桿與料管間隙過大導致射出壓力下降；②產品產生燒焦或色差；③料管外壁出現裂縫或凹痕。欣晨工程師可協助現場診斷。',
    pib_faq3_q: '雙金屬料管比氮化料管貴多少，值得嗎？',
    pib_faq3_a: '雙金屬料管成本約為氮化料管的 1.5-2.5 倍。但若加工材料含有玻纖、礦物填充劑，氮化料管壽命可能只有雙金屬的 1/3-1/5。長期計算，雙金屬料管換管次數少、停機成本低，通常是更經濟的選擇。',
    pib_rel1_title: '工業加熱器', pib_rel1_desc: '料管配套加熱圈',
    pib_rel2_title: '熱電偶', pib_rel2_desc: '料管溫度監控',
    pib_cta_title: '需要一體式料管的規格與報價？',
    pib_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    // ── product-graphite-tube.html ──
    pgt_eyebrow: 'NANO-BUBBLE FLUID MODULE', pgt_title: '高濃度奈米氣泡流體模組', pgt_breadcrumb: '高濃度奈米氣泡流體模組',
    pgt_lead: '氣泡尺寸 < 100nm，產生高濃度奈米氣泡流體，應用於半導體製程、生醫設備與液冷系統，達到節能、高密度、免化學添加的潔淨效果。',
    pgt_spec1_label: '氣泡尺寸', pgt_spec1_val: '< 100 nm',
    pgt_spec2_label: '氣泡濃度', pgt_spec2_val: '> 10⁸ 顆/mL（高密度）',
    pgt_spec3_label: '適用介質', pgt_spec3_val: '純水、半導體製程用水、冷卻液、生醫用水',
    pgt_spec4_label: '氣體來源', pgt_spec4_val: 'N₂ / O₂ / CO₂ / 空氣（依應用需求選配）',
    pgt_spec5_label: '安裝方式', pgt_spec5_val: '管路在線式安裝，相容現有製程水路與液冷迴路',
    pgt_spec6_label: '功能', pgt_spec6_val: '物理性氣泡崩潰產生微衝擊力，分解污染物與生物膜，免化學添加',
    pgt_spec7_label: '客製選項', pgt_spec7_val: '流量、濃度、氣體種類均可依產線需求客製',
    pgt_type1_name: '半導體製程型', pgt_type1_desc: '適用晶圓清洗與製程用水系統，提升清潔效率並降低化學品使用量。',
    pgt_type2_name: '液冷系統型', pgt_type2_desc: '安裝於資料中心或設備液冷迴路，強化散熱效率並抑制管路結垢與生物膜。',
    pgt_type3_name: '生醫設備型', pgt_type3_desc: '應用於生醫儀器清洗與滅菌輔助流程，提供溫和且無化學殘留的潔淨方案。',
    pgt_ind1: '半導體製造 — 晶圓清洗、製程用水水質提升、後段製程清洗',
    pgt_ind2: '生醫產業 — 醫療設備清洗、實驗室用水純化輔助',
    pgt_ind3: '資料中心液冷 — 伺服器液冷迴路散熱效率提升、防垢抑菌',
    pgt_ind4: '精密電子製造 — 高階電子零組件清洗、無化學殘留要求製程',
    pgt_faq1_q: '什麼是奈米氣泡？與一般微氣泡有何不同？',
    pgt_faq1_a: '奈米氣泡是直徑小於100nm的微小氣泡，在液體中帶負電位（zeta potential），不易上浮聚合，可長時間懸浮於流體中。相較於傳統微氣泡，奈米氣泡比表面積極大，與液體及顆粒物的接觸效率大幅提升，因此在清洗、傳質、散熱等應用上效果顯著。',
    pgt_faq2_q: '高濃度奈米氣泡流體模組可以應用在哪些領域？',
    pgt_faq2_a: '主要應用於三大領域：①半導體製程—晶圓清洗與製程用水水質提升；②生醫產業—醫療設備清洗與滅菌輔助；③液冷系統—提升資料中心與設備液冷迴路的散熱效率，並抑制管路結垢與生物膜增生。',
    pgt_faq3_q: '奈米氣泡如何達到免化學添加的清潔效果？',
    pgt_faq3_a: '奈米氣泡在液體中崩潰時會釋放局部能量並產生微衝擊力，可物理性鬆動並剝離附著於表面的微粒污染物與生物膜，無需依賴化學藥劑即可達到清潔效果，大幅降低化學品採購與廢液處理成本，同時更友善環境。',
    pgt_faq4_q: '導入高濃度奈米氣泡流體模組需要哪些條件？如何維護？',
    pgt_faq4_a: '模組採管路在線式安裝，相容大部分既有製程用水或液冷管路，僅需接入水源與電源即可運作。日常維護僅需定期更換濾芯，無需補充化學藥劑，大幅簡化維護流程並降低營運成本。歡迎告知您的流量與場域需求，欣晨工程師協助選型評估。',
    pgt_rel1_title: '碳化矽保護管', pgt_rel1_desc: '半導體與高溫製程關鍵耗材',
    pgt_rel2_title: '熱電偶', pgt_rel2_desc: '精密溫度監控應用',
    pgt_cta_title: '需要高濃度奈米氣泡流體模組的規格與報價？',
    pgt_cta_desc: '告訴我們您的使用環境、規格需求與數量，欣晨工業工程師 1-2 個工作日內為您提供最適方案。',

    pp_qa_title: '品質保證', pp_qa_lead: '每一項產品皆通過嚴格品管流程，從原材料選用到成品測試，全程品質追蹤。',
    pp_qa_1_title: '原料嚴選', pp_qa_1_desc: '所有產品均選用業界認證的高純度原材料，確保化學成分與物理性能符合嚴苛工業應用標準。',
    pp_qa_2_title: '出廠檢測', pp_qa_2_desc: '每批產品出廠前均進行尺寸、耐溫、強度等多項性能檢測，提供完整的檢驗報告，確保品質一致性。',
    pp_qa_3_title: '客製規格', pp_qa_3_desc: '提供非標準尺寸客製化服務，依據客戶設備規格特製生產，交期彈性配合，滿足多樣化應用需求。',
    pp_cta_title: '需要客製規格或報價？',
    pp_cta_desc: '告訴我們您的應用環境與規格需求，欣晨工業的產品工程師將為您提供最適合的材料建議與報價。',
    pp_cta_btn: '立即詢價',

    // Services page
    srv_eyebrow_top: 'SERVICES', srv_eyebrow_cta: 'START PROJECT',
    srv_page_title: '欣晨工業 服務項目',
    srv_page_lead: '欣晨工業有限公司七大自動化服務，從數位規劃、機械手臂整合、視覺檢測，到設備智能化升級、奈米氣泡流體應用，一站式滿足您的製造需求。',
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
    srv_d7_num: 'SERVICE 07', srv_d7_tag: 'Nano-Bubble Application', srv_d7_title: '高濃度奈米氣泡流體產業應用',
    srv_d7_desc: '針對半導體製程用水、生醫設備清洗、資料中心液冷等場域，導入高濃度奈米氣泡流體模組，提供選型評估、管路整合安裝與效能驗證，以物理性奈米氣泡取代化學藥劑，達成節能、免化學添加的製程升級。',
    srv_d7_p1: '半導體製程用水品質提升與晶圓清洗輔助', srv_d7_p2: '生醫設備清洗滅菌輔助，降低化學藥劑依賴',
    srv_d7_p3: '資料中心液冷系統散熱效率提升、抑制管路結垢', srv_d7_p4: '免化學添加，降低廢液處理成本與環境負擔', srv_d7_btn: '諮詢此服務',
    srv_cta_title: '準備啟動您的自動化專案？',
    srv_cta_desc: '無論是全新產線規劃還是既有設備升級，欣晨工業的工程師團隊都能提供最適合的解決方案。',
    srv_cta_btn: '立即洽詢',

    // Technology page
    tech_eyebrow_top: 'TECHNOLOGY INSIGHT',
    tech_eyebrow_cta: 'COLLABORATE WITH US',
    tech_page_title: '欣晨工業 新技術討論',
    tech_page_lead: '從半導體製程到人形機器人，探討欣晨工業精密零件與耐高溫材料在六大前沿領域中的關鍵應用與技術貢獻。',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: 'Semiconductor', tech_d1_title: '半導體製程',
    tech_d1_desc: '半導體晶圓製程需要在超高溫、強腐蝕性環境中精準操控熔融金屬與化學材料，同時對製程用水與清洗品質有極高要求。欣晨的碳化矽（SiC）保護管以其卓越的耐熱衝擊性與化學惰性，成為擴散爐管、長晶設備等核心製程設備的關鍵耗材；高濃度奈米氣泡流體模組則用於晶圓清洗與製程用水品質提升，達到節能且免化學添加的潔淨效果。',
    tech_d1_p1: 'SiC保護管：耐溫達1600°C，抗氧化與抗腐蝕', tech_d1_p2: '高濃度奈米氣泡流體模組：氣泡尺寸<100nm，用於晶圓清洗與製程用水品質提升',
    tech_d1_p3: '一體式料管：確保熔融矽材輸送的純淨無汙染', tech_d1_p4: '客製化尺寸，適配各式長晶爐與PECVD設備', tech_d1_btn: '諮詢應用方案',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: 'Electric Vehicle', tech_d2_title: '電動車',
    tech_d2_desc: '電動車的電池模組、電機與功率電子元件對熱管理有嚴苛要求。欣晨的耐火材料與高精度陶瓷零件，廣泛應用於電池包結構防護、電機定子絕緣及鑄造廠鋁合金電機殼的生產製程中，確保材料在高溫、高壓環境下的長期穩定性。',
    tech_d2_p1: '電池模組防火隔熱板：阻燃耐高溫結構保護', tech_d2_p2: '鋁合金鑄造製程保護管：電機殼體生產必備',
    tech_d2_p3: '陶瓷熱電偶：精確監控電機運行溫度', tech_d2_p4: '耐高溫絕緣材料：適用功率模組（IGBT/SiC MOSFET）', tech_d2_btn: '諮詢應用方案',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'Silicon Photonics', tech_d3_title: '矽光子',
    tech_d3_desc: '矽光子技術將光學元件整合於矽基板上，實現高速光通訊與AI加速運算。欣晨提供應用於光子晶片封裝製程的高精度陶瓷載具、耐高溫夾治具及製程保護零件，確保晶片在鍵合（Bonding）、退火（Annealing）等精密工序中的結構完整性。',
    tech_d3_p1: '高精度陶瓷定位夾具：光纖陣列對準夾持', tech_d3_p2: '耐高溫製程載具：鍵合製程穩定承載',
    tech_d3_p3: '氧化鋁陶瓷隔熱板：退火爐製程熱均勻分佈', tech_d3_p4: '客製化規格，配合晶圓廠製程節點需求', tech_d3_btn: '諮詢應用方案',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'Humanoid Robot', tech_d4_title: '人形機器人',
    tech_d4_desc: '人形機器人的關節傳動、末端執行器與感知系統需要兼顧輕量化與高精度的零件製造。欣晨憑藉30年精密加工經驗，為人形機器人製造商提供鋁合金結構件、精密傳動套筒及耐磨陶瓷元件，以嚴格的尺寸管控確保機器人的動作精度與長壽命。',
    tech_d4_p1: '關節傳動精密套筒：保持動作重複定位精度', tech_d4_p2: '輕量鋁合金結構件：降低本體重量，提升靈活性',
    tech_d4_p3: '耐磨陶瓷導向件：延長關節使用壽命', tech_d4_p4: '高精度公差管控：±0.01mm 級別加工能力', tech_d4_btn: '諮詢應用方案',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: 'Quantum Computing', tech_d5_title: '量子電腦',
    tech_d5_desc: '量子電腦的稀釋冷凍機需將量子比特維持在接近絕對零度（15 mK）的環境中，對零件的熱傳導性、電磁干擾防護與超精密加工有極端要求。欣晨提供適用於低溫環境的高純度無氧銅零件與精密陶瓷隔熱元件，協助量子計算設備製造商突破製程瓶頸。',
    tech_d5_p1: '高純度無氧銅（OFC）精密零件：優異導熱與導電性', tech_d5_p2: '陶瓷隔熱結構件：低溫環境下的熱絕緣設計',
    tech_d5_p3: '超精密加工：表面粗糙度 Ra ≤ 0.4μm', tech_d5_p4: '嚴格潔淨度管控：避免量子態干擾汙染', tech_d5_btn: '諮詢應用方案',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / Drone', tech_d6_title: '無人機',
    tech_d6_desc: '無人機追求極致輕量化與結構強度的平衡，電機座、傳動軸、雲台架等關鍵零件需要精密加工與嚴格品質管控。欣晨為無人機廠商提供高強度鋁合金機構件、碳纖維複合材料嵌件及客製化工裝治具，支援從原型開發到量產的全週期製造需求。',
    tech_d6_p1: '航空鋁合金（7075-T6）輕量化結構件', tech_d6_p2: '電機固定座：精密孔位確保馬達同心度',
    tech_d6_p3: '碳纖維複合材料嵌入式金屬螺套', tech_d6_p4: '快速打樣與小批量量產彈性服務', tech_d6_btn: '諮詢應用方案',
    tech_cta_title: '探索精密材料在您領域的應用？',
    tech_cta_desc: '欣晨工業的技術團隊歡迎與各前沿科技領域的廠商共同探討材料解決方案，一起推動技術邊界。',
    tech_cta_btn: '立即聯繫技術團隊',

    // Careers page
    career_page_title: '欣晨工業 人力資源',
    career_page_lead: '加入欣晨工業有限公司，與我們一同傳承30年精密製造工藝，共同迎接自動化與新材料時代的機遇與挑戰。',
    career_eyebrow_top: 'CAREERS',
    career_apply_label: 'Email 應徵',
    career_apply_note: '請於主旨標明「應徵職位名稱＋姓名」，並附上完整履歷與自傳',
    career_apply_btn: '立即應徵',
    career_eyebrow_jobs: 'OPEN POSITIONS',
    career_jobs_title: '目前開缺職位',
    career_job1_tag: '機械設計', career_job1_title: '資深機械設計工程師',
    career_job1_req1: '以 Solid Edge / SolidWorks 進行精密零件、模組及治具設計',
    career_job1_req2: '協同製造部門進行設計驗證、圖面管控與加工工藝改善',
    career_job1_req3: '學歷：大專以上，機械工程相關科系，具5年以上設計實務',
    career_job1_req4: '熟悉 GD&T 公差設計與精密加工工藝者優先',
    career_job2_tag: '業務行銷', career_job2_title: '產品業務工程師',
    career_job2_req1: '開發與維護國內外客戶，推廣精密零件與自動化解決方案',
    career_job2_req2: '解讀客戶技術規格，提供報價、技術支援及售後服務',
    career_job2_req3: '學歷：大專以上，機械或工業工程背景佳',
    career_job2_req4: '具備中英文或日文溝通能力者優先',
    career_job3_tag: '自動化技術', career_job3_title: '自動化設備工程師',
    career_job3_req1: '規劃、設計及整合自動化生產設備與產線系統',
    career_job3_req2: 'PLC 程式設計（三菱 iQ-F / iQ-R）與 HMI 整合開發',
    career_job3_req3: '學歷：大專以上，電機、機電或自動控制相關科系',
    career_job3_req4: '具機械手臂整合或視覺系統應用經驗者尤佳',
    career_job4_tag: '採購供應', career_job4_title: '供應鏈管理師',
    career_job4_req1: '供應商開發與評鑑、詢比議價及交期管控',
    career_job4_req2: '物料採購計劃、庫存管理與物流協調',
    career_job4_req3: '學歷：大專以上，工管、供應鏈或工業工程相關科系',
    career_job4_req4: '熟悉 ERP 系統操作，具製造業採購經驗者優先',
    career_job5_tag: '技術製造', career_job5_title: '組立技師',
    career_job5_req1: '依工程圖面與 SOP 進行精密機械零件組立作業',
    career_job5_req2: '組裝後功能測試、精度量測及品質自主確認',
    career_job5_req3: '學歷：高中職以上，機械相關科系尤佳',
    career_job5_req4: '具精密組裝或電氣配線經驗者優先，歡迎訓練生',
    career_eyebrow_benefits: 'EMPLOYEE BENEFITS',
    career_ben_title: '員工福利',
    career_ben1_title: '全勤獎金', career_ben1_desc: '每月全勤出席者額外發放全勤獎金，獎勵敬業精神與穩定的工作投入。',
    career_ben2_title: '年終獎金', career_ben2_desc: '年終依公司績效及個人貢獻發放年終獎金，與員工共享企業成長果實。',
    career_ben3_title: '保險', career_ben3_desc: '勞工保險、全民健康保險及團體意外險，由公司依法足額投保，保障無憂。',
    career_ben4_title: '免費供餐', career_ben4_desc: '公司提供員工午餐，減輕生活負擔，讓同仁無後顧之憂，專注工作。',
    career_ben5_title: '國內旅遊', career_ben5_desc: '定期舉辦國內員工旅遊活動，增進同仁情誼，凝聚團隊向心力。',
    career_ben6_title: '生日禮金', career_ben6_desc: '員工生日當月贈送生日禮金，表達公司對每一位夥伴的重視與真誠關懷。',
    career_ben7_title: '三節獎金', career_ben7_desc: '端午節、中秋節、農曆春節三大節慶均發放節慶獎金，感謝員工辛勤付出。',
    career_ben8_title: '尾牙', career_ben8_desc: '每年舉辦尾牙聚餐，感謝全體員工一年辛勞，共同歡慶豐收、展望新年。',
    career_eyebrow_join: 'JOIN OUR TEAM',
    career_cta_title: '準備好加入欣晨了嗎？',
    career_cta_desc: '將您的履歷寄送至 hc3814497@gmail.com，我們期待與您共同創造欣晨的下一個50年。',
    career_cta_btn: '立即投遞履歷',

    // Contact page
    contact_eyebrow_top: 'CONTACT US',
    contact_page_title: '聯絡欣晨工業',
    contact_page_lead: '無論是產品詢價、技術合作或服務洽談，歡迎透過以下方式與欣晨工業有限公司聯繫，我們將於1-2個工作日內回覆。',
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

    faq_title: '常見問題', faq_lead: '快速找到您需要的答案。更多問題歡迎直接', faq_contact_link: '聯絡我們',

    idx_eyebrow_genchi: 'GENCHI GENBUTSU',
    genchi_title: '現地現物',
    genchi_desc: '豐田的核心原則：不相信二手報告，要親自到現場，用雙眼確認、用雙手丈量。欣晨工業在每個專案啟動前，工程師必定親赴客戶廠房，深入理解真實的生產環境、設備空間限制與作業員習慣。唯有真正讀懂現場，才能設計出真正適用的自動化系統。',
    genchi_spec1_label: '現場', genchi_spec1_val: '需求訪談與動線觀察',
    genchi_spec2_label: '量測', genchi_spec2_val: '設備空間與干涉評估',
    genchi_spec3_label: '分析', genchi_spec3_val: '生產節拍（Takt Time）實地計測',
    genchi_cta: '了解我們的做法', genchi_img_tag: '現地現物',

    idx_eyebrow_kaizen: 'KAIZEN',
    kaizen_title_1: '改善', kaizen_title_2: '永無止境的精益之路',
    kaizen_desc: '改善不是一次性的革命，而是每天積累的微進化。欣晨工業將Kaizen精神落實在每一個設計環節：從縮短換線時間（SMED）、導入防呆裝置（Poka-yoke），到建立標準作業程序（SOP）。我們不停地問：「這裡還能更好嗎？」，直到找到答案為止。',
    kaizen_spec1_val: '快速換模設計，縮短換線停機',
    kaizen_spec2_label: '防呆', kaizen_spec2_val: 'Poka-yoke 機構，從源頭杜絕錯誤',
    kaizen_spec3_label: '標準化', kaizen_spec3_val: 'SOP 建立，確保製程一致性',
    kaizen_cta: '查看自動化服務', kaizen_img_tag: '改善',

    marquee_1: '半導體製程客戶', marquee_2: '鋁鑄造廠', marquee_3: '電動車零件製造商',
    marquee_4: '精密機械廠', marquee_5: '電子封裝廠', marquee_6: '化工設備廠',

    tech_lead: '以改善、防呆與標準化思維，持續突破製造效能的邊界。',
    tps_tag_1: '改善 × 半導體製程', tps_1_title: 'Kaizen文化在精密製程中的實踐',
    tps_1_desc: '半導體製程的微米級要求，正是Kaizen精神最需要的舞台。每一道工序的微小改善，累積成良率的持續突破。',
    tps_tag_2: 'JIT × 電動車生產', tps_2_title: 'JIT準時化生產在電動車廠的應用',
    tps_2_desc: '電動車零件種類龐雜，JIT的「必要時間、必要數量、必要品項」原則，是消除電池組裝線庫存浪費的關鍵工具。',
    tps_tag_3: '防呆設計 × 機械手臂', tps_3_title: 'Poka-yoke防呆設計讓機械手臂零失誤',
    tps_3_desc: '在機械手臂整合中建入防呆機構，讓夾爪錯誤、定位偏差在發生前就被制止，是實現零缺陷生產的核心設計邏輯。',
  },

  ja: {
    nav_home: 'ホーム', nav_about: '会社概要', nav_products: '製品情報',
    nav_services: 'サービス', nav_tech: '新技術', nav_careers: '採用情報',
    nav_contact: 'お問い合わせ',

    hero_badge: '精密自動化ソリューション · Since 1996',
    hero_h1_line1: '精密が駆動する、', hero_h1_line2: '未来を創る',
    hero_h2: '欣晨工業有限公司 — カイゼン・JIT・自働化を核に、精密自動化ソリューションを提供',
    cta_products: '製品を見る', cta_contact_ask: 'お問い合わせ',
    metric_years: '年の経験', metric_products: '製品ライン',
    metric_services: 'サービス項目', scroll: 'SCROLL',

    idx_eyebrow_tps: 'トヨタ生産方式（TPS）',
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
    prod_b_title: '高濃度ナノバブル流体モジュール',
    prod_b_desc: '高濃度のナノバブル流体を生成、気泡サイズ100nm未満。半導体プロセス用水、生体医療機器洗浄、液冷システムに応用。省エネ・高密度・化学薬品不使用で、化学薬品コストと環境負荷を大幅に削減。',
    prod_b_use: '半導体 / 生体医療 / 液冷', prod_b_merit: '省エネ・高密度・化学薬品不使用',
    spec_temp: '耐熱温度', spec_mat: '材質', spec_app: '用途',
    spec_purity: '気泡サイズ', spec_use: '使用目的', spec_merit: '優位性',
    spec_type: 'タイプ', spec_heat: '温度', spec_spec: '仕様', spec_model: '型番', spec_measure: '測定範囲', spec_industry: '業種',
    cta_spec: '仕様を見る',

    idx_eyebrow_services: '全方位オートメーション',
    srv_title: '総合自動化サービス',
    srv_lead: '7つのサービスで計画から納品まで、ワンストップで自動化ニーズに対応',
    srv_1_title: 'デジタルツイン自動化設計', srv_1_desc: '仮想ライン検証でリスク低減',
    srv_2_title: 'ロボットアーム応用',       srv_2_desc: '搬送・溶接・組立統合、経路計画',
    srv_3_title: '単機自動化設計製造',       srv_3_desc: '要件→設計→製造→調整、一貫対応',
    srv_4_title: '画像検査',                 srv_4_desc: '産業カメラ + AI欠陥検出・寸法測定',
    srv_5_title: '治具設計製造',             srv_5_desc: '高精度治具で品質一貫性向上',
    srv_6_title: '設備インテリジェント化',   srv_6_desc: '既存設備を PLC / HMI / IoT へアップグレード',
    srv_7_title: '高濃度ナノバブル流体産業応用', srv_7_desc: '半導体・生医・液冷を化学薬品不使用で導入',
    cta_learn: '詳しく見る', cta_all_services: 'すべてのサービスを見る',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    idx_eyebrow_tps_insights: 'TPSインサイト',
    tech_title: 'トヨタ哲学 × 精密製造の応用',
    tech_tag_semi: '半導体プロセス', tech_tag_ev: '電気自動車', tech_tag_robot: 'ヒューマノイドロボット',
    tech_1_title: '精密製造における材料の鍵',
    tech_1_desc: 'SiC保護管は半導体高温プロセスで重要な役割を担い、安定した熱環境と腐食防護を提供します。',
    tech_2_title: 'EV電池生産の熱管理革新',
    tech_2_desc: 'EV電池セル製造には精密な熱管理が必要です。欣晨のヒーターとセンサー素子が生産一貫性を確保します。',
    tech_3_title: 'ロボット関節精密加工',
    tech_3_desc: 'ヒューマノイドロボット関節には高精度製造が必要です。欣晨の治具設計が精密ソリューションを提供します。',
    cta_read_more: '続きを読む', cta_view_all_tech: 'すべての技術テーマを見る',

    idx_eyebrow_cta: '今すぐ始める',
    cta_banner_title: 'トヨタ哲学で生産ラインを最適化する準備はできましたか？',
    cta_banner_desc: '現場の課題をお聞かせください。欣晨工業のエンジニアが現地を訪問し、改善精神で最適なソリューションを設計します。',
    cta_contact_now: 'お問い合わせ',

    footer_nav_title: 'クイックナビ', footer_contact_title: '連絡先',
    footer_years: '30年の製造経験',
    footer_addr: '桃園市大園区中正東路三段490号',
    footer_tel: 'Tel：03-381-4497', footer_fax: 'Fax：03-381-4536',
    footer_tagline_1: '精密が駆動する', footer_tagline_2: '未来を創る',
    footer_est: 'Est. 1996 · 製造30年の歴史',

    about_banner_title: '欣晨工業 会社概要',
    about_banner_lead: '欣晨工業有限公司 — 30年の精密製造経験、桃園市大園区を拠点に台湾全土の産業顧客にサービスを提供。技術・品質・サービスを事業の礎に。',
    about_eyebrow_top: '会社概要',
    about_eyebrow_story: 'ストーリー',
    about_our_title: '欣晨工業について',
    about_desc_1: '欣晨工業有限公司（Hsin-Chan Industrial Co., Ltd.）は1996年に創業し、台湾桃園市大園区中正東路三段490号に位置しています。30年以上の積み重ねにより、欣晨工業は初期の産業用消耗品サプライヤーから、自動化設備の設計・製造・統合・アフターサービスを含む総合製造パートナーへと発展しました。',
    about_desc_2: '欣晨工業の中核製品は、炭化ケイ素保護管、高濃度ナノバブル流体モジュール、ヒーター、熱電対などの高温工業用消耗品です。また、デジタルツイン計画、ロボットアーム応用、画像検査などのインテリジェント自動化サービス分野にも継続的に拡大しています。欣晨工業のヒーターは最高使用温度1200°Cに対応し、射出成形、アルミ鋳造、工業炉など幅広いプロセスで使用されています。',
    about_desc_3: '現在に至るまで、欣晨工業は「精密・カスタム・サポート」という三つの核心を貫き、半導体・鋳造・電気自動車・精密機械などの産業に信頼性の高い製造ソリューションを提供しています。サービス範囲は台湾全島および日本・東南アジアに及び、中国語・日本語・英語の三言語対応が可能です。',
    about_desc_4: '欣晨工業はトヨタ生産方式（TPS）を経営の核心哲学とし、改善（Kaizen）、ジャストインタイム（JIT）、自働化（Jidoka）をあらゆる製造工程に徹底しています。欣晨工業は、継続的な改善と精密製造によってお客様に最大の生産効果を生み出し、共に工業4.0の智造時代を迎えられると信じています。',
    about_history_eyebrow: '歩みの歴史',
    about_tl_1_title: '会社設立', about_tl_1_desc: '桃園大園に設立。高温工業用消耗品の製造・供給に特化し、地元製造業顧客にサービスを提供。',
    about_tl_2_title: '製品ライン拡大', about_tl_2_desc: '炭化ケイ素保護管の生産技術を導入。サービス対象を半導体・鋳造業へと拡大。',
    about_tl_3_title: '工場拡張', about_tl_3_desc: 'ヒーターと熱電対の生産ラインを追加し、工場面積を拡張。年間生産能力と品質管理能力を向上。',
    about_tl_4_title: '自動化への転換', about_tl_4_desc: '自動化設備の設計・製造に進出。ロボットアーム統合、単機自動化、画像検査サービスを提供。',
    about_tl_5_title: 'インテリジェント化', about_tl_5_desc: 'デジタルツイン技術を導入し、既存設備のインテリジェント化を推進。工業4.0統合サービス会社へ。',
    about_eyebrow_philosophy: 'フィロソフィー',
    about_mgmt_title: '経営理念',
    about_mgmt_lead_1: '欣晨工業の経営哲学は、日本の京セラ株式会社創業者である', about_mgmt_name: '稲盛和夫', about_mgmt_lead_2: '氏の思想に深く影響を受けています。氏は終生、企業が存在する意義は構成員全員の物心両面の幸福を追求することにあり、それを基盤として人類と社会の進歩に貢献することだと信じていました。この信念は、今も欣晨工業が前進し続けるための座右の銘です。',
    about_mgmt_quote_main: '敬天愛人',
    about_mgmt_quote_sub: 'けいてんあいじん',
    about_mgmt_quote_cite: '稲盛和夫 — 京セラ株式会社、KDDI創業者',
    about_mgmt_c1_title: '利他の心', about_mgmt_c1_concept: '利他は利己に通ず',
    about_mgmt_c1_desc: '稲盛和夫は、真の成功は「他者を思う」利他の心から生まれると考えました。欣晨工業はお客様とのあらゆる対話において、製品を売ることではなく、「どの方案がお客様の生産に最も役立つか」を最優先に考えます。お客様に真の価値を創造することこそ、長期的なパートナーシップの礎です。',
    about_mgmt_c2_title: '敬天愛人', about_mgmt_c2_concept: '正道を歩み、誠実に人と接する',
    about_mgmt_c2_desc: '「敬天」とは自然と物事の本質的な法則に従い、近道や欺きを避けることを意味し、「愛人」とはすべての仲間、顧客、社員に対して真心で向き合うことを意味します。欣晨工業は誠実さと透明性の原則を堅持し、見積り、納期、品質の約束はすべて言行一致を貫き、お客様に疑念を残したまま帰らせることはありません。',
    about_mgmt_c3_title: '継続的な精進', about_mgmt_c3_concept: '誰にも負けない努力をする',
    about_mgmt_c3_desc: '稲盛六つの精進の第一条は「誰にも負けない努力をする」ことです。欣晨工業の技術者は日々現場で技術を磨き、「使えればいい」では満足せず、「最高」を追求します。図面設計から部品加工、機械の調整まで、すべての工程で昨日より少しでも精度を高めることを目指します。',
    about_mgmt_c4_title: '仕事は修行である', about_mgmt_c4_concept: '労働の中で魂を磨く',
    about_mgmt_c4_desc: '稲盛和夫は「仕事は魂を磨く最高の方法である」と語りました。製造業におけるすべての部品、すべての設備は、人の心血と意志の結晶です。欣晨工業は、仕事に全身全霊で取り組むことが、お客様への責任を果たすだけでなく、すべての社員が自己成長し人格を磨くための道であると信じています。',
    about_phil_title: '経営理念',
    about_phil_lead: '三大理念が欣晨の30年の安定した成長を支え、すべての顧客へのサービスにおける約束でもあります。',
    about_phil_1_title: '精密製造', about_phil_1_desc: '30年の製造技術の蓄積と厳格な品質管理体制により、すべての部品が基準を正確に満たします。原材料の入荷から完成品の出荷まで、全工程の品質追跡で安定した稼働を確保します。',
    about_phil_2_title: 'カスタムサービス', about_phil_2_desc: '要件分析から機構設計、生産・納品まで、一対一のカスタムサービスを提供。顧客の生産現場を深く理解し、最適な自動化ソリューションをお届けします。',
    about_phil_3_title: '技術サポート', about_phil_3_desc: '専門エンジニアチームによる現場調整と技術研修、充実したアフターサービス体制。納品後も継続的に技術支援を提供し、設備の長期安定稼働を保証します。',
    about_team_title: '経営チーム',
    about_team_lead: '豊富な業界経験を持つプロフェッショナルチームが、技術革新とサービス向上を継続的に推進します。',
    about_team_1_role: '総経理', about_team_1_desc: '会社全体の戦略立案と運営管理を担当。チームを率いて継続的に革新し、自動化設備製造分野に30年以上従事しています。',
    about_team_2_role: '技術長', about_team_2_desc: '研究開発部門を主導。高温材料工学と自動化機構設計を専門とし、半導体プロセス設備開発の豊富な経験を持ちます。',
    about_team_3_role: '営業部長', about_team_3_desc: '営業開発と顧客関係管理を統括。顧客ニーズを深く理解し、各産業の顧客に最適な自動化ソリューションを提供します。',
    about_eyebrow_cta: 'お問い合わせ',
    about_cta_title: '欣晨工業と共に、精密な未来を創造しましょう',
    about_cta_desc: '製品の見積もり、技術相談、プロジェクト協力など、欣晨工業有限公司の専門チームへお気軽にご連絡ください。1～2営業日以内にご返信いたします。',
    about_cta_btn: 'お問い合わせ',

    pp_eyebrow_top: '製品情報', pp_eyebrow_lineup: '製品ライン', pp_eyebrow_qa: '品質保証', pp_eyebrow_quote: 'お見積り依頼',
    pp_banner_title: '欣晨工業 製品情報',
    pp_banner_lead: '欣晨工業有限公司の6大高温工業用消耗品ラインは、半導体・鋳造・エネルギーなどの産業に、過酷な環境下でも信頼性の高い素材ソリューションを提供します。',
    pp_overview_title: '6つの製品ライン', pp_overview_lead: 'すべての製品は厳格な品質管理を経ており、高温・腐食性・精密工業環境に対応しています。',
    pp_p1_tag: '射出成形消耗品', pp_p1_title: '一体型バレル',
    pp_p1_desc: '一体成形プロセスを採用し、継ぎ目のない設計により溶湯漏れのリスクを大幅に低減。アルミダイカスト、マグネシウム合金ダイカストなど各種非鉄金属の射出成形プロセスに広く使用されています。',
    pp_p1_s1: '材質：窒化鋼', pp_p1_s2: '硬度：HRC 60–65', pp_p1_s3: 'カスタムサイズ対応', pp_p1_btn: '見積依頼',
    pp_p1_app: 'ダイカスト機（宇部/東芝/芝浦）/ 射出成形', pp_p1_mat: 'SKD61 工具鋼', pp_p1_vtag: '一体型バレル',
    pp_p2_tag: '高温プロセス消耗品', pp_p2_title: '炭化ケイ素保護管',
    pp_p2_desc: '高純度炭化ケイ素（SiC）製で、耐熱温度1600°C超、優れた耐腐食性を備えています。半導体プロセス炉管、アルミ溶解、その他各種高温工業用途に広く使用されています。',
    pp_p2_s1: '耐熱：＞1600°C', pp_p2_s2: '材質：高純度 SiC', pp_p2_s3: '耐熱衝撃・耐食性', pp_p2_btn: '見積依頼',
    pp_p2_app: '半導体 / 鋳造業', pp_p2_mat: '高純度SiC', pp_p2_vtag: 'SiC保護管 · 1600°C',
    pp_p3_tag: '窯炉工業消耗品', pp_p3_title: '耐火材料',
    pp_p3_desc: '各種高温窯炉用の耐火レンガ、キャスタブル耐火材、断熱ウールなどの材料を提供。優れた断熱・保温性能により窯炉の使用寿命を延ばし、エネルギー損失を低減します。',
    pp_p3_s1: '耐熱：材質により最大1800°C', pp_p3_s2: '高圧縮強度・低熱伝導', pp_p3_s3: '多種材質・規格から選択可能', pp_p3_btn: '見積依頼',
    pp_p3_type: '耐火レンガ / キャスタブル / 断熱ウール', pp_p3_app: '窯炉 / 溶解炉 / 熱処理炉', pp_p3_temp: '1200°C～1800°C', pp_p3_vtag: '耐火材料',
    pp_p4_tag: '半導体プロセスモジュール', pp_p4_title: '高濃度ナノバブル流体モジュール',
    pp_p4_desc: '高濃度のナノバブル流体を生成、気泡サイズ100nm未満。半導体プロセス用水、生体医療機器洗浄、液冷システムに応用。省エネ・高密度・化学薬品不使用。',
    pp_p4_s1: '気泡サイズ：100nm未満の高濃度ナノバブル', pp_p4_s2: '応用：半導体 / 生体医療 / 液冷システム', pp_p4_s3: '優位性：省エネ・高密度・化学薬品不使用', pp_p4_btn: '見積依頼',
    pp_p4_use: '半導体 / 生体医療 / 液冷', pp_p4_merit: '省エネ / 高密度 / 化学薬品不使用', pp_p4_vtag: 'ナノバブル · <100nm',
    pp_p5_tag: '精密温度制御部品', pp_p5_title: 'ヒーター',
    pp_p5_desc: '炭化ケイ素発熱体、シリコンカーバイドロッド、二珪化モリブデンヒーターなど、各種規格の工業用電熱部品を提供。お客様のご要望に応じてカスタム仕様に対応し、高温炉管、熱処理設備、各種工業窯炉に適しています。',
    pp_p5_s1: '耐熱：タイプにより最大1200°C', pp_p5_s2: '多種出力規格（50W–10kW）', pp_p5_s3: 'カスタム形状・配線方式', pp_p5_btn: '見積依頼',
    pp_p5_type: 'SiC棒 / MoSi₂ / 白金線', pp_p5_heat: '最大1800°C', pp_p5_spec: '鉄鋼業 / ガラス業 / 鋳造業', pp_p5_vtag: 'ヒーター',
    pp_p6_tag: '精密計測部品', pp_p6_title: '熱電対',
    pp_p6_desc: '工業用温度センサーとして、K型・J型・R型・S型・B型など多種類の規格を提供。各種高温プロセスの温度測定に適しており、応答速度が速く精度も高い上、保護管と組み合わせることで耐久性がさらに向上します。',
    pp_p6_s1: '測温範囲：−200°C ～ +1800°C', pp_p6_s2: '多種型番・保護管素材', pp_p6_s3: 'IEC / JIS 規格適合', pp_p6_btn: '見積依頼',
    pp_p6_model: 'K / J / R / S / B タイプ', pp_p6_measure: '最大1750°C', pp_p6_spec: '標準 / カスタム', pp_p6_vtag: '熱電対',

    // ── 製品詳細ページ共通 (Product Detail Pages Shared) ──
    pd_eyebrow_specs: '仕様', pd_specs_title: '製品仕様',
    pd_custom_title: 'カスタム仕様をご希望ですか？', pd_custom_desc: '欣晨工業ではフルカスタムサービスを提供しています。ご要望をお知らせいただければ、エンジニアが1～2営業日以内にご返信いたします。',
    pd_contact_btn: 'お問い合わせ', pd_contact_tel_label: '電話：', pd_contact_email_label: 'メール：',
    pd_contact_hours_label: '営業時間：', pd_contact_hours_val: '月曜～金曜 8:00～17:30',
    pd_eyebrow_types: '製品タイプ', pd_types_title: '製品タイプ',
    pd_eyebrow_industries: '用途産業', pd_industries_title: '用途産業',
    pd_eyebrow_faq: 'FAQ', pd_faq_title: 'よくある質問',
    pd_eyebrow_related: '関連製品', pd_related_title: '関連製品',
    pd_viewall: '全製品を見る', pd_viewall_desc: '6つの高温工業用消耗品ライン',
    pd_eyebrow_quote: 'お見積り依頼', pd_quote_btn: '今すぐお見積り',

    // ── product-thermocouple.html ──
    pth_eyebrow: '熱電対', pth_title: '熱電対', pth_breadcrumb: '工業用熱電対',
    pth_lead: 'K、J、T、E、R、S、B型まで全シリーズの工業用熱電対を取り揃え、測温範囲は-200°C～+1820°C、IEC 584国際規格に準拠しています。',
    pth_spec1_label: '対応タイプ', pth_spec1_val: 'K / J / T / E / R / S / B タイプ',
    pth_spec2_label: '測温範囲', pth_spec2_val: '-200°C ～ +1820°C（タイプにより異なる）',
    pth_spec3_label: '適合規格', pth_spec3_val: 'IEC 584（国際規格）、JIS C 1602（日本）',
    pth_spec4_label: '保護管材質', pth_spec4_val: 'ステンレス / 炭化ケイ素（SiC）/ 高純度セラミック / 石英',
    pth_spec5_label: '配線方式', pth_spec5_val: '端子台タイプ / コネクタタイプ / リード線タイプ',
    pth_spec6_label: '精度クラス', pth_spec6_val: 'クラス1 / クラス2（IEC 584準拠）',
    pth_spec7_label: 'カスタム項目', pth_spec7_val: '長さ、外径、コネクタ、保護管はすべてカスタマイズ可能です。',
    pth_type1_name: 'Kタイプ（クロメル-アルメル）', pth_type1_desc: '最も汎用性が高く、-200°C～+1372°C、耐酸化性に優れ、工業標準の第一選択です。',
    pth_type2_name: 'Jタイプ（鉄-コンスタンタン）', pth_type2_desc: '-40°C～+750°C、還元性雰囲気に適し、低コストです。',
    pth_type3_name: 'Tタイプ（銅-コンスタンタン）', pth_type3_desc: '-270°C～+400°C、低温域での精度が高く、食品の冷蔵・冷凍に適しています。',
    pth_type4_name: 'Eタイプ（クロメル-コンスタンタン）', pth_type4_desc: '-270°C～+1000°C、最も高い感度を持ち、低温高精度用途に適しています。',
    pth_type5_name: 'R/Sタイプ（白金ロジウム-白金）', pth_type5_desc: '0°C～+1767°C、貴金属製で高精度、精密な高温プロセスに適しています。',
    pth_type6_name: 'Bタイプ（白金ロジウム30%-白金ロジウム6%）', pth_type6_desc: '0°C～+1820°C、最高温度に対応するタイプで、高温酸化雰囲気に適しています。',
    pth_ind1: '射出成形 — バレル温度のモニタリング、金型温度の測定',
    pth_ind2: 'アルミ合金鋳造 — 溶解炉温度・注湯温度のリアルタイム監視',
    pth_ind3: '半導体プロセス — 拡散炉の温度制御、CVDプロセスの温度監視',
    pth_ind4: '熱処理 — 焼なまし炉・焼入れ炉の温度記録',
    pth_ind5: '食品加工 — 低温殺菌、焙煎炉の温度制御（Tタイプ）',
    pth_ind6: 'EV電池製造 — 電池モジュールの温度監視',
    pth_faq1_q: 'K型とJ型の熱電対にはどのような違いがあり、どちらを選ぶべきですか？',
    pth_faq1_a: 'K型は一般的な工業環境（酸化雰囲気、最高1372°C）に適しており、市場で最も汎用的なタイプで、交換部品も入手しやすいです。J型は還元性または真空雰囲気に適し、最高750°C、コストも低めです。射出成形工場ではK型が多く使われ、鉄系金属の熱処理ではJ型が選ばれることもあります。',
    pth_faq2_q: '熱電対の保護管材質はどのように選べばよいですか？',
    pth_faq2_a: 'ステンレス（SUS304/316）：一般的な工業環境向けで耐腐食性があり、100～1100°Cに対応。炭化ケイ素（SiC）：アルミ溶解など腐食性の高い環境向けで耐衝撃性があり、最高1600°Cに対応。高純度セラミック（Al₂O₃）：高温・腐食性ガス環境向けで、最高1700°Cに対応。',
    pth_faq3_q: '欣晨工業の熱電対は、既存の温度コントローラーと組み合わせて使用できますか？',
    pth_faq3_a: '可能です。欣晨の熱電対はIEC 584国際規格に準拠しており、市販の各ブランドの温度コントローラー（Omron、横河電機、Shinkoなど）と互換性があります。ご注文時に温度コントローラーの型式をお知らせいただければ、配線方法の確認をサポートいたします。',
    pth_faq4_q: 'カスタム熱電対の納期はどのくらいですか？',
    pth_faq4_a: '標準タイプの在庫品は3～5営業日です。カスタムサイズは通常7～14営業日です。用途、温度範囲、取り付けスペースなどの情報をご提供いただければ、選定をサポートいたします。',
    pth_rel1_title: '工業用ヒーター', pth_rel1_desc: '熱電対と組み合わせて使用する加熱エレメント',
    pth_rel2_title: '炭化ケイ素保護管', pth_rel2_desc: '高温溶液環境向けの保護管',
    pth_cta_title: '熱電対の仕様やお見積りについてお気軽にお問い合わせください',
    pth_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    // ── product-heater.html ──
    phe_eyebrow: '産業用ヒーター', phe_title: '産業用ヒーター', phe_breadcrumb: '産業用ヒーター',
    phe_lead: '射出成形からアルミ鋳造まで対応する精密加熱エレメント。最高使用温度1200°C、フルカスタム仕様に対応します。',
    phe_spec1_label: '最高使用温度', phe_spec1_val: '1,200°C',
    phe_spec2_label: '出力範囲', phe_spec2_val: '50W ～ 10kW',
    phe_spec3_label: '電圧仕様', phe_spec3_val: '110V / 220V / 380V（カスタム可）',
    phe_spec4_label: 'ヒーター管材質', phe_spec4_val: 'ニクロム合金（Ni-Cr）/ FeCrAl / Kanthal A-1',
    phe_spec5_label: '絶縁材質', phe_spec5_val: '酸化マグネシウム（MgO）粉末充填',
    phe_spec6_label: '外装材質', phe_spec6_val: 'SUS304 / SUS316 ステンレス',
    phe_spec7_label: '取付方式', phe_spec7_val: 'フランジ式 / ネジ式 / 挿入式',
    phe_spec8_label: 'カスタム項目', phe_spec8_val: '外径、長さ、リード線位置、出力はすべてカスタマイズ可能です。',
    phe_type1_name: '射出成形機用バンドヒーター', phe_type1_desc: 'バレル外側に巻き付けて均一に加熱し、各種射出成形機に対応します。',
    phe_type2_name: '産業用ヒーターロッド', phe_type2_desc: '挿入式設計で精密なスポット加熱が可能。金型の予熱やホットランナーシステムに適しています。',
    phe_type3_name: 'セラミックヒーター', phe_type3_desc: '高温・耐衝撃性に優れ、工業炉、半導体装置、焼なまし炉などに適しています。',
    phe_type4_name: '赤外線ヒーター', phe_type4_desc: '非接触加熱方式で、プラスチックの予熱、食品加工、表面処理に適しています。',
    phe_type5_name: '工業炉用ヒーター管', phe_type5_desc: '高出力・高耐熱設計で、アルミ鋳造の注湯システムや熱処理炉に適しています。',
    phe_ind1: '射出成形（インジェクション成形）— バレル用バンドヒーター、金型用ヒーターロッド',
    phe_ind2: 'アルミ合金鋳造（ダイカスト）— 注湯システム用ヒーター管、保温炉用加熱エレメント',
    phe_ind3: '半導体プロセス — 拡散炉・酸化炉周辺の加熱システム',
    phe_ind4: '産業用熱処理 — 焼なまし炉、焼戻し炉、オーブン用加熱エレメント',
    phe_ind5: 'EV製造 — 電池電極の乾燥、モーターステーターの予熱',
    phe_faq1_q: '欣晨工業のヒーターは最高何度まで使用できますか？',
    phe_faq1_a: '産業用電熱管の最高使用温度は1200°C（ニクロム合金製）です。セラミックヒーターは型式により800～1200°Cまで対応可能です。赤外線ヒーターは通常400～700°Cです。実際の使用環境に応じて適切な型式をお選びください。',
    phe_faq2_q: 'カスタムヒーターはどのように注文すればよいですか？',
    phe_faq2_a: '電話（03-381-4497）またはオンライン問い合わせフォームより、外径仕様、長さ、電圧、出力、取付方式、材質要件をお知らせください。1～2営業日以内にお見積りをご回答いたします。',
    phe_faq3_q: 'バンドヒーターとヒーターロッドの違いは何ですか？',
    phe_faq3_a: 'バンドヒーターはバレル外側に巻き付けて均一な周方向加熱を行う、射出成形機の標準装備です。ヒーターロッドは挿入式設計で、金型内部の精密なスポット加熱に適しています。両者とも熱電対による温度制御システムと組み合わせて使用できます。',
    phe_faq4_q: '納期はどのくらいですか？',
    phe_faq4_a: '標準品の在庫サイズは通常3～5営業日で出荷します。カスタム仕様は複雑さに応じて7～14営業日です。お急ぎの場合は対応可能ですので、営業担当にご相談ください。',
    phe_rel1_title: '熱電対', phe_rel1_desc: 'ヒーターと組み合わせて使用する温度センサー',
    phe_rel2_title: '一体型バレル', phe_rel2_desc: 'ヒーターバンドを一体化した射出成形機用バレル',
    phe_cta_title: '産業用ヒーターの仕様やお見積りについてお気軽にお問い合わせください',
    phe_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    // ── product-sic-tube.html ──
    psic_eyebrow: 'SiC保護管', psic_title: '炭化ケイ素保護管', psic_breadcrumb: '炭化ケイ素保護管',
    psic_lead: '高純度炭化ケイ素（SiC）製で、耐熱温度1600°C以上、優れた耐熱衝撃性・耐酸化性・耐腐食性を備え、半導体プロセスやアルミ鋳造の高温環境に適しています。',
    psic_spec1_label: '材質', psic_spec1_val: '高純度炭化ケイ素（SiC）',
    psic_spec2_label: '純度', psic_spec2_val: '> 99%',
    psic_spec3_label: '最高使用温度', psic_spec3_val: '> 1,600°C（連続使用）',
    psic_spec4_label: '耐熱衝撃性', psic_spec4_val: '優れた耐熱衝撃性（急冷急熱に対応）',
    psic_spec5_label: '耐酸化性', psic_spec5_val: '優（高温酸化雰囲気中）',
    psic_spec6_label: '耐腐食性', psic_spec6_val: '優（強酸・強アルカリを除く）',
    psic_spec7_label: '硬度', psic_spec7_val: 'HV 2,500（モース硬度9以上）',
    psic_spec8_label: 'カスタム項目', psic_spec8_val: '外径、内径、長さ、端部形状はすべてカスタマイズ可能です。',
    psic_type1_name: '反応焼結SiC（RBSiC）', psic_type1_desc: 'コストを抑えられ、アルミ溶湯保護など一般的な高温用途に適しています。',
    psic_type2_name: '再結晶SiC（ReSiC）', psic_type2_desc: '高純度・高強度で、半導体拡散炉などの超高温プロセスに適しています。',
    psic_type3_name: '窒化ケイ素結合SiC（NSiC）', psic_type3_desc: '優れた耐熱衝撃性を持ち、急冷急熱が頻繁な環境に適しています。',
    psic_ind1: '半導体プロセス — 拡散炉（Diffusion Furnace）の炉管保護、LPCVDプロセス',
    psic_ind2: 'アルミ合金鋳造 — 溶融アルミ中の熱電対保護管、注湯ガイド管',
    psic_ind3: '結晶成長炉 — シリコンインゴット成長装置部材',
    psic_ind4: 'セラミック焼結炉 — 高温焼結用保護部材',
    psic_ind5: '化学工業設備 — 耐腐食性が必要な高温配管の保護',
    psic_faq1_q: '炭化ケイ素保護管とステンレス保護管の違いは何ですか？',
    psic_faq1_a: 'ステンレス保護管の使用上限は約1100～1200°Cで、高温下では強度が低下し、アルミ溶湯と接触すると腐食しやすくなります。SiC保護管は1600°C以上の耐熱性を持ち、アルミ溶湯環境でも化学的に安定しているため、寿命はステンレスの3～10倍に達し、アルミ鋳造工場で第一に選ばれています。',
    psic_faq2_q: '炭化ケイ素保護管は半導体プロセスの水素雰囲気でも使用できますか？',
    psic_faq2_a: '酸化雰囲気下ではSiCは優れた性能を発揮します。還元性雰囲気や水素雰囲気では、高純度の再結晶SiC（ReSiC）の方が適しています。具体的なプロセス条件をお知らせいただければ、最適な選定をサポートいたします。',
    psic_faq3_q: 'カスタム炭化ケイ素保護管はどのように注文すればよいですか？',
    psic_faq3_a: '外径（mm）、内径（mm）、長さ（mm）、使用温度、使用環境（雰囲気・接触媒体）、数量をお知らせください。電話（03-381-4497）またはオンライン問い合わせフォームより、1～2営業日以内にお見積りをご回答いたします。',
    psic_rel1_title: '熱電対', psic_rel1_desc: 'SiC保護管と組み合わせて使用する温度センサー',
    psic_rel2_title: '耐火材料', psic_rel2_desc: '高温炉の構築に使用する材料',
    psic_cta_title: '炭化ケイ素保護管の仕様やお見積りについてお気軽にお問い合わせください',
    psic_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    // ── product-refractory.html ──
    pref_eyebrow: '耐火材料', pref_title: '耐火材料', pref_breadcrumb: '耐火材料',
    pref_lead: '耐火レンガ、耐火キャスタブル、定形耐火製品。耐熱温度1800°Cに対応し、各種冶金炉、工業窯炉、高温プロセス設備に適しています。',
    pref_spec1_label: '最高使用温度', pref_spec1_val: '最高1,800°C（材質により異なる）',
    pref_spec2_label: '耐火レンガの種類', pref_spec2_val: '高アルミナ煉瓦 / シリカ煉瓦 / マグネシア煉瓦 / 炭化ケイ素煉瓦',
    pref_spec3_label: '不定形耐火材', pref_spec3_val: 'キャスタブル / プラスチック耐火材 / 吹付け材 / 塗布材',
    pref_spec4_label: '圧縮強度', pref_spec4_val: '高い（材質仕様により異なる）',
    pref_spec5_label: '熱伝導率', pref_spec5_val: '低い（優れた断熱性）',
    pref_spec6_label: '熱安定性', pref_spec6_val: '優（急熱急冷に強い耐性）',
    pref_spec7_label: 'カスタムサービス', pref_spec7_val: '炉の形状に合わせた施工プランをご提案します。',
    pref_type1_name: '高アルミナ煉瓦', pref_type1_desc: 'Al₂O₃含有率45%以上、耐熱温度1400～1800°C、高強度で、アーク炉や誘導炉の内壁に適しています。',
    pref_type2_name: 'シリカ煉瓦', pref_type2_desc: 'SiO₂含有率93%以上、耐熱温度1600～1700°C、コークス炉やガラス窯に適しています。',
    pref_type3_name: 'マグネシア煉瓦', pref_type3_desc: 'MgO含有率85%以上、塩基性スラグに強く、製鋼転炉やアーク炉の炉底に適しています。',
    pref_type4_name: '炭化ケイ素耐火煉瓦', pref_type4_desc: '高強度・高熱伝導率で、バーナースリーブやキルンカーの天板に適しています。',
    pref_type5_name: '不定形耐火材（キャスタブル）', pref_type5_desc: '任意の形状に流し込み成形でき、異形炉の補修や一体施工に適しています。',
    pref_ind1: '製鋼業 — アーク炉、転炉、レードルの内張り',
    pref_ind2: '非鉄金属精錬 — アルミ、銅、亜鉛溶解炉の内張り',
    pref_ind3: '工業用窯炉 — セラミック窯、ガラス窯、セメント窯',
    pref_ind4: '化学工業設備 — 高温反応炉、燃焼炉',
    pref_ind5: '鋳造業 — キューポラ、誘導炉、注湯ガター',
    pref_faq1_q: '耐火レンガの材質はどのように選べばよいですか？',
    pref_faq1_a: '主に以下の点をご検討ください：①使用温度（必要な耐火度を確認）；②スラグの性質（酸性スラグにはシリカ煉瓦、塩基性スラグにはマグネシア煉瓦）；③機械的負荷（高負荷には高アルミナ煉瓦）；④施工方法（一体施工には定形煉瓦、異形部位にはキャスタブル）。無料相談で材質選定をサポートいたします。',
    pref_faq2_q: '耐火材料のメンテナンス方法を教えてください。',
    pref_faq2_a: '急激な昇温・降温を避け（炉のベーキング曲線を遵守）、目地の漏れを定期的に確認し、損傷箇所は早期に補修してください。欣晨工業では炉のアフターメンテナンス相談も承っております。',
    pref_faq3_q: '最小注文数量はどのくらいですか？',
    pref_faq3_a: '製品型式や仕様によって異なりますので、お電話（03-381-4497）でお問い合わせください。標準仕様品は少量注文も可能で、大口購入には割引もございます。',
    pref_rel1_title: '炭化ケイ素保護管', pref_rel1_desc: '炉内用高温保護管',
    pref_rel2_title: '産業用ヒーター', pref_rel2_desc: '窯炉用加熱エレメント',
    pref_cta_title: '耐火材料の仕様やお見積りについてお気軽にお問い合わせください',
    pref_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    // ── product-integrated-barrel.html ──
    pib_eyebrow: '一体型バレル', pib_title: '一体型バレル', pib_breadcrumb: '一体型バレル',
    pib_lead: '一体成形によるシームレス設計で、従来のバレルにあった漏れのリスクを解消。バイメタル合金や窒化合金材質により、優れた耐摩耗性と耐腐食性を実現します。',
    pib_spec1_label: '設計特長', pib_spec1_val: '一体成形・シームレスで、漏れのリスクを解消',
    pib_spec2_label: '材質オプション', pib_spec2_val: '窒化スチール / バイメタル合金 / ハイスコーティング',
    pib_spec3_label: '窒化スチールの硬度', pib_spec3_val: 'HRC 60–65',
    pib_spec4_label: 'バイメタル合金の硬度', pib_spec4_val: 'HRC 60–68',
    pib_spec5_label: 'ハイスコーティングの硬度', pib_spec5_val: 'HRC 62–66',
    pib_spec6_label: '対応材料', pib_spec6_val: '一般プラスチック / ガラス繊維充填材 / エンジニアリングプラスチック / 腐食性材料（PVC）',
    pib_spec7_label: 'カスタム項目', pib_spec7_val: '内径、外径、長さ、バンドヒーター一体化はすべてカスタマイズ可能です。',
    pib_type1_name: '窒化スチールバレル', pib_type1_desc: '一般プラスチックに適し、高耐摩耗性、表面硬度HRC 60-65、コストパフォーマンスに優れています。',
    pib_type2_name: 'バイメタル合金バレル', pib_type2_desc: '内壁に高合金耐摩耗層を鋳込み、ガラス繊維や鉱物充填材など摩耗性の高いエンジニアリングプラスチックに適しています。',
    pib_type3_name: 'ハイスコーティングバレル', pib_type3_desc: 'PVCや難燃材などの腐食性材料に適し、耐摩耗性と耐腐食性を両立しています。',
    pib_ind1: '射出成形工場 — 各種プラスチック製品の生産',
    pib_ind2: '自動車部品製造 — 高強度エンジニアリングプラスチックの射出',
    pib_ind3: '電子部品 — 精密小型射出成形',
    pib_ind4: '包装材料 — 高速射出・高生産性が求められる用途',
    pib_ind5: '医療機器 — 高い清浄度が求められるバレル',
    pib_faq1_q: '一体型バレルと通常のバレルの違いは何ですか？',
    pib_faq1_a: '一体型バレルは一体鋳造または鍛造で製造され、接合部がありません。従来の分割式バレルには複数の接合部があり、長期間使用すると熱膨張・収縮により材料の漏れが発生しやすくなります。一体型設計は密閉性を大幅に向上させ、金型交換の停止回数を減らし、寿命を延ばします。',
    pib_faq2_q: '射出成形機のバレル交換が必要かどうかはどのように判断しますか？',
    pib_faq2_a: '以下のような場合は交換をご検討ください：①スクリューとバレルの隙間が大きくなり射出圧力が低下する；②製品に焦げや色のばらつきが発生する；③バレル外壁に亀裂や凹みが見られる。欣晨工業のエンジニアが現場診断をサポートいたします。',
    pib_faq3_q: 'バイメタルバレルは窒化バレルよりどのくらい高く、その価値はありますか？',
    pib_faq3_a: 'バイメタルバレルのコストは窒化バレルの約1.5～2.5倍です。ただし、加工材料にガラス繊維や鉱物充填材が含まれる場合、窒化バレルの寿命はバイメタルの1/3～1/5程度になることがあります。長期的に見ると、バイメタルバレルは交換回数が少なく、停止コストも低いため、多くの場合より経済的な選択となります。',
    pib_rel1_title: '産業用ヒーター', pib_rel1_desc: 'バレル用バンドヒーター',
    pib_rel2_title: '熱電対', pib_rel2_desc: 'バレル温度モニタリング用',
    pib_cta_title: '一体型バレルの仕様やお見積りについてお気軽にお問い合わせください',
    pib_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    // ── product-graphite-tube.html ──
    pgt_eyebrow: '高濃度ナノバブル流体モジュール', pgt_title: '高濃度ナノバブル流体モジュール', pgt_breadcrumb: '高濃度ナノバブル流体モジュール',
    pgt_lead: '気泡サイズ100nm未満の高濃度ナノバブル流体を生成し、半導体プロセス、医療機器、液冷システムに応用。省エネ・高密度・薬剤不使用のクリーンな効果を実現します。',
    pgt_spec1_label: '気泡サイズ', pgt_spec1_val: '< 100 nm',
    pgt_spec2_label: '気泡濃度', pgt_spec2_val: '> 10⁸ 個/mL（高密度）',
    pgt_spec3_label: '対応媒体', pgt_spec3_val: '純水、半導体プロセス用水、冷却液、医療用水',
    pgt_spec4_label: 'ガス源', pgt_spec4_val: 'N₂ / O₂ / CO₂ / 空気（用途に応じて選択可能）',
    pgt_spec5_label: '設置方式', pgt_spec5_val: '配管インライン設置、既存の水路・液冷回路に対応',
    pgt_spec6_label: '機能', pgt_spec6_val: '物理的な気泡崩壊による微小衝撃力で汚染物質やバイオフィルムを分解、薬剤不使用',
    pgt_spec7_label: 'カスタム項目', pgt_spec7_val: '流量、濃度、ガス種類は生産ラインの要件に応じてカスタマイズ可能',
    pgt_type1_name: '半導体プロセス向け', pgt_type1_desc: 'ウェーハ洗浄やプロセス用水システムに適用し、洗浄効率を高め薬剤使用量を削減します。',
    pgt_type2_name: '液冷システム向け', pgt_type2_desc: 'データセンターや設備の液冷回路に設置し、放熱効率を強化し配管のスケールやバイオフィルムの発生を抑制します。',
    pgt_type3_name: '医療機器向け', pgt_type3_desc: '医療機器の洗浄や滅菌補助プロセスに応用し、薬剤残留のないマイルドな洗浄ソリューションを提供します。',
    pgt_ind1: '半導体製造 — ウェーハ洗浄、プロセス用水の水質向上、後工程洗浄',
    pgt_ind2: '医療産業 — 医療機器洗浄、実験用水の純化補助',
    pgt_ind3: 'データセンター液冷 — サーバー液冷回路の放熱効率向上、スケール・バイオフィルム抑制',
    pgt_ind4: '精密電子製造 — 高度な電子部品の洗浄、薬剤残留不可のプロセス',
    pgt_faq1_q: 'ナノバブルとは何ですか？通常のマイクロバブルとの違いは？',
    pgt_faq1_a: 'ナノバブルは直径100nm未満の微小な気泡で、液体中で負のゼータ電位を帯びるため浮上・合体しにくく、長時間流体中に懸浮します。従来のマイクロバブルと比較して比表面積が非常に大きく、液体や粒子との接触効率が大幅に向上するため、洗浄・物質移動・放熱などの用途で顕著な効果を発揮します。',
    pgt_faq2_q: '高濃度ナノバブル流体モジュールはどのような分野に応用できますか？',
    pgt_faq2_a: '主に3つの分野に応用されます：①半導体プロセス — ウェーハ洗浄やプロセス用水の水質向上；②医療産業 — 医療機器の洗浄や滅菌補助；③液冷システム — データセンターや設備の液冷回路の放熱効率向上、配管のスケールやバイオフィルムの増殖を抑制。',
    pgt_faq3_q: 'ナノバブルはどのように薬剤不使用の洗浄効果を実現しますか？',
    pgt_faq3_a: 'ナノバブルが液体中で崩壊する際に局所的なエネルギーを放出し、微小な衝撃力を発生させることで、表面に付着した微粒子汚染物やバイオフィルムを物理的に緩めて剥離させます。化学薬剤に依存せず洗浄効果を実現でき、薬剤の購入や廃液処理コストを大幅に削減し、環境にもより優しくなります。',
    pgt_faq4_q: '高濃度ナノバブル流体モジュールの導入にはどのような条件が必要ですか？メンテナンスは？',
    pgt_faq4_a: 'モジュールは配管のインライン設置方式を採用しており、既存のプロセス用水や液冷配管の多くに対応可能で、給水と電源を接続するだけで稼働します。日常メンテナンスはフィルターの定期交換のみで、薬剤補充は不要なため、メンテナンス手順を大幅に簡素化し運用コストを削減します。流量や設置環境のご要望をお知らせいただければ、欣晨のエンジニアが選定をサポートいたします。',
    pgt_rel1_title: '炭化ケイ素保護管', pgt_rel1_desc: '半導体・高温プロセス用の主要消耗部品',
    pgt_rel2_title: '熱電対', pgt_rel2_desc: '精密温度モニタリング用途',
    pgt_cta_title: '高濃度ナノバブル流体モジュールの仕様やお見積りについてお気軽にお問い合わせください',
    pgt_cta_desc: '使用環境、仕様要件、数量をお知らせいただければ、欣晨工業のエンジニアが1～2営業日以内に最適なプランをご提案します。',

    pp_qa_title: '品質保証', pp_qa_lead: 'すべての製品は厳格な品質管理プロセスを経ています。原材料の選定から完成品の検査まで、全工程で品質を追跡しています。',
    pp_qa_1_title: '原材料の厳選', pp_qa_1_desc: 'すべての製品には業界認証済みの高純度原材料を採用し、化学成分・物理特性が厳格な工業用途基準に適合することを保証します。',
    pp_qa_2_title: '出荷前検査', pp_qa_2_desc: '出荷前には各バッチごとに寸法・耐熱性・強度など複数の性能検査を実施し、完全な検査報告書を提供することで品質の一貫性を確保します。',
    pp_qa_3_title: 'カスタム仕様', pp_qa_3_desc: '非標準サイズのカスタマイズサービスを提供し、お客様の設備仕様に合わせて特別生産。柔軟な納期対応で多様な用途のニーズにお応えします。',
    pp_cta_title: 'カスタム仕様やお見積りについて、お気軽にご相談ください',
    pp_cta_desc: 'ご利用環境や仕様のご要望をお知らせください。欣晨工業の製品エンジニアが最適な素材のご提案とお見積りをいたします。',
    pp_cta_btn: '今すぐ見積依頼',

    srv_eyebrow_top: 'サービス', srv_eyebrow_cta: 'プロジェクト開始',
    srv_page_title: '欣晨工業 サービス項目',
    srv_page_lead: '欣晨工業有限公司の7つの自動化サービス。デジタル計画からロボットアーム統合・画像検査・設備インテリジェント化・ナノバブル流体応用まで、製造ニーズをワンストップで満たします。',
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
    srv_d7_num: 'SERVICE 07', srv_d7_tag: 'ナノバブル応用', srv_d7_title: '高濃度ナノバブル流体産業応用',
    srv_d7_desc: '半導体プロセス用水、生医療機器洗浄、データセンター液冷などの分野に高濃度ナノバブル流体モジュールを導入。選定評価、配管統合設置、性能検証を提供し、物理的なナノバブルで化学薬品を代替し、省エネかつ薬品不使用のプロセスアップグレードを実現します。',
    srv_d7_p1: '半導体プロセス用水の水質向上とウェハー洗浄補助', srv_d7_p2: '生医療機器の洗浄・滅菌補助、化学薬品依存の低減',
    srv_d7_p3: 'データセンター液冷システムの放熱効率向上、配管スケール抑制', srv_d7_p4: '化学薬品不使用で廃液処理コストと環境負荷を低減', srv_d7_btn: 'このサービスについて相談',
    srv_cta_title: '自動化プロジェクトを始めませんか？',
    srv_cta_desc: '新規ライン計画から既存設備アップグレードまで、欣晨工業のエンジニアチームが最適なソリューションを提供します。',
    srv_cta_btn: '今すぐ相談する',

    tech_eyebrow_top: 'テクノロジーインサイト',
    tech_eyebrow_cta: '共同開発のご相談',
    tech_page_title: '欣晨工業 新技術の展望',
    tech_page_lead: '半導体プロセスからヒューマノイドロボットまで、欣晨工業の精密部品・耐高温材料の6大先端分野における重要な応用と技術貢献を探ります。',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: '半導体', tech_d1_title: '半導体製造プロセス',
    tech_d1_desc: '半導体ウェーハ製造は超高温・強腐食環境での精密な制御が必要であり、プロセス用水と洗浄品質にも高い要求があります。欣晨のSiC保護管は、優れた耐熱衝撃性と化学的不活性により、拡散炉管・結晶成長装置などの核心製造設備の重要消耗品となっています。高濃度ナノバブル流体モジュールは、ウェーハ洗浄とプロセス用水の水質向上に用いられ、省エネかつ化学薬品不使用の洗浄効果を実現します。',
    tech_d1_p1: 'SiC保護管：耐熱1600°C、耐酸化・耐食性', tech_d1_p2: '高濃度ナノバブル流体モジュール：気泡サイズ100nm未満、ウェーハ洗浄とプロセス用水の水質向上に使用',
    tech_d1_p3: '一体型バレル：溶融シリコン搬送時の純度・無汚染を確保', tech_d1_p4: 'カスタム寸法、各種結晶成長炉とPECVD設備に適合', tech_d1_btn: '応用ソリューションについて相談',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: '電気自動車', tech_d2_title: '電気自動車（EV）',
    tech_d2_desc: 'EV電池モジュール・モーター・パワーエレクトロニクス部品は熱管理に厳しい要件があります。欣晨の耐火材料・高精度セラミック部品は、電池パック構造保護・モーターステーター絶縁・鋳造工場でのアルミ合金モーターシェル製造に広く使用されており、高温・高圧環境下での材料の長期安定性を確保します。',
    tech_d2_p1: '電池モジュール防火断熱板：難燃・耐高温構造保護', tech_d2_p2: 'アルミ鋳造プロセス保護管：モーターシェル製造に必須',
    tech_d2_p3: 'セラミック熱電対：モーター動作温度の精確な監視', tech_d2_p4: '耐高温絶縁材料：パワーモジュール（IGBT/SiC MOSFET）対応', tech_d2_btn: '応用ソリューションについて相談',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'シリコンフォトニクス', tech_d3_title: 'シリコンフォトニクス',
    tech_d3_desc: 'シリコンフォトニクス技術は光学部品をシリコン基板上に統合し、高速光通信とAI加速演算を実現します。欣晨は光子チップ封止プロセス向けの高精度セラミック治具・耐高温治具・プロセス保護部品を提供し、ボンディングやアニーリングなどの精密工程におけるチップの構造的完全性を確保します。',
    tech_d3_p1: '高精度セラミック位置決め治具：光ファイバーアレイ位置合わせ', tech_d3_p2: '耐高温プロセスキャリア：ボンディングプロセスの安定した搭載',
    tech_d3_p3: 'アルミナセラミック断熱板：アニール炉の均一熱分布', tech_d3_p4: 'カスタム仕様、ファウンドリのプロセスノード要件に対応', tech_d3_btn: '応用ソリューションについて相談',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'ヒューマノイドロボット', tech_d4_title: 'ヒューマノイドロボット',
    tech_d4_desc: 'ヒューマノイドロボットの関節駆動・エンドエフェクター・センシングシステムは軽量化と高精度を兼ね備えた部品製造を必要とします。欣晨は30年の精密加工経験を活かし、ヒューマノイドロボットメーカー向けにアルミ合金構造部品・精密駆動スリーブ・耐摩耗セラミック部品を提供し、厳格な寸法管理によりロボットの動作精度と長寿命を確保します。',
    tech_d4_p1: '関節駆動精密スリーブ：動作繰り返し位置決め精度を維持', tech_d4_p2: '軽量アルミ合金構造部品：本体重量を削減し機敏性を向上',
    tech_d4_p3: '耐摩耗セラミックガイド部品：関節寿命を延長', tech_d4_p4: '高精度公差管理：±0.01mm 級加工能力', tech_d4_btn: '応用ソリューションについて相談',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: '量子コンピューター', tech_d5_title: '量子コンピューター',
    tech_d5_desc: '量子コンピューターの希釈冷凍機は量子ビットを絶対零度近く（15 mK）に保つ必要があり、部品の熱伝導性・電磁障害防護・超精密加工に極限の要求があります。欣晨は低温環境に適した高純度無酸素銅部品と精密セラミック断熱部品を提供し、量子コンピューティング機器メーカーの製造プロセスのボトルネック解消を支援します。',
    tech_d5_p1: '高純度無酸素銅（OFC）精密部品：優れた熱伝導・電気伝導性', tech_d5_p2: 'セラミック断熱構造部品：低温環境での熱絶縁設計',
    tech_d5_p3: '超精密加工：表面粗さ Ra ≤ 0.4μm', tech_d5_p4: '厳格な清潔度管理：量子状態への干渉汚染を回避', tech_d5_btn: '応用ソリューションについて相談',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / ドローン', tech_d6_title: '無人機（UAV/ドローン）',
    tech_d6_desc: 'ドローンは極限の軽量化と構造強度のバランスを追求し、モーターマウント・駆動軸・ジンバルフレームなどの重要部品は精密加工と厳格な品質管理が必要です。欣晨はドローンメーカー向けに高強度アルミ合金機構部品・炭素繊維複合材インサート・カスタム工作治具を提供し、プロトタイプ開発から量産まで、ライフサイクル全体にわたる製造ニーズに対応します。',
    tech_d6_p1: '航空アルミ合金（7075-T6）軽量化構造部品', tech_d6_p2: 'モーターマウント：精密孔位でモーター同心度を確保',
    tech_d6_p3: '炭素繊維複合材料埋込み式金属インサート', tech_d6_p4: '迅速試作と小ロット量産の柔軟なサービス', tech_d6_btn: '応用ソリューションについて相談',
    tech_cta_title: 'あなたの分野での精密材料応用を探りませんか？',
    tech_cta_desc: '欣晨工業の技術チームは、各先端技術分野のメーカーと材料ソリューションを共に探求し、技術の限界を共に押し広げることを歓迎します。',
    tech_cta_btn: '技術チームに今すぐ連絡',

    career_page_title: '欣晨工業 採用情報',
    career_page_lead: '欣晨工業有限公司に加わり、30年の精密製造技術を受け継ぎ、自動化と新材料時代の機会と挑戦を共に迎えましょう。',
    career_eyebrow_top: '採用情報',
    career_apply_label: 'メール応募',
    career_apply_note: '件名に「応募職位名＋氏名」を記載し、完全な履歴書と自己紹介文を添付してください',
    career_apply_btn: '今すぐ応募',
    career_eyebrow_jobs: '募集中の職種',
    career_jobs_title: '現在の求人',
    career_job1_tag: '機械設計', career_job1_title: '機械設計シニアエンジニア',
    career_job1_req1: 'Solid Edge / SolidWorksを用いた精密部品、モジュール、治具の設計',
    career_job1_req2: '製造部門と連携した設計検証、図面管理、加工工程の改善',
    career_job1_req3: '学歴：専門学校卒以上、機械工学関連学科、5年以上の設計実務経験',
    career_job1_req4: 'GD&T許容差設計および精密加工工程に精通している方優遇',
    career_job2_tag: '営業・マーケティング', career_job2_title: '製品営業エンジニア',
    career_job2_req1: '国内外の顧客開拓・維持、精密部品と自動化ソリューションの提案',
    career_job2_req2: '顧客の技術仕様を理解し、見積り・技術サポート・アフターサービスを提供',
    career_job2_req3: '学歴：専門学校卒以上、機械または工業工学系優遇',
    career_job2_req4: '中国語・英語または日本語のコミュニケーション能力がある方優先',
    career_job3_tag: '自動化技術', career_job3_title: '自動化設備エンジニア',
    career_job3_req1: '自動化生産設備および生産ラインシステムの計画・設計・統合',
    career_job3_req2: 'PLCプログラミング（三菱 iQ-F / iQ-R）およびHMI統合開発',
    career_job3_req3: '学歴：専門学校卒以上、電気・電子・自動制御関連学科',
    career_job3_req4: 'ロボットアーム統合または視覚システム応用経験者優遇',
    career_job4_tag: '購買・サプライチェーン', career_job4_title: 'サプライチェーンマネージャー',
    career_job4_req1: 'サプライヤーの開拓・評価、価格交渉および納期管理',
    career_job4_req2: '原材料調達計画、在庫管理および物流調整',
    career_job4_req3: '学歴：専門学校卒以上、経営工学・サプライチェーンまたは工業工学関連学科',
    career_job4_req4: 'ERPシステム操作に精通し、製造業での調達経験がある方優先',
    career_job5_tag: '技術製造', career_job5_title: '組立技術員',
    career_job5_req1: '工程図面とSOPに基づく精密機械部品の組立作業',
    career_job5_req2: '組立後の機能テスト、精度測定および品質自主確認',
    career_job5_req3: '学歴：高校卒以上、機械系学科優遇',
    career_job5_req4: '精密組立または電気配線の経験者優先、未経験者の研修も歓迎',
    career_eyebrow_benefits: '福利厚生',
    career_ben_title: '従業員福利厚生',
    career_ben1_title: '皆勤手当', career_ben1_desc: '毎月皆勤の従業員には皆勤手当を追加支給し、真摯な勤務態度と安定した仕事への取り組みを表彰します。',
    career_ben2_title: '年末ボーナス', career_ben2_desc: '会社の業績と個人の貢献度に応じて年末ボーナスを支給し、企業成長の成果を従業員と分かち合います。',
    career_ben3_title: '保険', career_ben3_desc: '労働保険、国民健康保険および団体傷害保険に法令に基づき満額加入し、安心の保障を提供します。',
    career_ben4_title: '無料食事', career_ben4_desc: '会社が従業員に昼食を提供し、生活の負担を軽減することで、仕事に専念できる環境を整えます。',
    career_ben5_title: '国内旅行', career_ben5_desc: '定期的に国内社員旅行を開催し、従業員同士の親睦を深め、チームの結束力を高めます。',
    career_ben6_title: '誕生日祝い金', career_ben6_desc: '従業員の誕生月に誕生日祝い金を贈呈し、会社が各メンバーを大切に思う気持ちと心からの祝福を伝えます。',
    career_ben7_title: '節季手当', career_ben7_desc: '端午節・中秋節・旧正月の三大節句にそれぞれ手当を支給し、従業員の日々の努力に感謝します。',
    career_ben8_title: '忘年会', career_ben8_desc: '毎年忘年会を開催し、全従業員の一年間の労をねぎらい、共に豊作を祝い新年を迎えます。',
    career_eyebrow_join: '私たちのチームへ',
    career_cta_title: '欣晨に加わる準備はできましたか？',
    career_cta_desc: '履歴書を hc3814497@gmail.com へお送りください。欣晨の次の50年を共に創ることを楽しみにしています。',
    career_cta_btn: '今すぐ履歴書を送る',

    contact_eyebrow_top: 'お問い合わせ',
    contact_page_title: '欣晨工業へのお問い合わせ',
    contact_page_lead: '製品の見積もり、技術協力、サービス交渉など、以下の方法で欣晨工業有限公司へご連絡ください。1〜2営業日以内にご回答します。',
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

    faq_title: 'よくある質問', faq_lead: 'お探しの答えをすばやく見つけてください。その他のご質問は', faq_contact_link: 'お問い合わせ',

    idx_eyebrow_genchi: '現地現物',
    genchi_title: '現地現物',
    genchi_desc: 'トヨタのコア原則：二次情報を信じず、自ら現場へ赴き、目で確認し、手で計測する。欣晨工業では、すべてのプロジェクト開始前にエンジニアが必ずお客様の工場を直接訪問し、実際の生産環境・設備スペース・作業者の動きを深く理解します。現場を真に読み解いてこそ、真に使える自動化システムを設計できます。',
    genchi_spec1_label: '現場', genchi_spec1_val: '要件ヒアリングと動線観察',
    genchi_spec2_label: '計測', genchi_spec2_val: '設備スペースと干渉評価',
    genchi_spec3_label: '分析', genchi_spec3_val: 'タクトタイム（Takt Time）の実地計測',
    genchi_cta: '私たちのアプローチを見る', genchi_img_tag: '現地現物',

    idx_eyebrow_kaizen: '改善（カイゼン）',
    kaizen_title_1: '改善', kaizen_title_2: '終わりなき改良への道',
    kaizen_desc: 'カイゼンは一度きりの革命ではなく、毎日積み重ねる微進化です。欣晨工業はカイゼン精神をすべての設計工程に落とし込んでいます。段取り替え時間の短縮（SMED）、ポカヨケ装置の導入、標準作業手順（SOP）の確立など、「ここをもっと良くできないか？」と問い続けます。',
    kaizen_spec1_val: '段取り替え設計で停機時間を短縮',
    kaizen_spec2_label: 'ポカヨケ', kaizen_spec2_val: 'Poka-yoke機構で源流エラーを防止',
    kaizen_spec3_label: '標準化', kaizen_spec3_val: 'SOP策定で工程の一貫性を確保',
    kaizen_cta: '自動化サービスを見る', kaizen_img_tag: '改善',

    marquee_1: '半導体プロセスのお客様', marquee_2: 'アルミ鋳造メーカー', marquee_3: 'EV部品メーカー',
    marquee_4: '精密機械メーカー', marquee_5: '電子封止メーカー', marquee_6: '化学設備メーカー',

    tech_lead: 'カイゼン・ポカヨケ・標準化の思想で、製造効率の限界を継続的に突破します。',
    tps_tag_1: 'カイゼン × 半導体製造', tps_1_title: '精密製造におけるカイゼン文化の実践',
    tps_1_desc: '半導体製造のマイクロメートル単位の要求こそ、カイゼン精神が最も輝く舞台です。各工程のわずかな改善が積み重なり、歩留まりの継続的な向上につながります。',
    tps_tag_2: 'JIT × EV生産', tps_2_title: 'JIT生産方式のEV工場への応用',
    tps_2_desc: 'EV部品は種類が多岐にわたります。「必要なとき、必要な数量、必要な品目」というJITの原則は、電池組立ラインの在庫ロス削減に不可欠なツールです。',
    tps_tag_3: 'ポカヨケ × 産業用ロボット', tps_3_title: 'Poka-yoke設計で産業用ロボットのエラーをゼロに',
    tps_3_desc: 'ロボット統合にポカヨケ機構を組み込むことで、グリッパーエラーや位置ズレを発生前に防止します。これがゼロ不良生産を実現するコア設計ロジックです。',
  },

  en: {
    nav_home: 'Home', nav_about: 'About Us', nav_products: 'Products',
    nav_services: 'Services', nav_tech: 'Technology', nav_careers: 'Careers',
    nav_contact: 'Contact',

    hero_badge: 'Precision Automation Solutions · Since 1996',
    hero_h1_line1: 'Precision Drives,', hero_h1_line2: 'Future Forged',
    hero_h2: 'Hsin-Chan Industrial Co., Ltd. — Precision automation rooted in Kaizen, Just-In-Time, and Jidoka.',
    cta_products: 'View Products', cta_contact_ask: 'Contact Us',
    metric_years: 'Years Experience', metric_products: 'Product Lines',
    metric_services: 'Service Areas', scroll: 'SCROLL',

    idx_eyebrow_tps: 'TOYOTA PRODUCTION SYSTEM',
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
    prod_b_title: 'High-Concentration Nano-Bubble Fluid Module',
    prod_b_desc: 'Generates high-concentration nano-bubble fluid with bubble size below 100nm. Applied in semiconductor process water, biomedical equipment cleaning, and liquid cooling systems — energy-saving, high-density, and chemical-additive-free, significantly reducing chemical costs and environmental impact.',
    prod_b_use: 'Semiconductor / Biomedical / Liquid Cooling', prod_b_merit: 'Energy-Saving, High-Density, Chemical-Free',
    spec_temp: 'Max Temp', spec_mat: 'Material', spec_app: 'Application',
    spec_purity: 'Bubble Size', spec_use: 'Purpose', spec_merit: 'Advantage',
    spec_type: 'Type', spec_heat: 'Temperature', spec_spec: 'Spec', spec_model: 'Model', spec_measure: 'Measurement', spec_industry: 'Industry',
    cta_spec: 'View Specs',

    idx_eyebrow_services: 'FULL-SPECTRUM AUTOMATION',
    srv_title: 'Full-Spectrum Automation Services',
    srv_lead: 'Seven services from planning to handover — your one-stop automation partner',
    srv_1_title: 'Digital Twin Automation Planning', srv_1_desc: 'Virtual line validation to reduce construction risk',
    srv_2_title: 'Robotic Arm Applications',         srv_2_desc: 'Handling, welding, assembly integration with path planning',
    srv_3_title: 'Custom Machine Design & Build',    srv_3_desc: 'Requirements → Design → Build → Commission, end-to-end',
    srv_4_title: 'Machine Vision Inspection',        srv_4_desc: 'Industrial cameras + AI defect detection & measurement',
    srv_5_title: 'Fixture & Jig Design',             srv_5_desc: 'High-precision fixtures for consistent quality',
    srv_6_title: 'Equipment Intelligence Upgrade',   srv_6_desc: 'Retrofit existing equipment with PLC / HMI / IoT',
    srv_7_title: 'High-Concentration Nano-Bubble Fluid Applications', srv_7_desc: 'Chemical-free adoption for semiconductor, biomedical, liquid cooling',
    cta_learn: 'Learn More', cta_all_services: 'View All Services',

    partners_eyebrow: 'TRUSTED BY INDUSTRY LEADERS',

    idx_eyebrow_tps_insights: 'TPS INSIGHTS',
    tech_title: 'Toyota Philosophy × Precision Manufacturing',
    tech_tag_semi: 'Semiconductor', tech_tag_ev: 'Electric Vehicle', tech_tag_robot: 'Humanoid Robotics',
    tech_1_title: 'Material Science in Precision Processes',
    tech_1_desc: 'SiC protection tubes play a critical role in high-temperature semiconductor processes, providing stable thermal environments and corrosion protection.',
    tech_2_title: 'Thermal Management in EV Battery Production',
    tech_2_desc: 'EV cell manufacturing demands precise thermal management. Hsin-Chan Industrial Co., Ltd. heaters and sensing elements ensure production consistency.',
    tech_3_title: 'Precision Machining for Robot Joints',
    tech_3_desc: "Humanoid robot joints require ultra-high precision manufacturing. Hsin-Chan Industrial Co., Ltd.'s fixture design provides accurate solutions for this challenge.",
    cta_read_more: 'Read More', cta_view_all_tech: 'View All Topics',

    idx_eyebrow_cta: 'START TODAY',
    cta_banner_title: 'Ready to Optimize Your Production Line with Toyota Philosophy?',
    cta_banner_desc: 'Tell us your on-site challenges. Our engineers will visit your facility and design the optimal solution with the spirit of Kaizen.',
    cta_contact_now: 'Contact Us Now',

    footer_nav_title: 'Quick Navigation', footer_contact_title: 'Contact Info',
    footer_years: '30 Years of Manufacturing',
    footer_addr: '490, Sec. 3, Zhongzheng E. Rd., Dayuan Dist., Taoyuan City, Taiwan',
    footer_tel: 'Tel: 03-381-4497', footer_fax: 'Fax: 03-381-4536',
    footer_tagline_1: 'Precision Drives', footer_tagline_2: 'Future Forged',
    footer_est: 'Est. 1996 · 30 Years of Manufacturing',

    about_banner_title: 'About Hsin-Chan Industrial',
    about_banner_lead: 'Hsin-Chan Industrial Co., Ltd. — 30 years of precision manufacturing expertise, rooted in Dayuan, Taoyuan, serving industrial clients across Taiwan. Built on technology, quality, and service.',
    about_eyebrow_top: 'ABOUT US',
    about_eyebrow_story: 'OUR STORY',
    about_our_title: 'About Hsin-Chan Industrial',
    about_desc_1: 'Hsin-Chan Industrial Co., Ltd. was founded in 1996 and is located at No. 490, Section 3, Zhongzheng East Road, Dayuan District, Taoyuan City, Taiwan. Over more than 30 years, Hsin-Chan Industrial has evolved from an industrial consumables supplier into a full-service manufacturing partner encompassing automation equipment design, manufacturing, integration, and after-sales support.',
    about_desc_2: 'Hsin-Chan Industrial\'s core products include silicon carbide protection tubes, high-concentration nano-bubble fluid modules, heaters, and thermocouples — high-temperature industrial consumables. We continue expanding into intelligent automation services including digital twin planning, robotic arm applications, and machine vision inspection. Our heaters operate at temperatures up to 1200°C and are widely used in injection molding, aluminum casting, and industrial furnace processes.',
    about_desc_3: 'To this day, Hsin-Chan Industrial upholds its three core principles — Precision, Customization, and Support — delivering reliable manufacturing solutions to the semiconductor, foundry, EV, and precision machinery industries. Our service spans all of Taiwan as well as Japan and Southeast Asia, with full Chinese, Japanese, and English language support.',
    about_desc_4: 'Hsin-Chan Industrial is built on the Toyota Production System (TPS) as its core philosophy, embedding Kaizen (continuous improvement), JIT (Just-In-Time), and Jidoka (autonomation) into every stage of manufacturing. We believe that through continuous improvement and precision manufacturing, we can create the greatest production value for our customers — together embracing the era of Industry 4.0 smart manufacturing.',
    about_history_eyebrow: 'Our History',
    about_tl_1_title: 'Founded', about_tl_1_desc: 'Established in Dayuan, Taoyuan. Focused on high-temperature industrial consumables manufacturing and supply for local manufacturers.',
    about_tl_2_title: 'Product Expansion', about_tl_2_desc: 'Introduced SiC protection tube production. Extended service scope to semiconductor and foundry industries.',
    about_tl_3_title: 'Factory Expansion', about_tl_3_desc: 'Added heater and thermocouple production lines, expanded factory floor space, increasing annual capacity and quality control capabilities.',
    about_tl_4_title: 'Automation Transition', about_tl_4_desc: 'Entered automation equipment design and manufacturing. Offering robotic arm integration, standalone automation, and machine vision inspection.',
    about_tl_5_title: 'Smart Upgrade', about_tl_5_desc: 'Introduced digital twin technology, driving existing equipment intelligence. Moving toward Industry 4.0 integrated service provider.',
    about_eyebrow_philosophy: 'PHILOSOPHY',
    about_mgmt_title: 'Management Philosophy',
    about_mgmt_lead_1: 'Hsin-Chan Industrial’s management philosophy is deeply inspired by ', about_mgmt_name: 'Kazuo Inamori', about_mgmt_lead_2: ', founder of Kyocera Corporation. He believed throughout his life that the purpose of a business is to pursue the material and spiritual well-being of all its members, and on that foundation, to contribute to the progress of humanity and society. This belief remains the guiding principle of Hsin-Chan Industrial.',
    about_mgmt_quote_main: 'Respect Heaven, Love People',
    about_mgmt_quote_sub: 'Keiten Aijin',
    about_mgmt_quote_cite: 'Kazuo Inamori — Founder of Kyocera Corporation and KDDI',
    about_mgmt_c1_title: 'A Heart for Others', about_mgmt_c1_concept: 'Benefiting others is benefiting yourself',
    about_mgmt_c1_desc: 'Inamori believed that true success comes from a heart that thinks of others first. In every customer interaction, Hsin-Chan Industrial’s first question is: what solution will benefit the customer’s production most — not simply how to sell a product. Creating real value for customers is the foundation of every lasting partnership.',
    about_mgmt_c2_title: 'Respect Heaven, Love People', about_mgmt_c2_concept: 'Follow the right path, treat others with sincerity',
    about_mgmt_c2_desc: '“Respect Heaven” means following the fundamental laws of nature and things — never taking shortcuts or deceiving others. “Love People” means treating every partner, customer, and employee with genuine care. Hsin-Chan Industrial upholds integrity and transparency: every quote, lead time, and quality commitment is honored in full, so no customer ever leaves with doubts.',
    about_mgmt_c3_title: 'Continuous Improvement', about_mgmt_c3_concept: 'Make an effort greater than anyone else’s',
    about_mgmt_c3_desc: 'The first of Inamori’s Six Practices is to “make an effort greater than anyone else’s.” Hsin-Chan’s engineers hone their craft on the shop floor every day, never settling for “good enough” — always pursuing “the best.” From drawing design and parts machining to final commissioning, every step is made a little more precise than the day before.',
    about_mgmt_c4_title: 'Work as Spiritual Practice', about_mgmt_c4_concept: 'Forging the soul through labor',
    about_mgmt_c4_desc: 'Inamori said, “Work is the best way to forge the soul.” In manufacturing, every component and every piece of equipment embodies human dedication and will. Hsin-Chan Industrial believes that giving one’s full effort to work is not only a responsibility to customers, but also the path by which every employee grows and builds character.',
    about_phil_title: 'Our Philosophy',
    about_phil_lead: 'Three core principles have driven Hsin-Chan Industrial Co., Ltd.\'s steady 30-year growth, and represent our commitment to every client we serve.',
    about_phil_1_title: 'Precision Manufacturing', about_phil_1_desc: '30 years of accumulated manufacturing expertise and rigorous quality management ensure every component meets exact specifications. Full traceability from raw materials to finished products guarantees reliable equipment performance.',
    about_phil_2_title: 'Custom Solutions', about_phil_2_desc: 'From requirements analysis and mechanism design to production and delivery, we provide one-on-one custom service. We deeply understand each client\'s production environment to deliver the most suitable automation solution.',
    about_phil_3_title: 'Technical Support', about_phil_3_desc: 'Expert engineering teams provide on-site commissioning and technical training, backed by comprehensive after-sales maintenance. Ongoing technical consultation after delivery ensures long-term, stable, high-efficiency equipment operation.',
    about_team_title: 'Leadership Team',
    about_team_lead: 'A professional team with extensive industry experience, continuously driving technological innovation and service advancement.',
    about_team_1_role: 'General Manager', about_team_1_desc: 'Responsible for overall corporate strategy and operational management, leading the team in continuous innovation with over 30 years in automation equipment manufacturing.',
    about_team_2_role: 'Chief Engineer', about_team_2_desc: 'Leads the R&D department, specializing in high-temperature material engineering and automation mechanism design, with extensive experience in semiconductor process equipment development.',
    about_team_3_role: 'Sales Director', about_team_3_desc: 'Oversees business development and client relationship management, deeply understanding client needs to provide the most suitable automation solutions across industries.',
    about_eyebrow_cta: 'CONTACT US',
    about_cta_title: 'Partner With Hsin-Chan Industrial for a Precision Future',
    about_cta_desc: 'Whether for product quotations, technical consultation, or project collaboration, contact Hsin-Chan Industrial Co., Ltd.\'s expert team. We commit to responding within 1–2 business days.',
    about_cta_btn: 'Contact Us',

    pp_eyebrow_top: 'PRODUCTS', pp_eyebrow_lineup: 'PRODUCT LINEUP', pp_eyebrow_qa: 'QUALITY ASSURANCE', pp_eyebrow_quote: 'REQUEST QUOTE',
    pp_banner_title: 'Hsin-Chan Industrial Products',
    pp_banner_lead: 'Hsin-Chan Industrial Co., Ltd.\'s six high-temperature industrial consumable product lines deliver reliable material solutions for demanding environments across the semiconductor, foundry, and energy industries.',
    pp_overview_title: 'Six Product Lines', pp_overview_lead: 'All products pass rigorous quality control and are designed for high-temperature, corrosive, and precision industrial environments.',
    pp_p1_tag: 'Injection Molding Consumables', pp_p1_title: 'One-Piece Barrel',
    pp_p1_desc: 'Manufactured with a one-piece molding process, the seamless design significantly reduces the risk of molten metal leakage. Widely used in aluminum die-casting, magnesium alloy die-casting, and other non-ferrous metal injection molding processes.',
    pp_p1_s1: 'Material: Nitrided Steel', pp_p1_s2: 'Hardness: HRC 60–65', pp_p1_s3: 'Custom dimensions available', pp_p1_btn: 'Request Quote',
    pp_p1_app: 'Die Casting (UBE/Toshiba/Shibaura) / Injection Molding', pp_p1_mat: 'SKD61 Tool Steel', pp_p1_vtag: 'Integral Tube',
    pp_p2_tag: 'High-Temp Process Consumables', pp_p2_title: 'SiC Protection Tube',
    pp_p2_desc: 'Made from high-purity silicon carbide (SiC), rated above 1600°C with excellent corrosion resistance. Widely used in semiconductor process furnace tubes, aluminum melting, and a range of high-temperature industrial applications.',
    pp_p2_s1: 'Max Temp: >1600°C', pp_p2_s2: 'Material: High-purity SiC', pp_p2_s3: 'Thermal shock & corrosion resistant', pp_p2_btn: 'Request Quote',
    pp_p2_app: 'Semiconductor / Foundry', pp_p2_mat: 'High-Purity SiC', pp_p2_vtag: 'SiC Tube · 1600°C',
    pp_p3_tag: 'Kiln Industrial Consumables', pp_p3_title: 'Refractory Materials',
    pp_p3_desc: 'A range of refractory bricks, castables, and insulation wool for high-temperature kilns and furnaces, offering excellent thermal insulation that extends furnace service life and reduces energy loss.',
    pp_p3_s1: 'Max Temp: up to 1800°C by grade', pp_p3_s2: 'High compressive strength, low thermal conductivity', pp_p3_s3: 'Multiple grades and sizes available', pp_p3_btn: 'Request Quote',
    pp_p3_type: 'Refractory Brick / Castable / Insulation Wool', pp_p3_app: 'Kilns / Melting Furnaces / Heat Treatment Furnaces', pp_p3_temp: '1200°C – 1800°C', pp_p3_vtag: 'Refractory',
    pp_p4_tag: 'Semiconductor Process Module', pp_p4_title: 'High-Concentration Nano-Bubble Fluid Module',
    pp_p4_desc: 'Generates high-concentration nano-bubble fluid with bubble size below 100nm. Applied in semiconductor process water, biomedical equipment cleaning, and liquid cooling systems — energy-saving, high-density, and chemical-additive-free.',
    pp_p4_s1: 'Bubble Size: <100nm high-concentration nano-bubbles', pp_p4_s2: 'Applications: Semiconductor / Biomedical / Liquid Cooling', pp_p4_s3: 'Advantages: Energy-saving, high-density, chemical-free', pp_p4_btn: 'Request Quote',
    pp_p4_use: 'Semiconductor / Biomedical / Liquid Cooling', pp_p4_merit: 'Energy-saving / High-density / Chemical-free', pp_p4_vtag: 'Nano-Bubble · <100nm',
    pp_p5_tag: 'Precision Temperature Components', pp_p5_title: 'Heater',
    pp_p5_desc: 'A wide range of industrial electric heating elements, including silicon carbide heating rods, SiC rods, and MoSi₂ heaters. Custom specifications available to meet customer requirements, suitable for high-temperature furnace tubes, heat treatment equipment, and industrial kilns.',
    pp_p5_s1: 'Max Temp: up to 1200°C by type', pp_p5_s2: 'Multiple power ratings (50W–10kW)', pp_p5_s3: 'Custom shape and wiring configuration', pp_p5_btn: 'Request Quote',
    pp_p5_type: 'SiC Rod / MoSi₂ / Platinum Wire', pp_p5_heat: 'Up to 1800°C', pp_p5_spec: 'Steel / Glass / Foundry', pp_p5_vtag: 'Heater',
    pp_p6_tag: 'Precision Measurement Components', pp_p6_title: 'Thermocouple',
    pp_p6_desc: 'Industrial temperature sensors available in K, J, R, S, and B types. Suitable for a wide range of high-temperature process measurements, offering fast response and high accuracy, with enhanced durability when paired with protection tubes.',
    pp_p6_s1: 'Range: −200°C to +1800°C', pp_p6_s2: 'Multiple types and sheath materials', pp_p6_s3: 'IEC / JIS compliant', pp_p6_btn: 'Request Quote',
    pp_p6_model: 'Types K / J / R / S / B', pp_p6_measure: 'Up to 1750°C', pp_p6_spec: 'Standard / Custom', pp_p6_vtag: 'Thermocouple',

    // ── Product Detail Pages Shared ──
    pd_eyebrow_specs: 'SPECIFICATIONS', pd_specs_title: 'Specifications',
    pd_custom_title: 'Need Custom Specifications?', pd_custom_desc: 'Hsin-Chan Industrial offers full customization services. Tell us your requirements and our engineers will respond within 1-2 business days.',
    pd_contact_btn: 'Contact Us', pd_contact_tel_label: 'Phone:', pd_contact_email_label: 'Email:',
    pd_contact_hours_label: 'Business Hours:', pd_contact_hours_val: 'Mon-Fri 08:00-17:30',
    pd_eyebrow_types: 'PRODUCT TYPES', pd_types_title: 'Product Types',
    pd_eyebrow_industries: 'INDUSTRIES', pd_industries_title: 'Industries',
    pd_eyebrow_faq: 'FAQ', pd_faq_title: 'Frequently Asked Questions',
    pd_eyebrow_related: 'RELATED PRODUCTS', pd_related_title: 'Related Products',
    pd_viewall: 'View All Products', pd_viewall_desc: 'Six Core High-Temperature Industrial Consumable Lines',
    pd_eyebrow_quote: 'GET A QUOTE', pd_quote_btn: 'Get a Quote',

    // ── product-thermocouple.html ──
    pth_eyebrow: 'THERMOCOUPLES', pth_title: 'Thermocouples', pth_breadcrumb: 'Industrial Thermocouples',
    pth_lead: 'A full range of industrial thermocouples — Types K, J, T, E, R, S, and B — covering -200°C to +1820°C and compliant with the IEC 584 international standard.',
    pth_spec1_label: 'Supported Types', pth_spec1_val: 'Types K / J / T / E / R / S / B',
    pth_spec2_label: 'Temperature Range', pth_spec2_val: '-200°C to +1820°C (varies by type)',
    pth_spec3_label: 'Compliance Standards', pth_spec3_val: 'IEC 584 (International), JIS C 1602 (Japan)',
    pth_spec4_label: 'Protection Tube Material', pth_spec4_val: 'Stainless Steel / Silicon Carbide (SiC) / High-Purity Ceramic / Quartz',
    pth_spec5_label: 'Wiring Configuration', pth_spec5_val: 'Terminal Block / Connector / Lead Wire',
    pth_spec6_label: 'Accuracy Class', pth_spec6_val: 'Class 1 / Class 2 (per IEC 584)',
    pth_spec7_label: 'Customization Options', pth_spec7_val: 'Length, outer diameter, connector, and protection tube are all customizable.',
    pth_type1_name: 'Type K (Chromel-Alumel)', pth_type1_desc: 'The most versatile type, -200°C to +1372°C, with excellent oxidation resistance — the industrial standard of choice.',
    pth_type2_name: 'Type J (Iron-Constantan)', pth_type2_desc: '-40°C to +750°C, suited to reducing atmospheres, and low cost.',
    pth_type3_name: 'Type T (Copper-Constantan)', pth_type3_desc: '-270°C to +400°C, high accuracy at low temperatures — ideal for food refrigeration and freezing.',
    pth_type4_name: 'Type E (Chromel-Constantan)', pth_type4_desc: '-270°C to +1000°C, the highest sensitivity — ideal for high-precision low-temperature applications.',
    pth_type5_name: 'Type R/S (Platinum Rhodium-Platinum)', pth_type5_desc: '0°C to +1767°C, precious-metal construction with high accuracy — ideal for precision high-temperature processes.',
    pth_type6_name: 'Type B (Platinum Rhodium 30%-Platinum Rhodium 6%)', pth_type6_desc: '0°C to +1820°C, the highest-temperature type — suited to high-temperature oxidizing atmospheres.',
    pth_ind1: 'Injection Molding — Barrel temperature monitoring, mold temperature measurement',
    pth_ind2: 'Aluminum Alloy Casting — Real-time furnace and pouring temperature monitoring',
    pth_ind3: 'Semiconductor Process — Diffusion furnace temperature control, CVD process temperature monitoring',
    pth_ind4: 'Heat Treatment — Annealing and quenching furnace temperature recording',
    pth_ind5: 'Food Processing — Pasteurization, baking oven temperature control (Type T)',
    pth_ind6: 'EV Battery Manufacturing — Battery module temperature monitoring',
    pth_faq1_q: 'What’s the difference between Type K and Type J thermocouples, and which should I choose?',
    pth_faq1_a: 'Type K is suited to general industrial environments (oxidizing atmosphere, up to 1372°C), is the most widely used type on the market, and spare parts are easy to source. Type J is suited to reducing or vacuum atmospheres, up to 750°C, and costs less. Injection molding plants mostly use Type K, while ferrous metal heat treatment sometimes uses Type J.',
    pth_faq2_q: 'How do I choose the protection tube material for a thermocouple?',
    pth_faq2_a: 'Stainless Steel (SUS304/316): for general industrial environments, corrosion-resistant, 100-1100°C. Silicon Carbide (SiC): for molten aluminum and highly corrosive environments, impact-resistant, up to 1600°C. High-Purity Ceramic (Al₂O₃): for high-temperature, corrosive-gas environments, up to 1700°C.',
    pth_faq3_q: 'Can Hsin-Chan Industrial’s thermocouples be used with my existing temperature controller?',
    pth_faq3_a: 'Yes. Hsin-Chan thermocouples comply with the IEC 584 international standard and are compatible with commercial temperature controllers from major brands (Omron, Yokogawa, Shinko, etc.). Please let us know your controller model when ordering, and we’ll help confirm the wiring.',
    pth_faq4_q: 'How long is the lead time for custom thermocouples?',
    pth_faq4_a: 'Standard in-stock types ship in 3-5 business days. Custom dimensions typically take 7-14 business days. Please provide your application, temperature range, and installation space, and we’ll help with selection.',
    pth_rel1_title: 'Industrial Heaters', pth_rel1_desc: 'Heating elements used together with thermocouples',
    pth_rel2_title: 'Silicon Carbide Protection Tubes', pth_rel2_desc: 'Protection tubes for high-temperature molten environments',
    pth_cta_title: 'Need thermocouple specifications and a quote?',
    pth_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    // ── product-heater.html ──
    phe_eyebrow: 'INDUSTRIAL HEATERS', phe_title: 'Industrial Heaters', phe_breadcrumb: 'Industrial Heaters',
    phe_lead: 'Precision heating elements for everything from injection molding to aluminum die casting, rated up to 1200°C, with full customization support.',
    phe_spec1_label: 'Max Operating Temperature', phe_spec1_val: '1,200°C',
    phe_spec2_label: 'Power Range', phe_spec2_val: '50W to 10kW',
    phe_spec3_label: 'Voltage Specifications', phe_spec3_val: '110V / 220V / 380V (customizable)',
    phe_spec4_label: 'Heating Element Material', phe_spec4_val: 'Nickel-Chromium Alloy (Ni-Cr) / FeCrAl / Kanthal A-1',
    phe_spec5_label: 'Insulation Material', phe_spec5_val: 'Magnesium Oxide (MgO) Powder Fill',
    phe_spec6_label: 'Sheath Material', phe_spec6_val: 'SUS304 / SUS316 Stainless Steel',
    phe_spec7_label: 'Mounting Type', phe_spec7_val: 'Flange / Threaded / Insertion',
    phe_spec8_label: 'Customization Options', phe_spec8_val: 'Outer diameter, length, lead wire position, and power output are all customizable.',
    phe_type1_name: 'Injection Molding Band Heaters', phe_type1_desc: 'Wrap around the barrel to provide even heating, suited to a wide range of injection molding machines.',
    phe_type2_name: 'Industrial Heater Rods', phe_type2_desc: 'Insertion design for precise spot heating, ideal for mold preheating and hot runner systems.',
    phe_type3_name: 'Ceramic Heaters', phe_type3_desc: 'High-temperature, impact-resistant — suited to industrial furnaces, semiconductor equipment, and annealing furnaces.',
    phe_type4_name: 'Infrared Heaters', phe_type4_desc: 'Non-contact heating, suited to plastic preheating, food processing, and surface treatment.',
    phe_type5_name: 'Industrial Furnace Heating Tubes', phe_type5_desc: 'High-power, high-temperature design for aluminum die casting pouring systems and heat treatment furnaces.',
    phe_ind1: 'Injection Molding — Barrel band heaters, mold heater rods',
    phe_ind2: 'Aluminum Die Casting — Pouring system heater tubes, holding furnace heating elements',
    phe_ind3: 'Semiconductor Process — Diffusion and oxidation furnace peripheral heating systems',
    phe_ind4: 'Industrial Heat Treatment — Annealing furnace, tempering furnace, and oven heating elements',
    phe_ind5: 'EV Manufacturing — Battery electrode drying, motor stator preheating',
    phe_faq1_q: 'What’s the maximum temperature Hsin-Chan Industrial’s heaters can withstand?',
    phe_faq1_a: 'Industrial heating elements have a maximum operating temperature of 1200°C (nickel-chromium alloy). Ceramic heaters can reach 800-1200°C depending on the model. Infrared heaters typically operate at 400-700°C. Please choose the appropriate model based on your actual operating environment.',
    phe_faq2_q: 'How do I order a custom heater?',
    phe_faq2_a: 'Please call 03-381-4497 or fill out our online inquiry form, specifying: outer diameter, length, voltage, power, mounting method, and material requirements. We commit to responding with a quote within 1-2 business days.',
    phe_faq3_q: 'What’s the difference between band heaters and heater rods?',
    phe_faq3_a: 'Band heaters wrap around the outside of the barrel to provide uniform circumferential heating, and are standard equipment on injection molding machines. Heater rods use an insertion design, ideal for precise spot heating inside molds. Both can be used with thermocouple-based temperature control systems.',
    phe_faq4_q: 'How long is the lead time?',
    phe_faq4_a: 'Standard in-stock sizes typically ship in 3-5 business days. Custom specifications take 7-14 business days depending on complexity. Expedited processing is available for urgent orders — please contact our sales team.',
    phe_rel1_title: 'Thermocouples', phe_rel1_desc: 'Temperature sensors used together with heaters',
    phe_rel2_title: 'Integrated Barrels', phe_rel2_desc: 'Injection molding barrels with integrated band heaters',
    phe_cta_title: 'Need industrial heater specifications and a quote?',
    phe_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    // ── product-sic-tube.html ──
    psic_eyebrow: 'SiC PROTECTION TUBES', psic_title: 'Silicon Carbide Protection Tubes', psic_breadcrumb: 'Silicon Carbide Protection Tubes',
    psic_lead: 'Made from high-purity silicon carbide (SiC), rated above 1600°C with excellent thermal shock resistance, oxidation resistance, and corrosion resistance — ideal for semiconductor processes and aluminum casting environments.',
    psic_spec1_label: 'Material', psic_spec1_val: 'High-Purity Silicon Carbide (SiC)',
    psic_spec2_label: 'Purity', psic_spec2_val: '> 99%',
    psic_spec3_label: 'Max Operating Temperature', psic_spec3_val: '> 1,600°C (continuous use)',
    psic_spec4_label: 'Thermal Shock Resistance', psic_spec4_val: 'Excellent — withstands rapid heating and cooling',
    psic_spec5_label: 'Oxidation Resistance', psic_spec5_val: 'Excellent (in high-temperature oxidizing atmospheres)',
    psic_spec6_label: 'Corrosion Resistance', psic_spec6_val: 'Excellent (except strong acids/alkalis)',
    psic_spec7_label: 'Hardness', psic_spec7_val: 'HV 2,500 (Mohs 9+)',
    psic_spec8_label: 'Customization Options', psic_spec8_val: 'Outer diameter, inner diameter, length, and end shape are all customizable.',
    psic_type1_name: 'Reaction-Bonded SiC (RBSiC)', psic_type1_desc: 'Lower cost, suited to general high-temperature protection such as molten aluminum processing.',
    psic_type2_name: 'Recrystallized SiC (ReSiC)', psic_type2_desc: 'High purity and high strength, suited to ultra-high-temperature processes such as semiconductor diffusion furnaces.',
    psic_type3_name: 'Nitride-Bonded SiC (NSiC)', psic_type3_desc: 'Excellent thermal shock resistance, suited to environments with frequent rapid heating and cooling.',
    psic_ind1: 'Semiconductor Process — Diffusion furnace tube protection, LPCVD processes',
    psic_ind2: 'Aluminum Alloy Casting — Thermocouple protection tubes and pouring guides in molten aluminum',
    psic_ind3: 'Crystal Growth Furnaces — Components for silicon ingot growth equipment',
    psic_ind4: 'Ceramic Sintering Furnaces — High-temperature sintering protection components',
    psic_ind5: 'Chemical Processing Equipment — Corrosion-resistant protection for high-temperature piping',
    psic_faq1_q: 'What’s the difference between SiC protection tubes and stainless steel protection tubes?',
    psic_faq1_a: 'Stainless steel protection tubes are limited to roughly 1100-1200°C, lose strength at high temperatures, and corrode easily when in contact with molten aluminum. SiC protection tubes withstand temperatures above 1600°C, remain chemically inert in molten aluminum environments, and last 3-10 times longer than stainless steel — making them the top choice for aluminum casting facilities.',
    psic_faq2_q: 'Can SiC protection tubes be used in hydrogen atmospheres for semiconductor processes?',
    psic_faq2_a: 'SiC performs excellently in oxidizing atmospheres. In reducing or hydrogen atmospheres, high-purity recrystallized SiC (ReSiC) performs better. Please let us know your specific process conditions so we can help with selection.',
    psic_faq3_q: 'How do I order custom SiC protection tubes?',
    psic_faq3_a: 'Please provide: outer diameter (mm), inner diameter (mm), length (mm), operating temperature, operating environment (atmosphere, contact media), and quantity. Call 03-381-4497 or fill out our online inquiry form — we will respond with a quote within 1-2 business days.',
    psic_rel1_title: 'Thermocouples', psic_rel1_desc: 'Temperature sensors used together with SiC protection tubes',
    psic_rel2_title: 'Refractory Materials', psic_rel2_desc: 'Construction materials for high-temperature furnace linings',
    psic_cta_title: 'Need silicon carbide protection tube specifications and a quote?',
    psic_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    // ── product-refractory.html ──
    pref_eyebrow: 'REFRACTORY MATERIALS', pref_title: 'Refractory Materials', pref_breadcrumb: 'Refractory Materials',
    pref_lead: 'Refractory bricks, refractory mortar, and shaped refractory products rated up to 1800°C — suited to a wide range of metallurgical furnaces, industrial kilns, and high-temperature process equipment.',
    pref_spec1_label: 'Max Operating Temperature', pref_spec1_val: 'Up to 1,800°C (depending on material)',
    pref_spec2_label: 'Refractory Brick Types', pref_spec2_val: 'High-Alumina Brick / Silica Brick / Magnesia Brick / Silicon Carbide Brick',
    pref_spec3_label: 'Unshaped Refractories', pref_spec3_val: 'Castables / Plastic Refractories / Gunning Mixes / Coating Materials',
    pref_spec4_label: 'Compressive Strength', pref_spec4_val: 'High (depending on material specification)',
    pref_spec5_label: 'Thermal Conductivity', pref_spec5_val: 'Low (excellent insulation)',
    pref_spec6_label: 'Thermal Stability', pref_spec6_val: 'Excellent (strong resistance to rapid heating and cooling)',
    pref_spec7_label: 'Customization Service', pref_spec7_val: 'Lining design solutions tailored to your furnace configuration',
    pref_type1_name: 'High-Alumina Brick', pref_type1_desc: 'Al₂O₃ content >45%, rated 1400-1800°C, high strength — suited to electric arc furnace and induction furnace linings.',
    pref_type2_name: 'Silica Brick', pref_type2_desc: 'SiO₂ content >93%, rated 1600-1700°C — suited to coke ovens and glass furnaces.',
    pref_type3_name: 'Magnesia Brick', pref_type3_desc: 'MgO content >85%, resistant to basic slag — suited to steelmaking converters and electric arc furnace hearths.',
    pref_type4_name: 'Silicon Carbide Refractory Brick', pref_type4_desc: 'High strength and high thermal conductivity — suited to burner sleeves and kiln car decking.',
    pref_type5_name: 'Unshaped Refractories (Castables)', pref_type5_desc: 'Can be cast into any shape, ideal for repairing irregular furnace linings and monolithic construction.',
    pref_ind1: 'Steelmaking — Electric arc furnace, converter, and ladle lining',
    pref_ind2: 'Non-Ferrous Metal Smelting — Aluminum, copper, and zinc melting furnace linings',
    pref_ind3: 'Industrial Kilns — Ceramic kilns, glass furnaces, cement kilns',
    pref_ind4: 'Chemical Processing Equipment — High-temperature reactors and combustion furnaces',
    pref_ind5: 'Foundry Industry — Cupola furnaces, induction furnaces, pouring troughs',
    pref_faq1_q: 'How do I choose the right refractory brick material?',
    pref_faq1_a: 'Key considerations: (1) operating temperature — confirm the required refractoriness; (2) slag properties — silica brick for acidic slag, magnesia brick for basic slag; (3) mechanical load — high-alumina brick for high-load applications; (4) construction method — shaped bricks for monolithic construction, castables for irregular sections. We offer free consultation to help you select the right material.',
    pref_faq2_q: 'How should refractory materials be maintained?',
    pref_faq2_a: 'Avoid rapid heating and cooling (follow the furnace curing curve); regularly inspect joints for leaks; repair any localized damage promptly. Hsin-Chan Industrial offers post-installation maintenance consultation.',
    pref_faq3_q: 'What is the minimum order quantity?',
    pref_faq3_a: 'Please call 03-381-4497 for details, as this depends on the product model and specifications. Standard items can be ordered in small quantities, with discounts available for bulk purchases.',
    pref_rel1_title: 'Silicon Carbide Protection Tubes', pref_rel1_desc: 'High-temperature protection tubes for furnace interiors',
    pref_rel2_title: 'Industrial Heaters', pref_rel2_desc: 'Heating elements for kilns and furnaces',
    pref_cta_title: 'Need refractory material specifications and a quote?',
    pref_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    // ── product-integrated-barrel.html ──
    pib_eyebrow: 'INTEGRATED BARRELS', pib_title: 'Integrated Barrels', pib_breadcrumb: 'Integrated Barrels',
    pib_lead: 'A seamless, single-piece design that eliminates the leakage risks of conventional barrels. Made from bimetallic alloy or nitrided alloy for outstanding wear and corrosion resistance.',
    pib_spec1_label: 'Design Feature', pib_spec1_val: 'Single-piece, seamless construction that eliminates leakage risk',
    pib_spec2_label: 'Material Options', pib_spec2_val: 'Nitrided Steel / Bimetallic Alloy / High-Speed Steel Coating',
    pib_spec3_label: 'Nitrided Steel Hardness', pib_spec3_val: 'HRC 60-65',
    pib_spec4_label: 'Bimetallic Alloy Hardness', pib_spec4_val: 'HRC 60-68',
    pib_spec5_label: 'High-Speed Steel Coating Hardness', pib_spec5_val: 'HRC 62-66',
    pib_spec6_label: 'Compatible Materials', pib_spec6_val: 'General Plastics / Glass-Fiber-Filled Resins / Engineering Plastics / Corrosive Materials (PVC)',
    pib_spec7_label: 'Customization Options', pib_spec7_val: 'Inner diameter, outer diameter, length, and band heater integration are all customizable.',
    pib_type1_name: 'Nitrided Steel Barrels', pib_type1_desc: 'Suited to general plastics, highly wear-resistant with a surface hardness of HRC 60-65 and excellent value.',
    pib_type2_name: 'Bimetallic Alloy Barrels', pib_type2_desc: 'Feature a high-alloy wear-resistant lining cast into the inner wall, suited to highly abrasive engineering plastics such as glass-fiber- or mineral-filled resins.',
    pib_type3_name: 'High-Speed Steel Coated Barrels', pib_type3_desc: 'Suited to corrosive materials such as PVC and flame retardants, balancing wear resistance and corrosion resistance.',
    pib_ind1: 'Injection Molding Plants — Production of a wide range of plastic products',
    pib_ind2: 'Automotive Parts Manufacturing — Injection molding of high-strength engineering plastics',
    pib_ind3: 'Electronic Components — Precision small-scale injection molding',
    pib_ind4: 'Packaging Materials — High-speed injection for high-volume production',
    pib_ind5: 'Medical Devices — Barrels meeting strict cleanliness requirements',
    pib_faq1_q: 'What’s the difference between integrated barrels and standard barrels?',
    pib_faq1_a: 'Integrated barrels are cast or forged as a single piece with no seams. Conventional segmented barrels have multiple joints that, over time, can leak material due to thermal expansion and contraction. The integrated design greatly improves sealing performance, reduces mold-change downtime, and extends service life.',
    pib_faq2_q: 'How do I know if my injection molding machine needs a new barrel?',
    pib_faq2_a: 'Consider replacement if you notice: (1) excessive clearance between the screw and barrel causing reduced injection pressure; (2) scorching or color variation in products; (3) cracks or dents on the barrel’s outer surface. Our engineers can help with on-site diagnosis.',
    pib_faq3_q: 'How much more expensive are bimetallic barrels compared to nitrided barrels, and are they worth it?',
    pib_faq3_a: 'Bimetallic barrels typically cost 1.5-2.5 times more than nitrided barrels. However, when processing materials containing glass fiber or mineral fillers, nitrided barrels may only last 1/3 to 1/5 as long as bimetallic barrels. Over the long run, bimetallic barrels require fewer replacements and incur lower downtime costs, making them the more economical choice in most cases.',
    pib_rel1_title: 'Industrial Heaters', pib_rel1_desc: 'Band heaters for barrels',
    pib_rel2_title: 'Thermocouples', pib_rel2_desc: 'For barrel temperature monitoring',
    pib_cta_title: 'Need integrated barrel specifications and a quote?',
    pib_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    // ── product-graphite-tube.html ──
    pgt_eyebrow: 'NANO-BUBBLE FLUID MODULE', pgt_title: 'High-Concentration Nano-Bubble Fluid Module', pgt_breadcrumb: 'High-Concentration Nano-Bubble Fluid Module',
    pgt_lead: 'Generates high-concentration nano-bubble fluid with bubble sizes under 100nm, for use in semiconductor processes, medical devices, and liquid cooling systems — delivering energy savings, high density, and chemical-free cleaning.',
    pgt_spec1_label: 'Bubble Size', pgt_spec1_val: '< 100 nm',
    pgt_spec2_label: 'Bubble Concentration', pgt_spec2_val: '> 10⁸ bubbles/mL (high density)',
    pgt_spec3_label: 'Compatible Media', pgt_spec3_val: 'Pure water, semiconductor process water, coolant, medical-grade water',
    pgt_spec4_label: 'Gas Source', pgt_spec4_val: 'N₂ / O₂ / CO₂ / Air (selectable based on application)',
    pgt_spec5_label: 'Installation', pgt_spec5_val: 'In-line pipe installation, compatible with existing process water lines and liquid cooling circuits',
    pgt_spec6_label: 'Function', pgt_spec6_val: 'Physical bubble collapse generates micro-impact forces that break down contaminants and biofilms — no chemicals required',
    pgt_spec7_label: 'Customization Options', pgt_spec7_val: 'Flow rate, concentration, and gas type can all be customized to production line requirements',
    pgt_type1_name: 'Semiconductor Process Type', pgt_type1_desc: 'Suited for wafer cleaning and process water systems, improving cleaning efficiency and reducing chemical usage.',
    pgt_type2_name: 'Liquid Cooling System Type', pgt_type2_desc: 'Installed in data center or equipment liquid cooling circuits to enhance heat dissipation efficiency and suppress pipe scaling and biofilm growth.',
    pgt_type3_name: 'Medical Device Type', pgt_type3_desc: 'Applied to medical equipment cleaning and sterilization-assist processes, providing a gentle, chemical-residue-free cleaning solution.',
    pgt_ind1: 'Semiconductor Manufacturing — Wafer cleaning, process water quality improvement, back-end process cleaning',
    pgt_ind2: 'Medical Industry — Medical equipment cleaning, laboratory water purification support',
    pgt_ind3: 'Data Center Liquid Cooling — Improved heat dissipation for server liquid cooling circuits, scale and biofilm suppression',
    pgt_ind4: 'Precision Electronics Manufacturing — Cleaning of high-end electronic components, chemical-residue-free processes',
    pgt_faq1_q: 'What are nanobubbles, and how do they differ from ordinary microbubbles?',
    pgt_faq1_a: 'Nanobubbles are tiny bubbles less than 100nm in diameter that carry a negative zeta potential in liquid, making them resistant to rising and coalescing and allowing them to remain suspended in fluid for extended periods. Compared to conventional microbubbles, nanobubbles have a vastly greater surface-area-to-volume ratio, dramatically improving contact efficiency with liquids and particles — resulting in significant effects for cleaning, mass transfer, and heat dissipation applications.',
    pgt_faq2_q: 'What fields can the high-concentration nano-bubble fluid module be applied to?',
    pgt_faq2_a: 'It is mainly applied in three areas: (1) Semiconductor processes — wafer cleaning and process water quality improvement; (2) Medical industry — medical equipment cleaning and sterilization assistance; (3) Liquid cooling systems — improving heat dissipation efficiency in data center and equipment liquid cooling circuits while suppressing pipe scaling and biofilm growth.',
    pgt_faq3_q: 'How do nanobubbles achieve chemical-free cleaning?',
    pgt_faq3_a: 'When nanobubbles collapse in liquid, they release localized energy and generate micro-impact forces that physically loosen and remove particulate contaminants and biofilms adhering to surfaces — achieving cleaning results without relying on chemical agents. This significantly reduces costs for chemical procurement and wastewater treatment while being more environmentally friendly.',
    pgt_faq4_q: 'What conditions are needed to adopt the high-concentration nano-bubble fluid module? How is it maintained?',
    pgt_faq4_a: 'The module is installed in-line with piping and is compatible with most existing process water or liquid cooling lines — simply connect it to a water source and power supply to operate. Routine maintenance only requires periodic filter replacement, with no chemical replenishment needed, greatly simplifying maintenance and reducing operating costs. Let us know your flow rate and site requirements, and our engineers will help with sizing and selection.',
    pgt_rel1_title: 'Silicon Carbide Protection Tubes', pgt_rel1_desc: 'Critical consumables for semiconductor and high-temperature processes',
    pgt_rel2_title: 'Thermocouples', pgt_rel2_desc: 'Precision temperature monitoring applications',
    pgt_cta_title: 'Need specifications and a quote for the high-concentration nano-bubble fluid module?',
    pgt_cta_desc: 'Tell us about your operating environment, specification requirements, and quantity — our engineers will respond with the best solution within 1-2 business days.',

    pp_qa_title: 'Quality Assurance', pp_qa_lead: 'Every product undergoes a rigorous quality control process — from raw material selection to final product testing, with full traceability at every stage.',
    pp_qa_1_title: 'Premium Material Sourcing', pp_qa_1_desc: 'All products are made from industry-certified, high-purity raw materials, ensuring chemical composition and physical properties meet demanding industrial application standards.',
    pp_qa_2_title: 'Pre-Shipment Inspection', pp_qa_2_desc: 'Every batch is tested for dimensions, heat resistance, strength, and other performance criteria before shipment, with complete inspection reports to ensure consistent quality.',
    pp_qa_3_title: 'Custom Specifications', pp_qa_3_desc: 'Custom production service for non-standard sizes, manufactured to match customer equipment specifications with flexible lead times to meet diverse application needs.',
    pp_cta_title: 'Need a Custom Specification or Quote?',
    pp_cta_desc: 'Tell us about your application environment and specification requirements — Hsin-Chan Industrial\'s product engineers will recommend the best material solution and provide a quote.',
    pp_cta_btn: 'Get a Quote Now',

    srv_eyebrow_top: 'SERVICES', srv_eyebrow_cta: 'START PROJECT',
    srv_page_title: 'Hsin-Chan Industrial Services',
    srv_page_lead: 'Hsin-Chan Industrial Co., Ltd. offers seven automation services covering digital planning, robotic arm integration, machine vision inspection, equipment intelligence upgrades, and nano-bubble fluid applications — one-stop manufacturing solutions.',
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
    srv_d7_num: 'SERVICE 07', srv_d7_tag: 'Nano-Bubble Application', srv_d7_title: 'High-Concentration Nano-Bubble Fluid Industrial Applications',
    srv_d7_desc: 'Deploys high-concentration nano-bubble fluid modules for semiconductor process water, biomedical equipment cleaning, and data center liquid cooling — covering selection assessment, piping integration, and performance validation. Physical nano-bubbles replace chemical additives, delivering an energy-saving, chemical-free process upgrade.',
    srv_d7_p1: 'Improves semiconductor process water quality and assists wafer cleaning', srv_d7_p2: 'Assists biomedical equipment cleaning/sterilization, reducing chemical dependency',
    srv_d7_p3: 'Boosts data center liquid cooling heat dissipation and suppresses pipe scaling', srv_d7_p4: 'Chemical-free operation lowers wastewater treatment costs and environmental impact', srv_d7_btn: 'Enquire About This Service',
    srv_cta_title: 'Ready to Launch Your Automation Project?',
    srv_cta_desc: 'Whether it\'s a new production line or upgrading existing equipment, Hsin-Chan Industrial Co., Ltd.\'s engineering team will deliver the most suitable solution.',
    srv_cta_btn: 'Contact Us Now',

    tech_eyebrow_top: 'TECHNOLOGY INSIGHT',
    tech_eyebrow_cta: 'COLLABORATE WITH US',
    tech_page_title: 'Hsin-Chan Industrial Technology Insights',
    tech_page_lead: 'From semiconductor processes to humanoid robots, exploring Hsin-Chan Industrial Co., Ltd.\'s precision components and high-temperature materials across six cutting-edge application fields.',
    tech_d1_num: 'TOPIC 01', tech_d1_tag: 'Semiconductor', tech_d1_title: 'Semiconductor Process',
    tech_d1_desc: 'Semiconductor wafer processing requires precise control of molten metals and chemical materials in ultra-high-temperature, highly corrosive environments, along with stringent requirements for process water and cleaning quality. Hsin-Chan Industrial Co., Ltd.\'s SiC protection tubes, with their outstanding thermal shock resistance and chemical inertness, serve as critical consumables in diffusion furnace tubes and crystal growth equipment. The High-Concentration Nano-Bubble Fluid Module is used for wafer cleaning and process water quality improvement, delivering energy-efficient, chemical-additive-free cleaning.',
    tech_d1_p1: 'SiC protection tube: rated to 1600°C, oxidation and corrosion resistant', tech_d1_p2: 'High-Concentration Nano-Bubble Fluid Module: bubble size <100nm, used for wafer cleaning and process water quality improvement',
    tech_d1_p3: 'One-piece barrel: ensures pure, contamination-free transport of molten silicon', tech_d1_p4: 'Custom dimensions to fit various crystal growth furnaces and PECVD equipment', tech_d1_btn: 'Enquire About Applications',
    tech_d2_num: 'TOPIC 02', tech_d2_tag: 'Electric Vehicle', tech_d2_title: 'Electric Vehicle',
    tech_d2_desc: 'EV battery modules, motors, and power electronics components demand rigorous thermal management. Hsin-Chan Industrial Co., Ltd.\'s refractory materials and precision ceramic components are widely used in battery pack structural protection, motor stator insulation, and aluminum alloy motor housing production processes, ensuring the long-term stability of materials in high-temperature, high-pressure environments.',
    tech_d2_p1: 'Battery module fire-resistant insulation panels for structural protection', tech_d2_p2: 'Aluminum casting process protection tubes for motor housing production',
    tech_d2_p3: 'Ceramic thermocouples for precise motor operating temperature monitoring', tech_d2_p4: 'High-temperature insulation materials for power modules (IGBT/SiC MOSFET)', tech_d2_btn: 'Enquire About Applications',
    tech_d3_num: 'TOPIC 03', tech_d3_tag: 'Silicon Photonics', tech_d3_title: 'Silicon Photonics',
    tech_d3_desc: 'Silicon photonics integrates optical components on silicon substrates for high-speed optical communications and AI acceleration. Hsin-Chan Industrial Co., Ltd. provides high-precision ceramic carriers, high-temperature fixtures, and process protection components for photonic chip packaging, ensuring the structural integrity of chips during precision processes such as bonding and annealing.',
    tech_d3_p1: 'High-precision ceramic positioning fixtures for fiber array alignment', tech_d3_p2: 'High-temperature process carriers for stable bonding support',
    tech_d3_p3: 'Alumina ceramic insulation for uniform heat distribution in annealing furnaces', tech_d3_p4: 'Custom specifications to match foundry process node requirements', tech_d3_btn: 'Enquire About Applications',
    tech_d4_num: 'TOPIC 04', tech_d4_tag: 'Humanoid Robot', tech_d4_title: 'Humanoid Robot',
    tech_d4_desc: 'Humanoid robot joint drives, end effectors, and sensing systems require parts that balance lightweight construction with high precision. With 30 years of precision machining experience, Hsin-Chan Industrial Co., Ltd. supplies humanoid robot manufacturers with aluminum alloy structural parts, precision drive sleeves, and wear-resistant ceramic components — with strict dimensional control ensuring motion accuracy and long service life.',
    tech_d4_p1: 'Precision joint drive sleeves to maintain motion repeatability', tech_d4_p2: 'Lightweight aluminum alloy structural parts to reduce body weight and improve agility',
    tech_d4_p3: 'Wear-resistant ceramic guide components to extend joint service life', tech_d4_p4: 'High-precision tolerance control: ±0.01mm class machining capability', tech_d4_btn: 'Enquire About Applications',
    tech_d5_num: 'TOPIC 05', tech_d5_tag: 'Quantum Computing', tech_d5_title: 'Quantum Computing',
    tech_d5_desc: 'Quantum computer dilution refrigerators must maintain qubits near absolute zero (15 mK), placing extreme demands on component thermal conductivity, EMI protection, and ultra-precision machining. Hsin-Chan Industrial Co., Ltd. provides high-purity oxygen-free copper components and precision ceramic insulation for low-temperature environments, helping quantum computing equipment manufacturers overcome manufacturing process bottlenecks.',
    tech_d5_p1: 'High-purity oxygen-free copper (OFC) precision parts with excellent thermal and electrical conductivity', tech_d5_p2: 'Ceramic insulation structural components designed for low-temperature thermal isolation',
    tech_d5_p3: 'Ultra-precision machining: surface roughness Ra ≤ 0.4μm', tech_d5_p4: 'Strict cleanliness control to avoid contamination affecting quantum states', tech_d5_btn: 'Enquire About Applications',
    tech_d6_num: 'TOPIC 06', tech_d6_tag: 'UAV / Drone', tech_d6_title: 'UAV / Drone',
    tech_d6_desc: 'Drones pursue the ultimate balance of lightweight construction and structural strength. Critical components like motor mounts, drive shafts, and gimbal frames require precision machining and strict quality control. Hsin-Chan Industrial Co., Ltd. provides high-strength aluminum alloy structural parts, carbon fiber composite inserts, and custom tooling, supporting full-lifecycle manufacturing needs from prototype development through mass production.',
    tech_d6_p1: 'Aerospace aluminum alloy (7075-T6) lightweight structural parts', tech_d6_p2: 'Motor mounts with precision bores to ensure motor concentricity',
    tech_d6_p3: 'Carbon fiber composite embedded metal inserts', tech_d6_p4: 'Rapid prototyping and flexible small-batch production services', tech_d6_btn: 'Enquire About Applications',
    tech_cta_title: 'Explore Precision Material Applications in Your Field?',
    tech_cta_desc: 'Hsin-Chan Industrial Co., Ltd.\'s technical team welcomes collaboration with manufacturers across cutting-edge technology fields to explore material solutions and push the boundaries of technology together.',
    tech_cta_btn: 'Contact the Technical Team',

    career_page_title: 'Hsin-Chan Industrial Careers',
    career_page_lead: 'Join Hsin-Chan Industrial Co., Ltd., carry forward 30 years of precision manufacturing craftsmanship, and embrace the opportunities and challenges of the automation and new materials era together.',
    career_eyebrow_top: 'CAREERS',
    career_apply_label: 'Apply by Email',
    career_apply_note: 'Please include "Position Title + Name" in the subject line, with your complete resume and personal statement',
    career_apply_btn: 'Apply Now',
    career_eyebrow_jobs: 'OPEN POSITIONS',
    career_jobs_title: 'Current Openings',
    career_job1_tag: 'Mechanical Design', career_job1_title: 'Senior Mechanical Design Engineer',
    career_job1_req1: 'Design precision parts, modules, and fixtures using Solid Edge / SolidWorks',
    career_job1_req2: 'Collaborate with manufacturing on design verification, drawing control, and process improvement',
    career_job1_req3: 'Education: College degree or above in mechanical engineering or related field, with 5+ years of design experience',
    career_job1_req4: 'Familiarity with GD&T tolerance design and precision machining processes preferred',
    career_job2_tag: 'Sales & Marketing', career_job2_title: 'Product Sales Engineer',
    career_job2_req1: 'Develop and maintain domestic and international clients, promoting precision parts and automation solutions',
    career_job2_req2: 'Interpret customer technical specifications and provide quotations, technical support, and after-sales service',
    career_job2_req3: 'Education: College degree or above, mechanical or industrial engineering background preferred',
    career_job2_req4: 'Communication skills in Chinese/English or Japanese preferred',
    career_job3_tag: 'Automation Technology', career_job3_title: 'Automation Equipment Engineer',
    career_job3_req1: 'Plan, design, and integrate automated production equipment and line systems',
    career_job3_req2: 'PLC programming (Mitsubishi iQ-F / iQ-R) and HMI integration development',
    career_job3_req3: 'Education: College degree or above in electrical, mechatronics, or automation control',
    career_job3_req4: 'Experience with robotic arm integration or vision system applications preferred',
    career_job4_tag: 'Procurement & Supply Chain', career_job4_title: 'Supply Chain Manager',
    career_job4_req1: 'Supplier development and evaluation, price negotiation, and delivery management',
    career_job4_req2: 'Material procurement planning, inventory management, and logistics coordination',
    career_job4_req3: 'Education: College degree or above in industrial management, supply chain, or industrial engineering',
    career_job4_req4: 'Proficiency with ERP systems; manufacturing procurement experience preferred',
    career_job5_tag: 'Manufacturing Technician', career_job5_title: 'Assembly Technician',
    career_job5_req1: 'Perform precision mechanical parts assembly per engineering drawings and SOPs',
    career_job5_req2: 'Conduct post-assembly functional testing, precision measurement, and quality self-inspection',
    career_job5_req3: 'Education: High school or above; mechanical-related major preferred',
    career_job5_req4: 'Experience in precision assembly or electrical wiring preferred; trainees welcome',
    career_eyebrow_benefits: 'EMPLOYEE BENEFITS',
    career_ben_title: 'Employee Benefits',
    career_ben1_title: 'Perfect Attendance Bonus', career_ben1_desc: 'A monthly bonus for employees with perfect attendance, rewarding dedication and consistent commitment to work.',
    career_ben2_title: 'Year-End Bonus', career_ben2_desc: 'A year-end bonus based on company performance and individual contributions, sharing the fruits of company growth with employees.',
    career_ben3_title: 'Insurance', career_ben3_desc: 'Labor insurance, national health insurance, and group accident insurance, fully covered by the company as required by law for worry-free protection.',
    career_ben4_title: 'Free Meals', career_ben4_desc: 'The company provides lunch for employees, easing daily expenses so staff can focus on work without worry.',
    career_ben5_title: 'Domestic Trips', career_ben5_desc: 'Regular domestic employee trips to strengthen camaraderie and build team cohesion.',
    career_ben6_title: 'Birthday Gift', career_ben6_desc: 'A birthday gift given to employees during their birthday month, expressing the company’s appreciation and genuine care for every team member.',
    career_ben7_title: 'Holiday Bonuses', career_ben7_desc: 'Holiday bonuses for the Dragon Boat Festival, Mid-Autumn Festival, and Lunar New Year, thanking employees for their hard work.',
    career_ben8_title: 'Year-End Banquet', career_ben8_desc: 'An annual year-end banquet to thank all employees for their year of hard work, celebrating success together and looking forward to the new year.',
    career_eyebrow_join: 'JOIN OUR TEAM',
    career_cta_title: 'Ready to Join Hsin-Chan Industrial Co., Ltd.?',
    career_cta_desc: 'Send your resume to hc3814497@gmail.com — we look forward to building Hsin-Chan Industrial Co., Ltd.\'s next 50 years together with you.',
    career_cta_btn: 'Submit Your Resume Now',

    contact_eyebrow_top: 'CONTACT US',
    contact_page_title: 'Contact Hsin-Chan Industrial',
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

    faq_title: 'Frequently Asked Questions', faq_lead: 'Find answers quickly. For more questions, feel free to', faq_contact_link: 'contact us',

    idx_eyebrow_genchi: 'GENCHI GENBUTSU',
    genchi_title: 'Genchi Genbutsu',
    genchi_desc: "Toyota's core principle: never trust second-hand reports — go to the actual place, confirm with your own eyes, measure with your own hands. At Hsin-Chan Industrial, engineers visit every client's facility before a project begins, gaining a deep understanding of the real production environment, equipment space constraints, and operator workflows. Only by truly reading the shop floor can we design automation systems that truly work.",
    genchi_spec1_label: 'Site', genchi_spec1_val: 'Requirements interviews & workflow observation',
    genchi_spec2_label: 'Measure', genchi_spec2_val: 'Equipment space & interference assessment',
    genchi_spec3_label: 'Analyze', genchi_spec3_val: 'Takt Time on-site measurement',
    genchi_cta: 'Learn our approach', genchi_img_tag: 'Genchi Genbutsu',

    idx_eyebrow_kaizen: 'KAIZEN',
    kaizen_title_1: 'Kaizen', kaizen_title_2: 'The Endless Path of Improvement',
    kaizen_desc: "Kaizen is not a one-time revolution — it is the micro-evolution of each passing day. Hsin-Chan Industrial embeds the Kaizen spirit into every design phase: reducing changeover time (SMED), introducing mistake-proofing devices (Poka-yoke), and establishing standard operating procedures (SOP). We never stop asking, 'Can this be better?' — until we find the answer.",
    kaizen_spec1_val: 'SMED design to minimize changeover downtime',
    kaizen_spec2_label: 'Poka-yoke', kaizen_spec2_val: 'Poka-yoke mechanisms to eliminate errors at the source',
    kaizen_spec3_label: 'Standardize', kaizen_spec3_val: 'SOP documentation for process consistency',
    kaizen_cta: 'View Automation Services', kaizen_img_tag: 'Kaizen',

    marquee_1: 'Semiconductor Process Clients', marquee_2: 'Aluminum Foundries', marquee_3: 'EV Parts Manufacturers',
    marquee_4: 'Precision Machinery Plants', marquee_5: 'Electronic Packaging Fabs', marquee_6: 'Chemical Equipment Makers',

    tech_lead: 'Continuously pushing the boundaries of manufacturing performance through Kaizen, Poka-yoke, and Standardization.',
    tps_tag_1: 'Kaizen × Semiconductor', tps_1_title: 'Kaizen Culture in Precision Manufacturing',
    tps_1_desc: 'The micron-level demands of semiconductor manufacturing are the perfect stage for Kaizen. Incremental improvements to each process step accumulate into sustained yield breakthroughs.',
    tps_tag_2: 'JIT × EV Production', tps_2_title: 'JIT Production in EV Manufacturing Plants',
    tps_2_desc: "EV components are highly diverse. JIT's principle of 'right time, right quantity, right item' is the key tool for eliminating inventory waste on battery assembly lines.",
    tps_tag_3: 'Poka-yoke × Robot Arms', tps_3_title: 'Poka-yoke Design for Zero-Error Robot Arms',
    tps_3_desc: 'Embedding mistake-proofing mechanisms into robot arm integration stops gripper errors and positioning deviations before they occur — this is the core design logic for zero-defect production.',
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

    // Re-render FAQ in new language (contentApi may not be defined yet on first call)
    if (typeof contentApi !== 'undefined') contentApi.refresh();
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
  let cachedData = null;

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



  function renderFaqList(data, lang) {
    if (!FAQ_LIST || !data) return;
    const key = lang === 'ja' ? 'faq_ja' : lang === 'en' ? 'faq_en' : 'faq';
    const items = (data[key] || data.faq || []).filter(validateFaqItem).slice(0, 30);
    if (!items.length) return;

    FAQ_LIST.innerHTML = '';
    const fragment = document.createDocumentFragment();
    items.forEach((item, i) => fragment.appendChild(renderFaqItem(item, i)));
    FAQ_LIST.appendChild(fragment);

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
  }

  async function init() {
    if (!FAQ_LIST) return;
    try {
      const res = await fetch('content.json');
      if (!res.ok) throw new Error('content.json fetch failed');
      cachedData = await res.json();
      renderFaqList(cachedData, i18n.current());
    } catch (e) {
      if (FAQ_LIST) FAQ_LIST.closest('section')?.remove();
    }
  }

  function refresh() {
    if (cachedData) renderFaqList(cachedData, i18n.current());
  }

  return { init, refresh };
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
