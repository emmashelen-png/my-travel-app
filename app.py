import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="隨身旅遊管家", layout="wide", initial_sidebar_state="expanded")

# --- 2. 側邊欄：介面風格設定 ---
st.sidebar.title("⚙️ 介面視覺設定")

theme_choice = st.sidebar.selectbox(
    "選擇專屬網頁配色：",
    ["🌓 智能感光 (隨系統自動日夜切換)", "✨ 經典純白 (極簡日間模式)", "🌙 深邃極黑 (高階夜間模式)", "💎 輕奢淺藍 (商務文青風)", "🌟 琥珀暖金 (現代典雅風)", "🌿 靜謐灰綠 (北歐極簡風)"]
)

theme_styles = {
    "✨ 經典純白 (極簡日間模式)": {"bg": "#F8FAFC", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#0F172A", "sidebar_text": "#334155", "accent": "#2563EB", "border": "#E2E8F0", "subtext": "#64748B", "is_dark": False},
    "🌙 深邃極黑 (高階夜間模式)": {"bg": "#0B0F19", "sidebar_bg": "#111827", "card": "#1E293B", "text": "#F8FAFC", "sidebar_text": "#F1F5F9", "accent": "#38BDF8", "border": "#334155", "subtext": "#94A3B8", "is_dark": True},
    "💎 輕奢淺藍 (商務文青風)": {"bg": "#F0F7F9", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#0F2D37", "sidebar_text": "#1E4D5A", "accent": "#0891B2", "border": "#CFE2E6", "subtext": "#4E737E", "is_dark": False},
    "🌟 琥珀暖金 (現代典雅風)": {"bg": "#FAF8F5", "sidebar_bg": "#F4EFE6", "card": "#FFFFFF", "text": "#362A1D", "sidebar_text": "#4A3925", "accent": "#D97706", "border": "#EFE6D5", "subtext": "#78624C", "is_dark": False},
    "🌿 靜謐灰綠 (北歐極簡風)": {"bg": "#F4F7F4", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#162E1A", "sidebar_text": "#2B4C30", "accent": "#16A34A", "border": "#D2E0D1", "subtext": "#5A735E", "is_dark": False}
}

# --- 3. 暴力權重 CSS 注入（精準打擊下拉選單展開時、已被選中項目的白色隱形字體） ---
if theme_choice == "🌓 智能感光 (隨系統自動日夜切換)":
    st.markdown("""
    <style>
        @media (prefers-color-scheme: light) {
            .stApp { background: #F8FAFC !important; color: #0F172A !important; }
            section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }
            h1, h2, h3, h4, h5, h6, p, label, span, div { color: #0F172A !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background: #0B0F19 !important; color: #F8FAFC !important; }
            section[data-testid="stSidebar"] { background-color: #111827 !important; }
            h1, h2, h3, h4, h5, h6, p, label, span, div { color: #F8FAFC !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"] { background: #1E293B !important; border: 1px solid #334155 !important; }
        }
    </style>
    """, unsafe_allow_html=True)
    cfg = theme_styles["✨ 經典純白 (極簡日間模式)"]
else:
    cfg = theme_styles[theme_choice]
    
    list_text_color = "#1E293B" if not cfg['is_dark'] else "#F8FAFC"
    list_bg_color = "#FFFFFF" if not cfg['is_dark'] else "#1E293B"
    
    st.markdown(f"""
    <style>
        /* 全域底色與文字強制顯色 */
        .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
        h1, h2, h3, h4, h5, h6, p, span, label {{ color: {cfg['text']} !important; }}
        
        /* 側邊欄外觀重編 */
        section[data-testid="stSidebar"] {{ background-color: {cfg['sidebar_bg']} !important; border-right: 1px solid {cfg['border']} !important; }}
        section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {{ color: {cfg['sidebar_text']} !important; }}
        
        /* 下拉選單（Selectbox）未點開收合狀態之文字與圖標 */
        div[data-baseweb="select"] div[role="button"],
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] p {{
            color: #1E293B !important; 
            font-weight: 600 !important;
        }}
        div[data-baseweb="select"] svg {{ fill: #334155 !important; }}

        /* 全域單行文字、多行文字、數字輸入框 */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input {{
            color: #1E293B !important;
            background-color: #FFFFFF !important;
            border: 1px solid {cfg['border']} !important;
            font-weight: 600 !important;
            -webkit-text-fill-color: #1E293B !important;
        }}
        
        div[data-testid="stTextInput"] button svg,
        div[data-testid="stNumberInput"] button svg {{
            fill: #334155 !important;
            color: #334155 !important;
        }}

        /* ==================== 🎯 核心擊殺：解決夜間模式下點開選單，當前選項字體隱形的問題 ==================== */
        ul[role="listbox"] {{ 
            background-color: #FFFFFF !important; /* 強制選單展開時，清單底色永遠是高對比的白色 */
            border: 1px solid {cfg['border']} !important; 
            border-radius: 12px !important; 
        }}
        
        /* 強制重寫清單內所有選項（包含已被滑鼠反白、未被滑鼠反白、已被系統預先選定項目）的文字顏色 */
        ul[role="listbox"] li,
        ul[role="listbox"] li *,
        ul[role="listbox"] li div,
        ul[role="listbox"] li span,
        ul[role="listbox"] li p,
        ul[role="listbox"] [data-active-item="true"],
        ul[role="listbox"] [aria-selected="true"] {{
            color: #0F172A !important; /* 強制字體一律呈現極高對比的深黑色，絕不允許變白或變灰 */
            font-weight: 600 !important;
        }}
        
        /* 當滑鼠真正懸停（Hover）在選項上時，套用主題色作為高光背景，此時字體轉為純白 */
        ul[role="listbox"] li:hover,
        ul[role="listbox"] li:hover * {{
            background-color: {cfg['accent']} !important;
            color: #FFFFFF !important; 
        }}
        
        /* 📊 數據指標與折疊卡片微動效 */
        div[data-testid="stMetric"], div[data-testid="stExpander"] {{
            background: {cfg['card']} !important;
            border: 1px solid {cfg['border']} !important;
            border-radius: 14px !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px) scale(1.01) !important;
        }}
        div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-weight: 800 !important; }}
        
        /* 🚀 按鈕動態回饋 */
        div.stButton > button {{
            border-radius: 10px !important;
            transition: all 0.2s ease-in-out !important;
        }}
        div.stButton > button:hover {{
            transform: scale(1.02) !important;
        }}
        div.stButton > button:active {{
            transform: scale(0.97) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. 旅程密碼驗證登入機制 ---
st.markdown("### 🔒 旅程安全驗證")
passcode_input = st.text_input("輸入您的專屬旅程密碼以載入資料：", type="password", placeholder="請填入旅程代碼（例如：KIX2026）")

# 側邊欄：建立新旅程
with st.sidebar.expander("➕ 建立全新旅遊行程", expanded=False):
    new_trip_name = st.text_input("旅程名稱", placeholder="例如：日本關西自由行")
    new_trip_sub = st.text_input("副標題說明", placeholder="例如：京都神設與專屬行程規劃")
    new_code = st.text_input("設定此行程的「專屬密碼」", placeholder="例如：JAPAN2026")
    num_members = st.number_input("參與成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"m_clean_{i}") for i in range(int(num_members))]
    
    if st.button("確認建立行程標籤", use_container_width=True):
        if new_trip_name and new_code:
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": f"【密碼：{new_code.strip()}】 {new_trip_sub}"}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success(f"行程建立成功！請在上方輸入密碼「{new_code}」即可解鎖進入！")

# 比對密碼
trips_res = supabase.table("trips").select("*").execute()
current_trip_id, current_trip = None, None

if trips_res.data:
    for t in trips_res.data:
        if t['subtitle'] and f"【密碼：{passcode_input.strip()}】" in t['subtitle'] and passcode_input.strip() != "":
            current_trip_id = t['id']
            current_trip = t
            break

if not current_trip_id:
    st.info("💡 請在上方欄位輸入正確的「旅程密碼」以同步資料；若需開啟新行程，請展開左側工具欄建立。")
    st.stop()

# 加載對應資料
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 身分選擇
st.sidebar.markdown("---")
selected_identity = st.sidebar.selectbox("👤 選擇您的成員身分：", ["僅進行瀏覽"] + list(members_dict.keys()))

# 主標題
st.title(f"🧭 {current_trip['name']}")
st.caption(f"📝 {current_trip['subtitle']}")

tabs = st.tabs(["📅 時間線行程規劃", "💰 團隊即時記帳本", "🎒 匯率換算工具"])

# ==================== 頁籤一：時間線行程規劃 ====================
with tabs[0]:
    st.subheader("🗺️ 每日日程規劃")
    
    with st.expander("➕ 增添新日程/交通節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1, key="p_day")
            time_slot = st.time_input("時間", key="p_time")
        with c2:
            act_type = st.selectbox("項目類別", ["📍 景點行程", "🚌 交通(主線)", "🔄 交通(轉乘提示)"], key="p_type")
            title = st.text_input("項目名稱", placeholder="例如：金閣寺參訪 / 購買御守", key="p_title")
        with c3:
            cost = st.number_input("預估花費 (TWD)", min_value=0.0, value=0.0, key="p_cost")
            note = st.text_area("詳細備註", placeholder="記錄轉乘月台、相關注意事項...", key="p_note")
            
        if st.button("確認寫入行程表", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 行程列表
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"#### 🗓️ 第 {day_num} 天 行程清單")
            for _, row in group.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: {cfg['card']}; border: 1px solid {cfg['border']}; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        ⏱️ <b>{row['time_slot'][:5]}</b> │ <b>[{row['activity_type']}] {row['title']}</b><br>
                        <small style="color: {cfg['subtext']};">說明：{row['note'] if row['note'] else '無'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2, _ = st.columns([1, 1, 8])
                    with b1:
                        with st.popover("✏️ 編輯"):
                            nt = st.text_input("更新項目名稱", value=row['title'], key=f"c_t_{row['id']}")
                            nn = st.text_area("更新備註說明", value=row['note'] if row['note'] else "", key=f"c_n_{row['id']}")
                            if st.button("確認修改", key=f"c_u_{row['id']}", type="primary"):
                                supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                                st.rerun()
                    with b2:
                        # 🛠️ 這裡精準修復了原本導致 SyntaxError 的引號截斷 Bug
                        with st.popover("🗑️ 移除"):
                            st.warning("確定要移除嗎？")
                            if st.button("確認移除", key=f"c_d_{row['id']}", type="primary", use_container_width=True):
                                supabase.table("itineraries").delete().eq("id", row['id']).execute()
                                st.rerun()

# ==================== 頁籤二：團隊即時記帳本 ====================
with tabs[1]:
    st.subheader("💰 即時開銷分帳本")
    
    with st.container():
        st.markdown("**📝 記錄新支出項目**")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費項目名稱", placeholder="例如：晚餐拉麵、交通通票")
            exp_amount = st.number_input("總金額 (TWD)", min_value=0.0, value=0.0, step=10.0, key="c_amt")
        with cx2:
            payer = st.selectbox("付款墊付人：", list(members_dict.keys()), key="c_payer")
            split_method = st.radio("分攤計算方式：", ["全員平均分攤", "自訂個別金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("🎯 **分帳平衡即時計算**")
            if split_method == "全員平均分攤":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.success(f"全員平均分攤，每人應付：${share:,.2f}")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"成員 {m} 負擔金額", min_value=0.0, value=0.0, key=f"c_sp_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.success("✅ 分配總額與總金額完全吻合。")
                    can_submit = True
                elif diff > 0:
                    st.warning(f" 還有 ${diff:,.2f} 元尚未分配...")
                    can_submit = False
                else:
                    st.error(f"⚠️ 超出總金額 ${abs(diff):,.2f} 元！")
                    can_submit = False
                    
        if st.button("💾 儲存此筆支出至雲端", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("記帳成功！")
            st.rerun()

    # 結算與明細
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        st.subheader("📊 花費統計與結算明細")
        
        my_paid, my_owe = 0.0, 0.0
        if selected_identity != "僅進行瀏覽":
            my_paid = df_exp[df_exp['paid_by'] == members_dict[selected_identity]]['amount'].sum()
            for _, r in df_exp.iterrows():
                my_owe += float(r['split_details'].get(selected_identity, 0.0))

        mi1, mi2, mi3 = st.columns(3)
        with mi1: st.metric("🎨 全團累積總開銷", f"${total_trip_cost:,.2f}")
        with mi2: 
            if selected_identity != "僅進行瀏覽": st.metric("💎 我的代墊金額", f"${my_paid:,.2f}")
        with mi3: 
            if selected_identity != "僅進行瀏覽": st.metric("📉 我的應付金額", f"${my_owe:,.2f}")

        fig = px.pie(df_exp, values='amount', names='description', hole=0.4, 
                     template="plotly_white" if "白" in theme_choice or "藍" in theme_choice or "金" in theme_choice or "綠" in theme_choice else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("💵 精簡債務清償方案")
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
            
            with st.container():
                if debtor == selected_identity:
                    st.markdown(f"🔴 **【您需還錢】** 請轉帳給 **{creditor}** 👉 🏦 **${amount_to_pay:,.2f}** 元")
                elif creditor == selected_identity:
                    st.markdown(f"🎉 **【您將收款】** **{debtor}** 將轉帳給你 👉 💰 **${amount_to_pay:,.2f}** 元")
                else:
                    st.markdown(f"🤝 **{debtor}** 應給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：匯率換算工具 ====================
with tabs[2]:
    st.subheader("🎒 國際即時匯率換算")
    
    if st.button("🔄 點擊刷新最新國際外匯數據", type="secondary", use_container_width=True):
        with st.spinner("正在連線國際金融資料庫，請稍候..."):
            st.cache_data.clear()
            st.success("匯率數據已即時刷新！")

    @st.cache_data(ttl=3600)
    def get_real_rates():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/TWD")
            return res.json()['rates']
        except:
            return {"USD": 0.031, "JPY": 4.65, "EUR": 0.029, "KRW": 41.5}

    rates = get_real_rates()
    
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    c_r1.metric("🇯🇵 日圓 (JPY) 基準", f"{rates.get('JPY', 4.65):.2f}")
    c_r2.metric("🇺🇸 美金 (USD) 基準", f"{rates.get('USD', 0.031):.4f}")
    c_r3.metric("🇪🇺 歐元 (EUR) 基準", f"{rates.get('EUR', 0.029):.4f}")
    c_r4.metric("🇰🇷 韓圓 (KRW) 基準", f"{rates.get('KRW', 41.5):.2f}")
    
    st.markdown("---")
    st.markdown("**💱 跨國金額即時試算**")
    src_currency = st.selectbox("選擇外幣種類：", ["JPY 日圓", "USD 美金", "EUR 歐元", "KRW 韓圓"])
    foreign_amt = st.number_input("輸入外幣消費金額：", min_value=0.0, value=1000.0, key="c_fx_in")
    
    cur_key = src_currency.split()[0]
    twd_result = foreign_amt / rates.get(cur_key, 1.0) if rates.get(cur_key) else 0.0
    st.success(f"💰 折合新台幣約：**`${twd_result:,.2f}`** TWD 元")
