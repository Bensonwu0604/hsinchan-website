#!/usr/bin/env python3
"""
欣晨工業 —《第一性原理拆解智慧製造》選題知識庫

50 個智慧製造核心關鍵技術，分屬 8 大維度，彼此以 links 互相連結。

每一集不是「講一個題目」，而是「拆解兩個概念的交會點」：
    主概念 × 相關概念 → 一個全新的切角
這讓 50 個概念能展開成數百集，而不是一年就播完。

選題同時顧兩件事：
  1. 廣度 — 主概念依序輪完 50 個，不重複
  2. 落地 — 配對時優先讓每集至少有一個概念落在欣晨真正的技術領域
           （relevance >= 2），否則該集無法自然連結到公司能力
"""

from datetime import date

# ── 8 大維度（依數據流由下而上排列）──────────────────────────────────────────
DIMENSIONS = {
    "sensing":    "端點感知與數據採集",
    "network":    "工業網路與通訊",
    "systems":    "製造營運與資訊系統",
    "ai":         "人工智慧與數據分析",
    "simulation": "數位化模擬與控制",
    "hardware":   "自動化與硬體裝備",
    "supply":     "智慧供應鏈與物流",
    "governance": "資訊安全、永續與管理",
}

# relevance：欣晨工業能否自然連結到自身技術能力
#   2 = 核心業務（熱電偶、工業加熱器、AOI、機械手臂整合、夾治具、TPS）
#   1 = 相鄰領域，能以實作經驗發言
#   0 = 可作為知識廣度，但不適合硬扯公司能力
CONCEPTS = [
    # ── 一、端點感知與數據採集 ──────────────────────────────────────────
    dict(id="industrial_sensors", name="工業感測器", dim="sensing", relevance=2,
         desc="擷取溫度、振動、壓力、光學等物理量的終端感知元件。",
         links=["iiot", "pdm", "soft_sensors", "closed_loop"]),
    dict(id="iiot", name="工業物聯網 IIoT", dim="sensing", relevance=1,
         desc="將設備、物料與系統連網的基礎通訊網路與架構。",
         links=["industrial_sensors", "edge_computing", "opc_ua", "ot_security"]),
    dict(id="edge_computing", name="邊緣運算", dim="sensing", relevance=1,
         desc="在機台端進行毫秒級即時運算與數據清洗，降低延遲與頻寬消耗。",
         links=["closed_loop", "vision_ai", "iiot", "private_5g"]),
    dict(id="smart_meters", name="智慧電表與能耗感測", dim="sensing", relevance=2,
         desc="即時監控機台與廠房的電力、水、氣體等資源消耗。",
         links=["carbon_tracking", "green_mfg", "oee", "industrial_sensors"]),
    dict(id="rfid_uwb", name="RFID / UWB 室內定位", dim="sensing", relevance=0,
         desc="物料、夾具與成品在廠內的精準即時位置追蹤。",
         links=["wms", "amr", "e2e_visibility", "mes", "industrial_robots"]),
    dict(id="plc_data", name="PLC 數據擷取", dim="sensing", relevance=1,
         desc="傳統與現代自動化控制器的底層數據導出技術。",
         links=["scada", "opc_ua", "gateways", "closed_loop"]),

    # ── 二、工業網路與通訊 ──────────────────────────────────────────────
    dict(id="private_5g", name="工業 5G 專網", dim="network", relevance=0,
         desc="提供高頻寬、低延遲、海量連線的廠區無線通訊基礎設施。",
         links=["amr", "ar_vr", "edge_computing", "tsn", "cobots"]),
    dict(id="opc_ua", name="OPC UA 協定", dim="network", relevance=1,
         desc="跨廠商、跨平台的工業自動化開放通訊標準與數據模型。",
         links=["plc_data", "mes", "gateways", "data_governance", "industrial_sensors"]),
    dict(id="tsn", name="TSN 時間敏感網路", dim="network", relevance=0,
         desc="確保工業乙太網中關鍵控制數據能精準、無延遲地傳送。",
         links=["closed_loop", "private_5g", "industrial_robots", "plc_data"]),
    dict(id="gateways", name="工業通訊閘道器", dim="network", relevance=1,
         desc="打通舊型機台（OT）與 IT 資訊系統之間的通訊壁壘。",
         links=["plc_data", "opc_ua", "ot_security", "mes", "industrial_sensors"]),
    dict(id="cloud_platform", name="雲端工業平台", dim="network", relevance=0,
         desc="跨廠區數據集中儲存、彈性擴充與全球化運算中心。",
         links=["big_data", "edge_computing", "data_governance", "digital_twin", "pdm"]),

    # ── 三、製造營運與資訊系統 ──────────────────────────────────────────
    dict(id="mes", name="MES 製造執行系統", dim="systems", relevance=1,
         desc="串聯現場排程、派工、物料追蹤與品質回報的生產心臟。",
         links=["aps", "scada", "oee", "erp"]),
    dict(id="scada", name="SCADA 監控系統", dim="systems", relevance=1,
         desc="全廠區即時狀態監控、可視化與遠端控制。",
         links=["plc_data", "mes", "ot_security", "digital_twin", "closed_loop"]),
    dict(id="erp", name="ERP 串接", dim="systems", relevance=0,
         desc="將生產數據與財務、採購、銷售端無縫對接。",
         links=["aps", "mes", "demand_forecast", "e2e_visibility", "oee"]),
    dict(id="plm", name="PLM 產品生命週期管理", dim="systems", relevance=1,
         desc="從研發設計、CAD/CAM 數據到生產製造的全程資料管理。",
         links=["digital_thread", "additive", "smed", "virtual_commissioning"]),
    dict(id="wms", name="WMS 智慧倉儲管理", dim="systems", relevance=0,
         desc="精準管理原料、半成品與成品的庫存狀態與儲位優化。",
         links=["asrs", "rfid_uwb", "amr", "e2e_visibility", "industrial_robots"]),
    dict(id="aps", name="APS 先進規劃與排程", dim="systems", relevance=1,
         desc="基於有限產能與多重約束的動態智慧排程。",
         links=["mes", "smed", "demand_forecast", "oee"]),

    # ── 四、人工智慧與數據分析 ──────────────────────────────────────────
    dict(id="big_data", name="工業大數據", dim="ai", relevance=0,
         desc="處理多源、高頻、非結構化工業數據的架構與技術。",
         links=["machine_learning", "data_governance", "cloud_platform", "rca", "pdm"]),
    dict(id="machine_learning", name="機器學習", dim="ai", relevance=1,
         desc="自動分析歷史生產數據，尋找最適製程參數與規律。",
         links=["soft_sensors", "pdm", "rca", "closed_loop"]),
    dict(id="pdm", name="AI 預測性維護", dim="ai", relevance=2,
         desc="分析機台振動與電流數據，提前預知故障並安排維修。",
         links=["industrial_sensors", "oee", "machine_learning", "digital_twin"]),
    dict(id="vision_ai", name="AI 瑕疵檢測 / Vision AI", dim="ai", relevance=2,
         desc="利用深度學習與電腦視覺替代人工進行高速、高精度品檢。",
         links=["closed_loop", "edge_computing", "industrial_robots", "rca"]),
    dict(id="industrial_llm", name="生成式 AI / 工業 LLM", dim="ai", relevance=1,
         desc="輔助工程師查詢 SOP、撰寫程式碼與診斷產線異常故障。",
         links=["ar_vr", "rca", "data_governance", "human_centric"]),
    dict(id="rca", name="根因分析 AI", dim="ai", relevance=1,
         desc="追蹤產品良率下滑或瑕疵發生的根本物理／化學原因。",
         links=["vision_ai", "machine_learning", "oee", "industrial_sensors"]),
    dict(id="soft_sensors", name="虛擬軟感測器", dim="ai", relevance=2,
         desc="利用 AI 演算法估算無法直接測量的關鍵製程品質變數。",
         links=["industrial_sensors", "machine_learning", "closed_loop", "digital_twin"]),

    # ── 五、數位化模擬與控制 ────────────────────────────────────────────
    dict(id="digital_twin", name="數位雙生", dim="simulation", relevance=1,
         desc="在虛擬空間構建物理設備、產線或全廠的 1:1 動態數位映射。",
         links=["virtual_commissioning", "plant_simulation", "pdm", "digital_thread"]),
    dict(id="digital_thread", name="數位螺紋", dim="simulation", relevance=0,
         desc="貫穿產品從概念、設計、製造到售後維護的全生命週期數據鏈結。",
         links=["plm", "digital_twin", "data_governance", "blockchain_trace", "industrial_sensors"]),
    dict(id="plant_simulation", name="廠房模擬", dim="simulation", relevance=1,
         desc="在擴產前進行虛擬產線物流與瓶頸測試。",
         links=["digital_twin", "aps", "amr", "oee"]),
    dict(id="virtual_commissioning", name="虛擬調試", dim="simulation", relevance=1,
         desc="在真實機台組裝前，於電腦內完成 PLC 與自動化控制程式的測試。",
         links=["digital_twin", "plc_data", "industrial_robots", "smed"]),
    dict(id="closed_loop", name="閉環控制", dim="simulation", relevance=2,
         desc="根據品檢數據自動即時反饋調整前段機台參數。",
         links=["vision_ai", "industrial_sensors", "edge_computing", "soft_sensors"]),

    # ── 六、自動化與硬體裝備 ────────────────────────────────────────────
    dict(id="industrial_robots", name="工業機器人", dim="hardware", relevance=2,
         desc="六軸、SCARA 等傳統高效能自動化加工與搬運手臂。",
         links=["cobots", "smed", "vision_ai", "virtual_commissioning"]),
    dict(id="cobots", name="協作機器人", dim="hardware", relevance=2,
         desc="具備安全防護機制、可與人類作業員近距離共事的機器人。",
         links=["human_centric", "industrial_robots", "smed", "ar_vr"]),
    dict(id="agv", name="AGV 自動導引車", dim="hardware", relevance=1,
         desc="依循固定軌道或磁條的自動物料搬運車。",
         links=["amr", "wms", "asrs", "plant_simulation", "industrial_robots"]),
    dict(id="amr", name="AMR 自主移動機器人", dim="hardware", relevance=1,
         desc="搭載 SLAM 技術、能自主避障與動態規劃路徑的智慧搬運車。",
         links=["agv", "rfid_uwb", "private_5g", "wms", "cobots"]),
    dict(id="additive", name="積層製造 / 3D 列印", dim="hardware", relevance=1,
         desc="實現複雜幾何結構快速原型開發與客製化小批量生產。",
         links=["giga_press", "plm", "smed", "green_mfg"]),
    dict(id="giga_press", name="一體化壓鑄 / 巨型加工裝備", dim="hardware", relevance=1,
         desc="簡化零件數量、極致化結構強度的先進硬體製程。",
         links=["additive", "smed", "green_mfg", "plant_simulation"]),
    dict(id="smed", name="自動夾治具與快速換模 SMED", dim="hardware", relevance=2,
         desc="實現高彈性、多樣少量生產的自動化機構。",
         links=["human_centric", "aps", "industrial_robots", "oee"]),

    # ── 七、智慧供應鏈與物流 ────────────────────────────────────────────
    dict(id="e2e_visibility", name="端到端供應鏈可視化", dim="supply", relevance=0,
         desc="跨企業上下游的即時物料與訂單狀態追蹤。",
         links=["autonomous_supply", "erp", "blockchain_trace", "demand_forecast", "oee"]),
    dict(id="asrs", name="AS/RS 自動化立體倉儲", dim="supply", relevance=1,
         desc="極大化空間利用率的自動化存取與揀貨系統。",
         links=["wms", "agv", "amr", "plant_simulation", "industrial_robots"]),
    dict(id="demand_forecast", name="需求預測模型", dim="supply", relevance=0,
         desc="基於市場數據與 AI 預測最佳備料量與生產排程。",
         links=["aps", "autonomous_supply", "erp", "machine_learning", "smed"]),
    dict(id="autonomous_supply", name="自主供應鏈", dim="supply", relevance=0,
         desc="具備自我修復與動態調整能力的自動補貨與物流網絡。",
         links=["e2e_visibility", "demand_forecast", "aps", "blockchain_trace", "smed"]),
    dict(id="blockchain_trace", name="區塊鏈供應鏈追溯", dim="supply", relevance=0,
         desc="高價值產品履歷的防竄改紀錄。",
         links=["e2e_visibility", "digital_thread", "data_governance", "carbon_tracking", "industrial_sensors"]),

    # ── 八、資訊安全、永續與管理 ────────────────────────────────────────
    dict(id="ot_security", name="OT 資安", dim="governance", relevance=1,
         desc="防止工廠產線與工控系統遭受勒索軟體與駭客攻擊。",
         links=["zero_trust", "gateways", "scada", "iiot", "closed_loop"]),
    dict(id="zero_trust", name="零信任架構", dim="governance", relevance=0,
         desc="針對廠區內所有設備與人員進行嚴格身份驗證。",
         links=["ot_security", "data_governance", "iiot", "cloud_platform", "closed_loop"]),
    dict(id="carbon_tracking", name="碳盤查與碳足跡管理", dim="governance", relevance=1,
         desc="即時計算單一產品在製造過程中的碳排放量。",
         links=["smart_meters", "green_mfg", "e2e_visibility", "oee"]),
    dict(id="green_mfg", name="綠色製造 / 循環經濟", dim="governance", relevance=1,
         desc="提升能源利用率、減少廢料與材料回收再利用。",
         links=["smart_meters", "carbon_tracking", "giga_press", "additive"]),
    dict(id="ar_vr", name="工業 AR / VR 輔助", dim="governance", relevance=0,
         desc="利用擴增實境協助作業員進行遠端維修指導與 SOP 培訓。",
         links=["human_centric", "industrial_llm", "cobots", "private_5g"]),
    dict(id="rpa", name="RPA 機器人流程自動化", dim="governance", relevance=0,
         desc="自動化處理工廠內跨系統表單文書與數據輸入。",
         links=["erp", "industrial_llm", "data_governance", "mes", "oee"]),
    dict(id="data_governance", name="數據治理", dim="governance", relevance=1,
         desc="確保全廠數據格式統一、品質清潔且安全共享。",
         links=["opc_ua", "big_data", "zero_trust", "digital_thread", "soft_sensors"]),
    dict(id="oee", name="OEE 整體設備效率", dim="governance", relevance=2,
         desc="結合可用率、性能率、品質率的精實生產衡量標準。",
         links=["human_centric", "pdm", "smed", "mes"]),
    dict(id="human_centric", name="人機協同與精實思維", dim="governance", relevance=2,
         desc="智慧製造不只是取代人，而是透過技術賦能員工並消除浪費（工業 5.0 核心）。",
         links=["oee", "cobots", "smed", "ar_vr"]),
]

# 切入視角：同一組概念搭配不同視角就是不同的一集，
# 讓有限的概念組合能持續產出真正有差異的新內容
LENSES = [
    ("成本結構", "這件事的錢實際花在哪、又省在哪？拆開成本組成，分辨哪些是物理必然、哪些只是歷史習慣。"),
    ("物理極限", "拆到物理、材料與資訊理論的根本限制：這個做法的理論下限在哪，目前離它還有多遠？"),
    ("導入路徑", "中小型製造廠該從哪一步開始做？第一個月、第一年分別該完成什麼，投資報酬從哪裡回收。"),
    ("常見誤區", "業界普遍做錯的地方：哪些是買了昂貴設備卻沒產生效益的典型陷阱，為什麼會掉進去。"),
    ("人與組織", "技術之外，現場的人與流程要怎麼配合？為什麼同樣的設備在不同工廠效果天差地遠。"),
]

BY_ID = {c["id"]: c for c in CONCEPTS}
INDEX = {c["id"]: i for i, c in enumerate(CONCEPTS)}


def validate():
    """結構自檢：id 唯一、links 都指得到、維度合法、連結對稱性足夠"""
    errors = []
    if len(BY_ID) != len(CONCEPTS):
        errors.append("concept id 有重複")
    for c in CONCEPTS:
        if c["dim"] not in DIMENSIONS:
            errors.append(f"{c['id']}：維度 {c['dim']} 不存在")
        if not c["links"]:
            errors.append(f"{c['id']}：沒有任何 links，無法配對")
        for l in c["links"]:
            if l not in BY_ID:
                errors.append(f"{c['id']}：links 指向不存在的 {l}")
            if l == c["id"]:
                errors.append(f"{c['id']}：links 指向自己")
    if not any(c["relevance"] >= 2 for c in CONCEPTS):
        errors.append("沒有任何欣晨核心領域概念，所有集數都無法自然落地")
    # 每個概念都必須能配到一個欣晨有實力的夥伴，否則那一集無法自然落地
    for c in CONCEPTS:
        if c["relevance"] < 2 and not any(BY_ID[l]["relevance"] >= 2 for l in c["links"] if l in BY_ID):
            errors.append(f"{c['id']}：links 中沒有任何欣晨核心概念，該集無法落地")
    if errors:
        raise ValueError("選題知識庫結構錯誤：\n  - " + "\n  - ".join(errors))
    return True


def week_index(today=None):
    """自 epoch 起算的週序號，讓選題隨週遞增且可重現"""
    today = today or date.today()
    return today.toordinal() // 7


def pick_episode(today=None):
    """選出本集的「主概念 × 相關概念 × 切入視角」

    主概念依序輪完 50 個（約一年不重複）。配對夥伴的起始順位會隨主概念
    本身的序號錯開，避免同一輪裡所有集數都挑到各自 links 的同一個順位，
    那會讓不重複的組合數大幅縮水。

    若主概念與候選夥伴都不在欣晨核心領域（relevance < 2），就改挑一個
    relevance 為 2 的夥伴——validate() 已保證每個概念都找得到。
    """
    w = week_index(today)
    idx = w % len(CONCEPTS)
    primary = CONCEPTS[idx]
    links = primary["links"]
    cycle = w // len(CONCEPTS)

    partner = BY_ID[links[(cycle + idx) % len(links)]]
    if primary["relevance"] < 2 and partner["relevance"] < 2:
        anchors = [BY_ID[l] for l in links if BY_ID[l]["relevance"] >= 2]
        if anchors:
            partner = anchors[(cycle + idx) % len(anchors)]

    # 同一組概念會從兩端各輪到一次（A 挑 B、B 挑 A）。若兩次撞上同一視角
    # 就成了重播，所以視角同時取決於「這次是從哪一端切入」，
    # 保證兩次必定落在不同視角——同樣兩個概念、不同問題，仍是新的一集。
    qi = INDEX[partner["id"]]
    lo, hi = min(idx, qi), max(idx, qi)
    side = 0 if idx == lo else 2
    lens = LENSES[(lo + hi + cycle + side) % len(LENSES)]
    return primary, partner, lens


def describe(primary, partner, lens):
    """組出給編劇的題目與切角"""
    lens_name, lens_desc = lens
    title = f"{primary['name']} × {partner['name']}"
    angle = (
        f"本集主軸是「{primary['name']}」（{DIMENSIONS[primary['dim']]}）："
        f"{primary['desc']}\n"
        f"要與「{partner['name']}」（{DIMENSIONS[partner['dim']]}）交會著談："
        f"{partner['desc']}\n"
        f"重點不是分別介紹兩個名詞，而是拆解它們之間的因果與依賴關係："
        f"為什麼少了其中一個，另一個就發揮不了價值？\n"
        f"本集的切入視角是「{lens_name}」：{lens_desc}\n"
        f"整集的論證都要繞著這個視角展開，不要寫成泛泛的技術介紹。"
    )
    tag = primary["name"].split()[0].split("/")[0]
    return title, tag, angle


if __name__ == "__main__":
    validate()
    print(f"概念總數：{len(CONCEPTS)}")
    for d, label in DIMENSIONS.items():
        n = sum(1 for c in CONCEPTS if c["dim"] == d)
        print(f"  {label}：{n}")
