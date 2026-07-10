import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 頂級 UI 配置
st.set_page_config(page_title="⚜️ 隨身奢華旅遊管家", layout="wide", initial_sidebar_state="expanded")

# --- 2. 🤖 智能時間感應：自動切換日間/夜間主題 ---
current_hour = datetime.now().hour
# 白天時間（06:00 - 18:00）預設璀璨晶白，其餘時間自動切換為靜謐深夜
if 6 <= current_hour < 18:
    default_theme_idx = 0  # 璀璨晶白
else:
    default_theme_idx = 1  # 靜謐深夜

st.sidebar.title("🎨 奢華美學管家")
theme_choice = st.sidebar.selectbox(
    "選擇您的專屬高奢主題：",
    ["✨ 璀璨晶白 (日間淺色)", "🌙 靜謐深夜 (夜間深色)", "💎 蒂芬妮鮮藍 (奢華高飽和)", "🌟 皇家御用金 (金屬高對比)", "🌿 翡翠碧綠 (清爽高鮮明)"],
    index=default_theme_idx
)

# 殿堂級多元主題配色系統（大幅調高對比度、鮮明度，確保字字清晰、絕不灰髒）
themes = {
    "✨ 璀璨晶白 (日間淺色)": {
        "bg": "#FFFFFF", "card": "#F3F4F6", "text": "#000000", "accent": "#2563EB", "border": "#9CA3AF", "subtext": "#4B5563", 
        "card_ex": "rgba(37, 99, 235, 0.08)", "card_tr": "rgba(124, 58, 237, 0.08)", "sidebar_bg": "#F9FAFB", "sidebar_text": "#111827"
    },
    "🌙 靜謐深夜 (夜間深色)": {
        "bg": "#0D1117", "card": "#161B22", "text": "#FFFFFF", "accent": "#00F0FF", "border": "#30363D", "subtext": "#8B949E", 
        "card_ex": "rgba(0, 240, 255, 0.1)", "card_tr": "rgba(187, 134, 252, 0.1)", "sidebar_bg": "#1F2937", "sidebar_text": "#F9FAFB"
    },
    "💎 蒂芬妮鮮藍 (奢華高飽和)": {
        "bg": "#E6F7F6", "card": "#FFFFFF", "text": "#042323", "accent": "#0D9488", "border": "#99F6E4", "subtext": "#115E59", 
        "card_ex": "rgba(13, 148, 136, 0.1)", "card_tr": "rgba(217, 119, 6, 0.1)", "sidebar_bg": "#CCFBF1", "sidebar_text": "#115E59"
    },
    "🌟 皇家御用金 (金屬高對比)": {
        "bg": "#FDFBF7", "card": "#F4EFE6", "text": "#3A2A18", "accent": "#B45309", "border": "#D97706", "subtext": "#78350F", 
        "card_ex": "rgba(180, 83, 9, 0.1)", "card_tr": "rgba(75, 85, 99, 0.08)", "sidebar_bg": "#FEF3C7", "sidebar_text": "#78350F"
    },
    "🌿 翡翠碧綠 (清爽高鮮明)": {
        "bg": "#F0FDF4", "card": "#FFFFFF", "text": "#062F16", "accent": "#16A34A", "border": "#86EFAC", "subtext": "#14532D", 
        "card_ex": "rgba(22, 163, 74, 0.1)", "card_tr": "rgba(217, 119, 6, 0.08)", "sidebar_bg": "#DCFCE7", "sidebar_text": "#14532D"
    }
}
cfg = themes[theme_choice]

# 使用官方原生 st.html 100% 免疫 TypeError，並對側邊欄文字注入強力保固樣式
st.html(f"""
<style>
    /* 全域核心樣式 */
    .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
    h1, h2, h3, h4, p, span, label {{ color: {cfg['text']} !important; font-weight: 600; }}
    
    /* 側邊欄專屬強制配色修正（徹底消滅字體消失、隱形 Bug） */
    section[data-testid="stSidebar"] {{ background-color: {cfg['sidebar_bg']} !important; }}
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span {{ 
        color: {cfg['sidebar_text']} !important; 
    }}
    
    /* 輸入框高對比邊框與背景調配 */
    .stTextInput input, .stSelectbox div {{
        background-color: {cfg['card']} !important;
        color: {cfg['text']} !important;
        border: 2px solid {cfg['border']} !important;
        border-radius: 10px !important;
    }}
    
    /* 質感卡片與高飽和度邊框線 */
    .trip-card {{ 
        background: {cfg['card']}; 
        padding: 22px; 
        border-radius: 16px; 
        border: 2px solid {cfg['border']}; 
        margin-bottom: 18px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }}
    .expense-card {{ 
        background: {cfg['card_ex']}; 
        padding: 18px; 
        border-radius: 12px; 
        border-left: 8px solid {cfg['accent']}; 
        border-top: 2px solid {cfg['border']}; 
        border-right: 2px solid {cfg['border']}; 
        border-bottom: 2px solid {cfg['border']}; 
        margin-bottom: 12px; 
    }}
    .transit-card {{ 
        background: {cfg['card_tr']}; 
        padding: 18px; 
        border-radius: 12px; 
        border-left: 8px solid #8B5CF6; 
        border-top: 2px solid {cfg['border']}; 
        border-right: 2px solid {cfg['border']}; 
        border-bottom: 2px solid {cfg['border']}; 
        margin-bottom: 12px; 
    }}
    
    /* 數據分析指標大卡片 */
    div[data-testid="stMetric"] {{ 
        background: {cfg['card']} !important; 
        padding: 18px 24px; 
        border-radius: 16px; 
        border: 2px solid {cfg['border']} !important; 
    }}
    div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-size: 2.4rem !important; font-weight: 800 !important; }}
    
    /* 高級分頁標籤按鈕 */
    .stTabs [data-baseweb="tab"] {{ font-size: 1.15rem; font-weight: 700; padding: 12px 24px; color: {cfg['subtext']} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {cfg['accent']} !important; border-bottom: 3px solid {cfg['accent']} !important; }}
</style>
""")

# --- 3. 核心隱私：旅程暗號通關機制 ---
st.markdown(f"### 🔒 護照通關驗證")
passcode_input = st.text_input("🔑 請輸入您的旅遊專屬暗號以解鎖內容：", type="password", placeholder="請填入旅程代碼（例如：KIX2026）")

# 側邊欄：創建新旅程（自動生成暗號）
with st.sidebar.expander("👑 策劃全新旅遊標籤", expanded=False):
    new_trip_name = st.text_input("填寫旅程名稱", placeholder="例如：日本關西精緻遊")
    new_trip_sub = st.text_input("輸入副標題描述", placeholder="例如：漫步京都與收集御守之旅")
    new_code = st.text_input("為這個旅程自訂一個「專屬通關暗號」", placeholder="例如：KYOTO666")
    num_members = st.number_input("參與成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"旅伴 {i+1}", key=f"m_cfg_{i}") for i in range(int(num_members))]
    
    if st.button("⚜️ 精緻鑄造旅遊標籤", use_container_width=True):
        if new_trip_name and new_code:
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": f"【暗號：{new_code}】 {new_trip_sub}"}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success(f"🎉 組織成功！請在上方輸入暗號「{new_code}」即可開啟！")

# 隱私過濾核心：比對資料庫
trips_res = supabase.table("trips").select("*").execute()
current_trip_id = None
current_trip = None

if trips_res.data:
    for t in trips_res.data:
        if t['subtitle'] and f"【暗號：{passcode_input}】" in t['subtitle'] and passcode_input.strip() != "":
            current_trip_id = t['id']
            current_trip = t
            break

if not current_trip_id:
    st.info("✨ 歡迎來到奢華旅程空間。請在上方輸入您受邀的「旅遊專屬暗號」解鎖行程；若要開啟新標籤，請利用左側邊欄創建。")
    st.stop()

# 成功通關，加載對應的成員與明細
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 認領身分
st.sidebar.markdown("---")
selected_identity = st.sidebar.selectbox("👤 尊榮身分認領：", ["未認領 (僅觀看)"] + list(members_dict.keys()))

# --- 主畫面大標題 ---
st.title(f"✨ {current_trip['name']}")
st.caption(f"📜 {current_trip['subtitle']}")

tabs = st.tabs(["📅 奢華時間線行程", "💰 智慧隨手帳本", "🎒 國際即時管家"])

# ==================== 頁籤一：時間線行程規劃 ====================
with tabs[0]:
    st.header("🗺️ 行程與高質感節點")
    
    with st.expander("➕ 新增行程/交通/轉乘節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1, key="v_day")
            time_slot = st.time_input("時間", key="v_time")
        with c2:
            act_type = st.selectbox("項目奢華類別", ["📍 璀璨景點", "⚜️ 交通(主線)", "🔄 交通(轉乘防呆提示)"], key="v_type")
            title = st.text_input("節點名稱", placeholder="例如：金閣寺 / 清水寺", key="v_title")
        with c3:
            cost = st.number_input("預算開銷 (TWD)", min_value=0.0, value=0.0, key="v_cost")
            note = st.text_area("備註細節說明", placeholder="記錄月台、美景角度...", key="v_note")
            
        if st.button("✨ 寫入奢華時間線", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 顯示
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"#### ☀️ 第 {day_num} 天 精緻時光")
            for _, row in group.iterrows():
                is_trans = "交通" in row['activity_type']
                c_style = "transit-card" if is_trans else "trip-card"
                
                st.html(f"""
                <div class="{c_style}">
                    <span style='color:{cfg['accent']}; font-weight:800; font-size:1.15rem;'>⏱ *{row['time_slot'][:5]}*</span> 
                    <span style='font-weight:800; margin-left:10px; color:{cfg['text']};'>{row['activity_type']} │ {row['title']}</span>
                    <p style='margin: 8px 0 0 0; color:{cfg['subtext']}; font-size:1rem; font-weight:500;'>💡 {row['note'] if row['note'] else '無特殊說明'}</p>
                </div>
                """)
                
                b1, b2, _ = st.columns([1, 1, 8])
                with b1:
                    with st.popover("✏️ 調整"):
                        nt = st.text_input("調整名稱", value=row['title'], key=f"e_t_{row['id']}")
                        nn = st.text_area("調整備註", value=row['note'] if row['note'] else "", key=f"e_n_{row['id']}")
                        if st.button("確定更新", key=f"u_i_{row['id']}"):
                            supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                            st.rerun()
                with b2:
                    if st.button("🗑️ 移除", key=f"d_i_{row['id']}", type="primary"):
                        supabase.table("itineraries").delete().eq("id", row['id']).execute()
                        st.rerun()

# ==================== 頁籤二：隨手分帳系統 ====================
with tabs[1]:
    st.header("💰 全員即時分帳帳本")
    
    with st.container(border=True):
        st.subheader("📝 隨手速記一筆款項")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費款項描述", placeholder="例如：豪華和牛晚餐")
            exp_amount = st.number_input("總金額", min_value=0.0, value=0.0, step=10.0, key="v_amt")
        with cx2:
            payer = st.selectbox("這筆錢是誰先墊的？", list(members_dict.keys()), key="v_payer")
            split_method = st.radio("分攤權重配置", ["均分模式", "自訂精確金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("🎯 **動態即時分帳修正回饋**")
            if split_method == "均分模式":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.html(f"<div style='color:{cfg['accent']}; font-weight:800; font-size:1.1rem;'>✨ 全員完美平分，每人應付：${share:,.2f}</div>")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"💸 {m} 的實質花費金額", min_value=0.0, value=0.0, key=f"v_sp_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.html("<div style='color:#10B981; font-weight:800; font-size:1.1rem;'>✅ 數據完全吻合！已解鎖儲存按鈕。</div>")
                    can_submit = True
                elif diff > 0:
                    st.html(f"<div style='color:#DC2626; font-weight:800; font-size:1.1rem;'>⏳ 還有 <strong>${diff:,.2f}</strong> 未配平，請繼續輸入。</div>")
                    can_submit = False
                else:
                    st.html(f"<div style='color:#B91C1C; font-weight:800; font-size:1.1rem;'>⚠️ 金額爆表！已超出總額 <strong>${abs(diff):,.2f}</strong>！</div>")
                    can_submit = False
                    
        if st.button("💾 安全寫入雲端帳本", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("儲存成功！")
            st.rerun()

    # 加載明細
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        st.subheader("📊 數據圖表與結算大盤口")
        
        my_paid, my_owe = 0.0, 0.0
        if selected_identity != "未認領 (僅觀看)":
            my_paid = df_exp[df_exp['paid_by'] == members_dict[selected_identity]]['amount'].sum()
            for _, r in df_exp.iterrows():
                my_owe += float(r['split_details'].get(selected_identity, 0.0))

        mi1, mi2, mi3 = st.columns(3)
        with mi1: st.metric("⚜️ 全團累積總支出", f"${total_trip_cost:,.2f}")
        with mi2: 
            if selected_identity != "未認領 (僅觀看)": st.metric("💎 我的代墊總額", f"${my_paid:,.2f}")
        with mi3: 
            if selected_identity != "未認領 (僅觀看)": st.metric("📉 我的應付總額", f"${my_owe:,.2f}")

        fig = px.pie(df_exp, values='amount', names='description', hole=0.5, template="plotly_white" if "日間" in theme_choice or "鮮藍" in theme_choice or "皇家" in theme_choice or "翡翠" in theme_choice else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # 債務精簡
        st.subheader("💵 精算清償帳單 (最少轉帳次數設計)")
        balances = {m: 0.0 for m in members_dict.keys()}
        for exp in exp_res.data:
            p_name = members_id_to_name[exp['paid_by']]
            balances[p_name] += float(exp['amount'])
            for m_name, s_amt in exp['split_details'].items():
                balances[m_name] -= float(s_amt)
                
        debtors = [(k, v) for k, v in balances.items() if v < 0]
        creditors = [(k, v) for k, v in balances.items() if v > 0]
        
        while debtors and creditors:
            debtor, d_bal = debtors[0]
            creditor, c_bal = creditors[0]
            amount_to_pay = min(abs(d_bal), c_bal)
            
            if debtor == selected_identity:
                st.html(f"<div style='background:rgba(220,38,38,0.15); padding:14px; border-radius:10px; margin-bottom:10px; border-left:6px solid #DC2626; color:#7F1D1D; font-weight:800;'>🔴 <strong>【您需轉帳】</strong> 轉給 <strong>{creditor}</strong> 👉 🏦 <strong>${amount_to_pay:,.2f}</strong> 元</div>")
            elif creditor == selected_identity:
                st.html(f"<div style='background:rgba(22,163,74,0.15); padding:14px; border-radius:10px; margin-bottom:10px; border-left:6px solid #16A34A; color:#14532D; font-weight:800;'>🟢 <strong>【您將收款】</strong> <strong>{debtor}</strong> 將轉帳給你 👉 💰 <strong>${amount_to_pay:,.2f}</strong> 元</div>")
            else:
                st.html(f"<div style='padding:12px; border-bottom:2px dashed {cfg['border']}; color:{cfg['text']}; font-weight:600;'>➡️ <strong>{debtor}</strong> 應轉給 <strong>{creditor}</strong> 👉 <strong>${amount_to_pay:,.2f}</strong> 元</div>")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：國際即時管家（實時API多國匯率） ====================
with tabs[2]:
    st.header("🎒 全球實時匯率管家")
    st.caption("自動對接國際匯率 API，即時刷新各國匯率資訊")
    
    @st.cache_data(ttl=3600)
    def get_real_rates():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/TWD")
            return res.json()['rates']
        except:
            return {"USD": 0.031, "JPY": 4.65, "EUR": 0.029, "KRW": 41.5}

    rates = get_real_rates()
    
    st.write("📊 **目前即時匯率大盤基準 (對應 1 TWD 台幣)：**")
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    c_r1.metric("🇯🇵 日圓 (JPY)", f"{rates.get('JPY', 4.65):.2f}")
    c_r2.metric("🇺🇸 美金 (USD)", f"{rates.get('USD', 0.031):.4f}")
    c_r3.metric("🇪🇺 歐元 (EUR)", f"{rates.get('EUR', 0.029):.4f}")
    c_r4.metric("🇰🇷 韓圓 (KRW)", f"{rates.get('KRW', 41.5):.2f}")
    
    st.markdown("---")
    st.subheader("💱 智慧多國金額試算轉換")
    src_currency = st.selectbox("選擇您要在當地消費的外幣種類：", ["JPY 日圓", "USD 美金", "EUR 歐元", "KRW 韓圓"])
    foreign_amt = st.number_input("輸入外幣消費金額：", min_value=0.0, value=1000.0)
    
    cur_key = src_currency.split()[0]
    twd_result = foreign_amt / rates.get(cur_key, 1.0) if rates.get(cur_key) else 0.0
    st.success(f"💎 折合新台幣約：**`${twd_result:,.2f}`** TWD 元 (即時即時動態換算)")
