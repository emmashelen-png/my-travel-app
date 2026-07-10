import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 頁面基本配置
st.set_page_config(page_title="🧳 隨身旅遊智慧管家", layout="wide", initial_sidebar_state="expanded")

# --- 2. 華美多主題切換與自訂色系流 (Light Mode 核心) ---
st.sidebar.title("🎨 奢華視覺風格設定")
theme_choice = st.sidebar.selectbox("切換風格主題", ["✨ 經典優雅白", "🌙 經典夜間黑", "🌸 浪漫櫻花粉", "🌊 輕奢蒂芙尼藍", "🌲 靜謐莫蘭迪綠"])

# 根據主題動態注入不同的頂級網頁外觀
theme_styles = {
    "✨ 經典優雅白": {"bg": "linear-gradient(135deg, #f6f8fb 0%, #e9eff5 100%)", "card": "rgba(255, 255, 255, 0.8)", "text": "#2d3748", "primary": "#3182ce", "border": "rgba(0,0,0,0.05)", "metric": "#1a365d"},
    "🌙 經典夜間黑": {"bg": "linear-gradient(135deg, #121214 0%, #1a1a1e 100%)", "card": "rgba(255, 255, 255, 0.04)", "text": "#f4f4f5", "primary": "#00f0ff", "border": "rgba(255,255,255,0.08)", "metric": "#00f0ff"},
    "🌸 浪漫櫻花粉": {"bg": "linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%)", "card": "rgba(255, 255, 255, 0.85)", "text": "#4a5568", "primary": "#e53e3e", "border": "rgba(229,62,62,0.1)", "metric": "#9b2c2c"},
    "🌊 輕奢蒂芙尼藍": {"bg": "linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%)", "card": "rgba(255, 255, 255, 0.85)", "text": "#2c5282", "primary": "#319795", "border": "rgba(49,151,149,0.1)", "metric": "#234e52"},
    "🌲 靜謐莫蘭迪綠": {"bg": "linear-gradient(135deg, #f0f4f1 0%, #d2decb 100%)", "card": "rgba(255, 255, 255, 0.85)", "text": "#2f3e2e", "primary": "#4a6b48", "border": "rgba(74,107,72,0.1)", "metric": "#1c2d1b"}
}
t = theme_styles[theme_choice]

st.html(f"""
<style>
    .stApp {{ background: {t['bg']} !important; color: {t['text']} !important; }}
    h1, h2, h3, p, span, label {{ color: {t['text']} !important; }}
    div[data-testid="stMetric"] {{
        background: {t['card']} !important; padding: 18px; border-radius: 16px;
        border: 1px solid {t['border']}; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}
    div[data-testid="stMetricValue"] {{ color: {t['metric']} !important; font-weight: 800 !important; }}
    .trip-card {{
        background: {t['card']} !important; padding: 20px; border-radius: 14px;
        border: 1px solid {t['border']}; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }}
    .expense-card {{
        background: {t['card']} !important; padding: 18px; border-radius: 12px;
        border-left: 6px solid {t['primary']}; border-top: 1px solid {t['border']};
        border-right: 1px solid {t['border']}; border-bottom: 1px solid {t['border']}; margin-bottom: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{ color: {t['text']}; font-weight: 600; padding: 12px 24px; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {t['primary']} !important; border-bottom-color: {t['primary']} !important; }}
</style>
""")

# --- 3. 核心安全防呆：使用者認領與旅程隱私隔離隔離機制 ---
st.sidebar.markdown("---")
st.sidebar.subheader("👤 使用者身分認領")

# 優先撈取全資料庫所有的不重複成員暱稱，供初次進入者選擇認領
all_members_raw = supabase.table("members").select("name").execute()
unique_member_names = sorted(list(set([m['name'] for m in all_members_raw.data]))) if all_members_raw.data else []

my_name = st.sidebar.selectbox("確認你是哪位成員？（認領後隔離無關旅遊標籤）", ["尚未認領"] + unique_member_names)

if my_name == "尚未認領":
    st.info("👋 歡迎使用！請先在左側邊欄「認領你是誰」，系統將會為您即時解鎖您有參與的旅遊行程標籤。")
    
    # 允許未認領時創建新旅遊（首創者防呆）
    with st.expander("➕ 點此創建一個全新旅遊團隊項目"):
        new_trip_name = st.text_input("全新旅遊名稱", placeholder="例如：2026日本慶生團")
        new_trip_sub = st.text_input("副標題說明", placeholder="例如：吃貨五天四夜之旅")
        num_members = st.number_input("成員總人數", min_value=1, max_value=10, value=2)
        member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"init_m_{i}") for i in range(int(num_members))]
        if st.button("🚀 建立全新旅遊標籤", use_container_width=True):
            if new_trip_name:
                t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": new_trip_sub}).execute()
                t_id = t_res.data[0]['id']
                for m_name in member_names:
                    if m_name.strip():
                        supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
                st.success("🎉 旅程創建成功！請在上方選擇您的暱稱認領進入。")
                st.rerun()
    st.stop()

# --- 🔓 隱私安全隔離核心：只撈取「我」有參與的旅程 ---
my_trips_res = supabase.table("members").select("trip_id").eq("name", my_name).execute()
my_trip_ids = [m['trip_id'] for m in my_trips_res.data] if my_trips_res.data else []

if not my_trip_ids:
    st.warning(f"🔍 找不到與成員「{my_name}」相關的旅程項目。")
    st.stop()

# 根據過濾出來的 ID 去拿 Trip 的真實名字（排除完全沒參與的旅遊，如花蓮行）
trips_res = supabase.table("trips").select("*").in_("id", my_trip_ids).order("created_at").execute()
trip_options = {t['name']: t['id'] for t in trips_res.data} if trips_res.data else {}

st.sidebar.markdown("---")
selected_trip_name = st.sidebar.selectbox("🧭 選擇您參與的旅遊標籤：", list(trip_options.keys()))
current_trip_id = trip_options[selected_trip_name]

# 獲取該團成員與詳細細節
current_trip = supabase.table("trips").select("*").eq("id", current_trip_id).single().execute().data
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 管理旅程面板
with st.sidebar.expander("⚙️ 管理此旅遊標籤", expanded=False):
    edit_name = st.text_input("修改名稱", value=current_trip['name'])
    edit_sub = st.text_input("修改副標題", value=current_trip['subtitle'] if current_trip['subtitle'] else "")
    if st.button("💾 儲存修改項目"):
        supabase.table("trips").update({"name": edit_name, "subtitle": edit_sub}).eq("id", current_trip_id).execute()
        st.rerun()
    if st.button("🗑️ 刪除此旅遊標籤與所有花費", type="primary"):
        supabase.table("trips").delete().eq("id", current_trip_id).execute()
        st.rerun()

# --- 主畫面渲染 ---
st.title(f"✈️ {current_trip['name']}")
if current_trip['subtitle']:
    st.caption(f"💡 {current_trip['subtitle']}")

tabs = st.tabs(["📅 全團共享時間線", "💰 智慧即時分帳本", "🎒 動態多國匯率工具"])

# ==================== 頁籤一：全團共享時間線 ====================
with tabs[0]:
    st.header("🗺️ 景點與交通動態規劃")
    with st.expander("➕ 新增行程與轉乘防呆節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1)
            time_slot = st.time_input("預定時間")
        with c2:
            act_type = st.selectbox("項目類別", ["📍 景點項目", "🚗 交通主線", "🔄 轉乘防呆提示"])
            title = st.text_input("景點/樞紐名稱", placeholder="例如：清水寺、HARUKA 特快")
        with c3:
            cost = st.number_input("花費預算 (TWD)", min_value=0.0, value=0.0)
            note = st.text_area("詳細備註", placeholder="車次、轉乘月台、優惠代碼...")
            
        if st.button("✨ 成功加入共享行程", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 顯示精美時間線卡片 (100% 採用原生 st.html 阻斷 TypeError)
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"### ☀️ 第 {day_num} 天 行程安排")
            for _, row in group.iterrows():
                is_trans = "交通" in row['activity_type'] or "轉乘" in row['activity_type']
                border_color = t['primary'] if not is_trans else "#bb86fc"
                
                st.html(f"""
                <div class="trip-card" style="border-left: 6px solid {border_color};">
                    <span style='color:{t['primary']}; font-weight:bold; font-size:1.1rem;'>⏱️ {row['time_slot'][:5]}</span> | 
                    <span style='font-weight:700; font-size:1.1rem;'>{row['activity_type']} - {row['title']}</span>
                    <br><span style='color:#718096; font-size:0.95rem;'>📝 備註：{row['note'] if row['note'] else '無'}</span>
                </div>
                """)
                
                cb1, cb2, _ = st.columns([1, 1, 8])
                with cb1:
                    with st.popover("✏️ 修改項目"):
                        nt = st.text_input("修改名稱", value=row['title'], key=f"e_it_t_{row['id']}")
                        nn = st.text_area("修改備註", value=row['note'] if row['note'] else "", key=f"e_it_n_{row['id']}")
                        if st.button("確認更新", key=f"u_it_{row['id']}"):
                            supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                            st.rerun()
                with cb2:
                    if st.button("🗑️ 刪除", key=f"d_it_{row['id']}", type="primary"):
                        supabase.table("itineraries").delete().eq("id", row['id']).execute()
                        st.rerun()

# ==================== 頁籤二：智慧即時分帳本 ====================
with tabs[1]:
    st.header("💰 團員費用分攤帳本")
    
    with st.container(border=True):
        st.subheader("📝 記錄一筆共同消費")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("品項/消費說明", placeholder="例如：藥妝代購、全體飯店費")
            exp_amount = st.number_input("消費總金額", min_value=0.0, value=0.0, step=10.0)
        with cx2:
            payer = st.selectbox("是誰先墊付的錢？", list(members_dict.keys()))
            split_method = st.radio("拆帳方式", ["全體均分", "自訂精確金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("🎯 **即時動態拆帳校正計算**")
            if split_method == "全體均分":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.html(f"<div style='color:{t['primary']}; font-weight:600;'>💡 每人平均負擔：${share:,.2f} 元</div>")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"💸 {m} 應付金額", min_value=0.0, value=0.0, key=f"js_v2_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.html("<div style='color:#48bb78; font-weight:600;'>✅ 總額完美符合！解鎖儲存。</div>")
                    can_submit = True
                elif diff > 0:
                    st.html(f"<div style='color:#dd6b20;'>⚠️ 還剩 <strong>${diff:,.2f}</strong> 元未分配！</div>")
                    can_submit = False
                else:
                    st.html(f"<div style='color:#e53e3e;'>⚠️ 超出總金額 <strong>${abs(diff):,.2f}</strong> 元！</div>")
                    can_submit = False
                    
        if st.button("💾 儲存此筆帳目到雲端", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("記帳成功！")
            st.rerun()

    # 花費明細歷史與統計
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        # 個人精準指標卡
        my_paid = df_exp[df_exp['paid_by'] == members_dict[my_name]]['amount'].sum()
        my_owe = sum([float(r['split_details'].get(my_name, 0.0)) for _, r in df_exp.iterrows()])
        
        mi1, mi2, mi3 = st.columns(3)
        with mi1: st.metric("🎨 團隊累積總花費", f"${total_trip_cost:,.2f}")
        with mi2: st.metric(f"💳 這是你 ({my_name}) 總共代墊的錢", f"${my_paid:,.2f}")
        with mi3: st.metric(f"📉 這是你 ({my_name}) 實際應負擔總額", f"${my_owe:,.2f}")
        
        fig = px.pie(df_exp, values='amount', names='description', hole=0.45,
                     template="plotly_white" if "白" in theme_choice or "粉" in theme_choice or "綠" in theme_choice or "藍" in theme_choice else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # 歷史卡片明細
        st.subheader("📋 共享明細維護")
        for _, row in df_exp.iterrows():
            payer_name = members_id_to_name[row['paid_by']]
            is_me_paid = (payer_name == my_name)
            border_style = f"border-left: 6px solid {t['primary']};" if is_me_paid else "border-left: 6px solid #cbd5e0;"
            
            st.html(f"""
            <div class="expense-card" style="{border_style}">
                <strong>項目：{row['description']}</strong> | 消費總金額：<span style='color:{t['primary']}; font-weight:700;'>${row['amount']:,} 元</span>
                <br><small style='color:#718096;'>由 【{payer_name}】 先行代墊付清</small>
            </div>
            """)
            
            mx1, mx2, _ = st.columns([1, 1, 8])
            with mx1:
                with st.popover("✏️ 修改項目描述"):
                    nd = st.text_input("修改消費品項描述", value=row['description'], key=f"e_ex_d_{row['id']}")
                    if st.button("儲存描述", key=f"u_ex_{row['id']}"):
                        supabase.table("expenses").update({"description": nd}).eq("id", row['id']).execute()
                        st.rerun()
            with mx2:
                if st.button("🗑️ 刪除帳單", key=f"d_ex_{row['id']}", type="primary"):
                    supabase.table("expenses").delete().eq("id", row['id']).execute()
                    st.rerun()

        # 債務精簡演算法結算
        st.markdown("---")
        st.subheader("💵 即時清償互不相欠帳單")
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
            
            if debtor == my_name:
                st.error(f"🔴 【你需要給錢】 ➡️ 請轉帳給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            elif creditor == my_name:
                st.success(f"🟢 【等著收錢】 ➡️ **{debtor}** 應該轉帳給你 👉 `${amount_to_pay:,.2f}` 元")
            else:
                st.info(f"💳 **{debtor}** 應給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
                
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：動態多國匯率工具 ====================
with tabs[2]:
    st.header("💱 全球即時匯率換算中心")
    
    # 動態抓取即時匯率 (防呆快取機制)
    @st.cache_data(ttl=3600)  # 每一小時自動更新一次最新國際牌價
    def get_live_rates():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/TWD").json()
            return res.get("rates", {})
        except:
            return {"JPY": 4.65, "USD": 0.031, "KRW": 42.5, "THB": 1.08} # 斷網時的防呆底線
            
    rates = get_live_rates()
    
    st.html(f"<p>ℹ️ <em>系統已自動為您同步連線全球即時外幣牌價。</em></p>")
    
    twd_input = st.number_input("💰 請輸入出遊預算新台幣 (TWD)", min_value=0.0, value=1000.0, step=100.0)
    
    col_cur1, col_cur2, col_cur3, col_cur4 = st.columns(4)
    with col_cur1:
        st.metric("🇯🇵 折合日圓 (JPY)", f"¥{(twd_input * rates.get('JPY', 4.65)):,.2f}", help="即時日幣匯率")
    with col_cur2:
        st.metric("🇺🇸 折合美金 (USD)", f"${(twd_input * rates.get('USD', 0.031)):,.2f}", help="即時美金匯率")
    with col_cur3:
        st.metric("🇰🇷 折合韓元 (KRW)", f"₩{(twd_input * rates.get('KRW', 42.5)):,.2f}", help="即時韓檢匯率")
    with col_cur4:
        st.metric("🇹🇭 折合泰銖 (THB)", f"฿{(twd_input * rates.get('THB', 1.08)):,.2f}", help="即時泰國銖匯率")
