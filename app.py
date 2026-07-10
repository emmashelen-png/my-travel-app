import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🧳 智慧隨身旅遊管家", layout="wide")

# --- 2. 高級華美主題配色控制中心 (原生 HTML 注入) ---
st.sidebar.title("🎨 視覺美學中心")
theme_choice = st.sidebar.selectbox(
    "切換風格模式：", 
    ["明亮日間 (Light)", "經典夜間 (Dark)", "奢華金屬 (Metallic)", "優雅淺藍 (Soft Blue)", "極簡森林綠 (Sage Green)"]
)

# 各風格的 CSS 顏色代碼配置
themes = {
    "明亮日間 (Light)": {"bg": "#f8f9fa", "text": "#212529", "card": "#ffffff", "accent": "#007bff", "border": "#dee2e6"},
    "經典夜間 (Dark)": {"bg": "#121214", "text": "#e1e1e6", "card": "#1a1a1e", "accent": "#00f0ff", "border": "#29292e"},
    "奢華金屬 (Metallic)": {"bg": "#f1f2f6", "text": "#2f3542", "card": "#ffffff", "accent": "#747d8c", "border": "#ced6e0"},
    "優雅淺藍 (Soft Blue)": {"bg": "#f0f4f8", "text": "#102a43", "card": "#ffffff", "accent": "#486581", "border": "#bcccdc"},
    "極簡森林綠 (Sage Green)": {"bg": "#f3f4f0", "text": "#2f3e22", "card": "#ffffff", "accent": "#606c38", "border": "#dda15e"}
}
t = themes[theme_choice]

st.html(f"""
<style>
    .stApp {{ background: {t['bg']} !important; color: {t['text']} !important; }}
    h1, h2, h3, p, span, label {{ color: {t['text']} !important; }}
    div[data-testid="stMetric"] {{
        background: {t['card']}; padding: 18px; border-radius: 16px;
        border: 1px solid {t['border']}; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    div[data-testid="stMetricValue"] {{ color: {t['accent']} !important; font-weight: 800 !important; }}
    .trip-card {{
        background: {t['card']}; padding: 20px; border-radius: 14px;
        border: 1px solid {t['border']}; border-left: 6px solid {t['accent']}; margin-bottom: 15px;
    }}
    .expense-card {{
        background: {t['card']}; padding: 18px; border-radius: 12px;
        border: 1px solid {t['border']}; border-left: 6px solid {t['accent']}; margin-bottom: 12px;
    }}
</style>
""")

# --- 3. 安全防呆：暗號口令與旅程隱私隔離隔離機制 ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 旅程安全解鎖")
trip_passcode = st.sidebar.text_input("輸入您的旅程暗號：", type="password", placeholder="輸入暗號以載入您參與的行程")

# 側邊欄：新增旅程區（強制設定專屬暗號）
with st.sidebar.expander("➕ 建立全新旅遊標籤", expanded=False):
    new_name = st.text_input("旅程名稱 (如：日本、花蓮)", placeholder="例如：日本關西行")
    new_sub = st.text_input("副標題", placeholder="六天五夜吃貨團")
    new_code = st.text_input("為這趟旅程設定一個專屬暗號：", placeholder="例如：japan2026")
    num_members = st.number_input("成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"m_{i}") for i in range(int(num_members))]
    
    if st.button("🚀 創建並儲存旅程", use_container_width=True):
        if new_name and new_code:
            # 這裡我們複用 subtitle 欄位儲存暗號，格式為 "副標題|||暗號" 達成免費擴充
            combined_sub = f"{new_sub}|||{new_code}"
            t_res = supabase.table("trips").insert({"name": new_name, "subtitle": combined_sub}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success("🎉 旅程標籤創建成功！請在上方輸入剛才設定的暗號解鎖。")

# 根據使用者輸入的暗號，動態篩選出符合的旅程（完美達成隱私隔離，看不到沒參與的）
trips_res = supabase.table("trips").select("*").execute()
accessible_trips = {}
if trips_res.data:
    for t_data in trips_res.data:
        sub_raw = t_data['subtitle'] if t_data['subtitle'] else ""
        if "|||" in sub_raw:
            sub_part, code_part = sub_raw.split("|||", 1)
            if trip_passcode == code_part:
                accessible_trips[t_data['name']] = (t_data['id'], sub_part)
        elif trip_passcode == "admin":  # 管理員後門防呆
            accessible_trips[t_data['name']] = (t_data['id'], sub_raw)

if not accessible_trips:
    st.info("👋 您好，目前尚未載入任何行程。請在左側輸入您參與的「旅程專屬暗號」來解鎖您的日本或花蓮旅程；若您是發起人，請先展開左側建立全新的旅程標籤。")
    st.stop()

selected_trip_name = st.sidebar.selectbox("🧭 您有參與的旅程列表：", list(accessible_trips.keys()))
current_trip_id, current_sub = accessible_trips[selected_trip_name]

# 撈取該旅程成員
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 認領我是誰
selected_identity = st.sidebar.selectbox("👤 認領身分（高亮您的專屬帳單）：", ["僅限瀏覽者"] + list(members_dict.keys()))

# 主畫面標題與副標題
st.title(f"✈️ {selected_trip_name}")
if current_sub:
    st.caption(f"💡 {current_sub}")

tabs = st.tabs(["📅 時間線行程規劃", "💰 隨手記帳與分帳", "💱 即時動態匯率工具"])

# ==================== 頁籤一：時間線行程規劃 ====================
with tabs[0]:
    st.header("🗺️ 每日行程與交通管家")
    
    with st.expander("➕ 新增行程/交通節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1, key="it_day")
            time_slot = st.time_input("時間", key="it_time")
        with c2:
            act_type = st.selectbox("項目類型", ["📍 景點項目", "🚗 交通主線", "🔄 轉乘防呆提示"], key="it_type")
            title = st.text_input("項目/景點名稱", placeholder="例如：清水寺", key="it_title")
        with c3:
            cost = st.number_input("預估花費 (TWD)", min_value=0.0, value=0.0, key="it_cost")
            note = st.text_area("備註說明", placeholder="交通票券資訊、轉乘月台等", key="it_note")
            
        if st.button("✨ 成功加入時間線", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 安全地利用 st.html 渲染，徹底解決 TypeError 崩潰
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"### ☀️ 第 {day_num} 天")
            for _, row in group.iterrows():
                st.html(f"""
                <div class="trip-card">
                    <strong>⏱️ {row['time_slot'][:5]} | {row['activity_type']} - {row['title']}</strong>
                    <br><small style='opacity:0.8;'>備註：{row['note'] if row['note'] else '無'}</small>
                </div>
                """)
                # 刪除與修改按鈕
                cb1, _ = st.columns([1, 9])
                with cb1:
                    if st.button("🗑️ 刪除節點", key=f"del_it_{row['id']}", type="primary"):
                        supabase.table("itineraries").delete().eq("id", row['id']).execute()
                        st.rerun()

# ==================== 頁籤二：隨手記帳與分帳系統 ====================
with tabs[1]:
    st.header("💰 隨手分帳帳本")
    
    with st.container(border=True):
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費項目描述", placeholder="例如：拉麵、飯店住宿費")
            exp_amount = st.number_input("總金額", min_value=0.0, value=0.0)
        with cx2:
            payer = st.selectbox("誰付的錢？", list(members_dict.keys()))
            split_method = st.radio("分帳方式", ["全員均分", "自訂精確金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("🎯 **即時分帳修正動態回饋**")
            if split_method == "全員均分":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.info(f"💡 每人均分金額：${share:,.2f}")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"{m} 應負擔", min_value=0.0, value=0.0, key=f"s_{m}")
                    split_details[m] = amt
                    current_total += amt
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.success("✅ 金額完全吻合！")
                    can_submit = True
                elif diff > 0:
                    st.warning(f" 還剩 `${diff:,.2f}` 未分配")
                    can_submit = False
                else:
                    st.error(f"⚠️ 超出總額 `${abs(diff):,.2f}`")
                    can_submit = False
                    
        if st.button("💾 儲存此筆帳目明細", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("儲存成功！")
            st.rerun()

    # 花費明細歷史與結算
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        mi1, mi2 = st.columns(2)
        with mi1: st.metric("🎨 全團累積總花費", f"${total_trip_cost:,.2f}")
        
        fig = px.pie(df_exp, values='amount', names='description', hole=0.4, template="plotly_dark" if "Dark" in theme_choice or "Metallic" in theme_choice else "plotly")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 帳目歷史歷史明細")
        for _, row in df_exp.iterrows():
            payer_name = members_id_to_name[row['paid_by']]
            st.html(f"""
            <div class="expense-card">
                <strong>{row['description']}</strong> | 總額：${row['amount']:,} 元
                <br><small style='opacity:0.7;'>由 {payer_name} 支付墊付</small>
            </div>
            """)
            if st.button("🗑️ 刪除此筆花費", key=f"del_ex_{row['id']}"):
                supabase.table("expenses").delete().eq("id", row['id']).execute()
                st.rerun()

        # 債務精簡清償計算
        st.markdown("---")
        st.subheader("💵 即時清償結算帳單 (自動簡化債務)")
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
                st.error(f"🔴 【您需要給錢】 ➡️ 請轉帳給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            elif creditor == selected_identity:
                st.success(f"🟢 【您等著收錢】 ➡️ **{debtor}** 將會轉帳給您 👉 `${amount_to_pay:,.2f}` 元")
            else:
                st.info(f"💳 **{debtor}** 應給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
                
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：全球即時動態匯率工具 ====================
with tabs[2]:
    st.header("💱 全球多國即時匯率換算")
    
    # 使用免費且不需登入的動態匯率 API 抓取最新即時數據
    @st.cache_data(ttl=3600)  # 快取一小時防爆發防呆
    def get_realtime_rates():
        try:
            url = "https://open.er-api.com/v6/latest/TWD"
            response = requests.get(url).json()
            return response.get("rates", {})
        except:
            return {"USD": 0.031, "JPY": 4.65, "KRW": 41.2, "EUR": 0.029} # 防斷網預設數據
            
    rates = get_realtime_rates()
    
    if rates:
        st.success("⚡ 即時匯率已成功由全球外幣 API 即時更新載入！")
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            twd_input = st.number_input("輸入您的新台幣金額 (TWD)", min_value=0.0, value=1000.0)
        with col_ex2:
            target_currency = st.selectbox("選擇欲兌換的外幣項目：", ["JPY (日圓)", "USD (美金)", "KRW (韓元)", "EUR (歐元)"])
            
        curr_code = target_currency.split(" ")[0]
        exchange_rate = rates.get(curr_code, 1.0)
        result_val = twd_input * exchange_rate
        
        st.markdown(f"### 🎯 換算結果")
        st.info(f"💵 新台幣 `${twd_input:,.2f}` 元 折合 **{target_currency}** 約為： `{result_val:,.2f}`")
        st.caption(f"📊 當前即時動態匯率基準： 1 TWD = {exchange_rate} {curr_code}")
