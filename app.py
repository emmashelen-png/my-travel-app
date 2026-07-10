import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 頂級 UI 配置
st.set_page_config(page_title="⚜️ 隨身奢華旅遊管家", layout="wide", initial_sidebar_state="expanded")

# --- 2. 側邊欄：尊榮自訂美學客製化 ---
st.sidebar.title("⚜️ 奢華美學空間")

theme_choice = st.sidebar.selectbox(
    "✨ 選擇專屬設計語彙：",
    ["🌓 智能感光 (隨系統自動日夜切換)", "✨ 璀璨晶白 (極簡法式白)", "🌙 靜謐安靜 (高階石墨黑)", "💎 蒂芬妮藍 (文藝輕奢)", "🌟 凡爾賽金 (巴洛克奢華)", "🌿 謐境微風 (北歐森林翠)"]
)

# --- 3. 殿堂級美學主題架構配置碼 ---
theme_styles = {
    "✨ 璀璨晶白 (極簡法式白)": {
        "bg": "#F8FAFC", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#0F172A", "sidebar_text": "#334155",
        "accent": "#2563EB", "border": "#E2E8F0", "subtext": "#64748B", "shadow": "0 10px 30px rgba(15,23,42,0.04)"
    },
    "🌙 靜謐安靜 (高階石墨黑)": {
        "bg": "#090D16", "sidebar_bg": "#111726", "card": "#151D30", "text": "#F8FAFC", "sidebar_text": "#E2E8F0",
        "accent": "#00F0FF", "border": "#1E293B", "subtext": "#94A3B8", "shadow": "0 10px 30px rgba(0,0,0,0.5)"
    },
    "💎 蒂芬妮藍 (文藝輕奢)": {
        "bg": "#F0F7F6", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#0B2F2E", "sidebar_text": "#114B4A",
        "accent": "#0D9488", "border": "#CCECE9", "subtext": "#4A7A77", "shadow": "0 10px 25px rgba(13,148,136,0.05)"
    },
    "🌟 凡爾賽金 (巴洛克奢華)": {
        "bg": "#FAF8F5", "sidebar_bg": "#F5F0E6", "card": "#FFFFFF", "text": "#36291C", "sidebar_text": "#4A3B2C",
        "accent": "#D4AF37", "border": "#EAE1D1", "subtext": "#7A6855", "shadow": "0 10px 30px rgba(212,175,55,0.04)"
    },
    "🌿 謐境微風 (北歐森林翠)": {
        "bg": "#F4F7F4", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#152E14", "sidebar_text": "#224D20",
        "accent": "#16A34A", "border": "#D2E0D1", "subtext": "#557353", "shadow": "0 10px 25px rgba(22,163,74,0.04)"
    }
}

# 處理智能感光切換
if theme_choice == "🌓 智能感光 (隨系統自動日夜切換)":
    # 注入標準響應式媒體查詢 CSS，讓瀏覽器主導日夜完美高對比色彩
    st.html("""
    <style>
        @media (prefers-color-scheme: light) {
            .stApp { background: #F8FAFC !important; color: #0F172A !important; }
            section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }
            section[data-testid="stSidebar"] *, .stSelectbox label, .stSidebar p { color: #334155 !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; }
            h1, h2, h3, h4, h5, h6, p, label, span { color: #0F172A !important; }
            .stTabs [data-baseweb="tab"] { color: #64748B !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background: #090D16 !important; color: #F8FAFC !important; }
            section[data-testid="stSidebar"] { background-color: #111726 !important; }
            section[data-testid="stSidebar"] *, .stSelectbox label, .stSidebar p { color: #E2E8F0 !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"] { background: #151D30 !important; border: 1px solid #1E293B !important; }
            h1, h2, h3, h4, h5, h6, p, label, span { color: #F8FAFC !important; }
            .stTabs [data-baseweb="tab"] { color: #94A3B8 !important; }
        }
        div[data-testid="stMetricValue"] { color: #2563EB !important; font-weight: 800 !important; }
    </style>
    """)
    cfg = theme_styles["✨ 璀璨晶白 (極簡法式白)"] # 保留預設物件變數防呆
else:
    cfg = theme_styles[theme_choice]
    # 強力注入指定主題 CSS，重寫 Streamlit 預設的所有髒灰、不鮮明底色
    st.html(f"""
    <style>
        /* 全域底色重寫 */
        .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
        h1, h2, h3, h4, h5, h6, p, span, label {{ color: {cfg['text']} !important; }}
        
        /* 側邊欄高質感校正 - 徹底消除字體消失問題 */
        section[data-testid="stSidebar"] {{ background-color: {cfg['sidebar_bg']} !important; border-right: 1px solid {cfg['border']} !important; }}
        section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {{ color: {cfg['sidebar_text']} !important; }}
        
        /* 頂級卡片工藝與深層陰影 */
        div[data-testid="stMetric"] {{ background: {cfg['card']} !important; border: 1px solid {cfg['border']} !important; box-shadow: {cfg['shadow']} !important; border-radius: 16px !important; }}
        div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-weight: 800 !important; font-size: 2.2rem !important; }}
        
        /* 折疊面板美化 */
        div[data-testid="stExpander"] {{ background: {cfg['card']} !important; border: 1px solid {cfg['border']} !important; border-radius: 14px !important; box-shadow: {cfg['shadow']} !important; }}
        
        /* 奢華頁籤微調 */
        .stTabs [data-baseweb="tab"] {{ color: {cfg['subtext']} !important; font-weight: 600 !important; font-size: 1.1rem !important; padding: 12px 24px !important; }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {cfg['accent']} !important; border-bottom-color: {cfg['accent']} !important; }}
    </style>
    """)

# --- 4. 核心隱私：旅程暗號通關機制 ---
st.markdown("### 🔒 奢華旅行護照驗證")
passcode_input = st.text_input("🔑 輸入您的專屬旅程通關暗號以解鎖藝術庫：", type="password", placeholder="請填入旅程代碼（例如：KIX2026）")

# 側邊欄：創建新旅程（自動生成暗號）
with st.sidebar.expander("👑 策劃全新奢華旅遊標籤", expanded=False):
    new_trip_name = st.text_input("填寫旅程名稱", placeholder="例如：法屬波利尼西亞奢華度假")
    new_trip_sub = st.text_input("輸入副標題描述", placeholder="例如：漫步京都神社與收集御守之旅")
    new_code = st.text_input("自訂一個「通關暗號」", placeholder="例如：JAPAN2026")
    num_members = st.number_input("參與成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"m_lux_{i}") for i in range(int(num_members))]
    
    if st.button("⚜️ 鑄造全新旅遊標籤", use_container_width=True):
        if new_trip_name and new_code:
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": f"【暗號：{new_code.strip()}】 {new_trip_sub}"}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success(f"🎉 成功！請在上方輸入「{new_code}」解鎖！")

# 隱私過濾：比對暗號
trips_res = supabase.table("trips").select("*").execute()
current_trip_id, current_trip = None, None

if trips_res.data:
    for t in trips_res.data:
        if t['subtitle'] and f"【暗號：{passcode_input.strip()}】" in t['subtitle'] and passcode_input.strip() != "":
            current_trip_id = t['id']
            current_trip = t
            break

if not current_trip_id:
    st.info("✨ 尊貴的旅客您好。請在上方輸入您受邀的「專屬暗號」解鎖行程；若要開啟全新專案，請利用左側邊欄創建。")
    st.stop()

# 成功通關，加載數據
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 認領身分
st.sidebar.markdown("---")
selected_identity = st.sidebar.selectbox("👤 尊榮身分認領：", ["未認領 (僅觀看)"] + list(members_dict.keys()))

# --- 主畫面大標題 ---
st.title(f"✨ {current_trip['name']}")
st.caption(f"📜 {current_trip['subtitle']}")

tabs = st.tabs(["📅 奢華時間線行程", "💰 即時全員分帳帳本", "🎒 國際金融管家"])

# ==================== 頁籤一：時間線行程規劃 ====================
with tabs[0]:
    st.header("🗺️ 精緻探險時間規劃線")
    
    with st.expander("➕ 增添全新時光節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1, key="l_day")
            time_slot = st.time_input("時間", key="l_time")
        with c2:
            act_type = st.selectbox("項目類別", ["📍 璀璨景點", "⚜️ 交通(主線)", "🔄 交通(轉乘提示)"], key="l_type")
            title = st.text_input("節點項目名稱", placeholder="例如：清水寺漫步 / 採購特殊御守", key="l_title")
        with c3:
            cost = st.number_input("預算開銷 (TWD)", min_value=0.0, value=0.0, key="l_cost")
            note = st.text_area("備註說明", placeholder="記錄轉乘月台、美景角度提示...", key="l_note")
            
        if st.button("✨ 寫入奢華時間線", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 以高相容性原生 st.container 替代 HTML，100% 免疫型態錯誤，並維持完美外觀
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"#### ☀️ 第 {day_num} 天 精緻日程")
            for _, row in group.iterrows():
                is_trans = "交通" in row['activity_type']
                with st.container(border=True):
                    ic1, ic2 = st.columns([1, 5])
                    ic1.markdown(f"⏱️ **{row['time_slot'][:5]}**")
                    ic2.markdown(f"**{row['activity_type']} │ {row['title']}**\n\n*{row['note'] if row['note'] else '無特殊備註'}*")
                    
                    # 內嵌修改與移除
                    b1, b2, _ = st.columns([1, 1, 8])
                    with b1:
                        with st.popover("✏️ 編輯"):
                            nt = st.text_input("更新名稱", value=row['title'], key=f"lux_t_{row['id']}")
                            nn = st.text_area("更新備註", value=row['note'] if row['note'] else "", key=f"lux_n_{row['id']}")
                            if st.button("確認", key=f"lux_u_{row['id']}"):
                                supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                                st.rerun()
                    with b2:
                        if st.button("🗑️ 移除", key=f"lux_d_{row['id']}", type="primary"):
                            supabase.table("itineraries").delete().eq("id", row['id']).execute()
                            st.rerun()

# ==================== 頁籤二：全員即時分帳帳本 ====================
with tabs[1]:
    st.header("💰 全員雲端同步分帳系統")
    
    with st.container(border=True):
        st.subheader("📝 隨手速記一筆公用款項")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費款項描述", placeholder="例如：頂級米其林晚餐、包車費")
            exp_amount = st.number_input("總金額", min_value=0.0, value=0.0, step=10.0, key="l_amt")
        with cx2:
            payer = st.selectbox("這筆錢是誰先墊的？", list(members_dict.keys()), key="l_payer")
            split_method = st.radio("分攤配置權重", ["全員平均分攤", "自訂精確消費金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("🎯 **分配平衡即時演算**")
            if split_method == "全員平均分攤":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.success(f"✨ 全員完美平分，每人：${share:,.2f}")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"💸 {m} 的實質花費", min_value=0.0, value=0.0, key=f"l_sp_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.success("✅ 金額完全吻合！儲存已解鎖。")
                    can_submit = True
                elif diff > 0:
                    st.warning(f"⏳ 剩餘 <strong>${diff:,.2f}</strong> 未配平...")
                    can_submit = False
                else:
                    st.error(f"⚠️ 爆表！超出 <strong>${abs(diff):,.2f}</strong> 元！")
                    can_submit = False
                    
        if st.button("💾 安全寫入雲端防護帳本", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("儲存成功！")
            st.rerun()

    # 明細加載
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        st.subheader("📊 雲端資產結算面板")
        
        # 尊榮數據卡片排列
        my_paid, my_owe = 0.0, 0.0
        if selected_identity != "未認領 (僅觀看)":
            my_paid = df_exp[df_exp['paid_by'] == members_dict[selected_identity]]['amount'].sum()
            for _, r in df_exp.iterrows():
                my_owe += float(r['split_details'].get(selected_identity, 0.0))

        mi1, mi2, mi3 = st.columns(3)
        with mi1: st.metric("⚜️ 全團累積總花費", f"${total_trip_cost:,.2f}")
        with mi2: 
            if selected_identity != "未認領 (僅觀看)": st.metric("💎 我的代墊開銷", f"${my_paid:,.2f}")
        with mi3: 
            if selected_identity != "未認領 (僅觀看)": st.metric("📉 我的應付底數", f"${my_owe:,.2f}")

        # 精緻圓餅圖
        fig = px.pie(df_exp, values='amount', names='description', hole=0.4, 
                     template="plotly_white" if "白" in theme_choice or "藍" in theme_choice or "金" in theme_choice or "綠" in theme_choice else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # 歷史與債務清償
        st.subheader("💵 最少轉帳次數清償明細")
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
            
            with st.container(border=True):
                if debtor == selected_identity:
                    st.markdown(f"🚨 **【您需還錢】** ➡️ 請轉帳給 **{creditor}** 👉 🏦 **${amount_to_pay:,.2f}** 元")
                elif creditor == selected_identity:
                    st.markdown(f"🎉 **【您將收款】** ➡️ **{debtor}** 將轉帳給你 👉 💰 **${amount_to_pay:,.2f}** 元")
                else:
                    st.markdown(f"🤝 **{debtor}** 應匯給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：國際金融管家（實時API多國匯率） ====================
with tabs[2]:
    st.header("🎒 全球匯率動態大盤")
    
    @st.cache_data(ttl=3600)
    def get_real_rates():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/TWD")
            return res.json()['rates']
        except:
            return {"USD": 0.031, "JPY": 4.65, "EUR": 0.029, "KRW": 41.5}

    rates = get_real_rates()
    
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    c_r1.metric("🇯🇵 日圓 (JPY)", f"{rates.get('JPY', 4.65):.2f}")
    c_r2.metric("🇺🇸 美金 (USD)", f"{rates.get('USD', 0.031):.4f}")
    c_r3.metric("🇪🇺 歐元 (EUR)", f"{rates.get('EUR', 0.029):.4f}")
    c_r4.metric("🇰🇷 韓圓 (KRW)", f"{rates.get('KRW', 41.5):.2f}")
    
    st.markdown("---")
    st.subheader("💱 智慧型多國匯率試算轉換")
    src_currency = st.selectbox("選擇您要在當地消費的外幣：", ["JPY 日圓", "USD 美金", "EUR 歐元", "KRW 韓圓"])
    foreign_amt = st.number_input("輸入外幣金額：", min_value=0.0, value=1000.0, key="lux_fx_in")
    
    cur_key = src_currency.split()[0]
    twd_result = foreign_amt / rates.get(cur_key, 1.0) if rates.get(cur_key) else 0.0
    st.success(f"⚜️ 精確折合新台幣約：**`${twd_result:,.2f}`** TWD 元")
