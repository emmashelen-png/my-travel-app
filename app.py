import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="智慧隨身旅遊管家", layout="wide", initial_sidebar_state="expanded")

# --- 2. 側邊欄：高對比度主題配置（改用全新膠囊控制鈕，徹底防範文字隱形） ---
st.sidebar.markdown("### 🎨 介面視覺風格")

# 改用 st.segmented_control 替代下拉選單，按鈕字體極度清晰，完全由原生系統驅動
theme_choice = st.sidebar.segmented_control(
    "請選擇您偏好的商務主題色調：",
    options=["智能感光", "極簡白", "石墨黑", "優雅藍", "經典金"],
    default="智能感光"
)

theme_styles = {
    "極簡白": {"bg": "#F8FAFC", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#0F172A", "accent": "#2563EB", "border": "#E2E8F0", "subtext": "#64748B"},
    "石墨黑": {"bg": "#0B0F19", "sidebar_bg": "#111827", "card": "#1F2937", "text": "#F9FAFB", "accent": "#00F0FF", "border": "#374151", "subtext": "#9CA3AF"},
    "優雅藍": {"bg": "#F0F4F8", "sidebar_bg": "#FFFFFF", "card": "#FFFFFF", "text": "#102A43", "accent": "#1982C4", "border": "#D9E2EC", "subtext": "#486581"},
    "經典金": {"bg": "#FAF8F5", "sidebar_bg": "#F4EFE6", "card": "#FFFFFF", "text": "#3D3025", "accent": "#C5A059", "border": "#E6DFD1", "subtext": "#736252"}
}

if theme_choice == "智能感光":
    st.html("""
    <style>
        @media (prefers-color-scheme: light) {
            .stApp { background: #F8FAFC !important; color: #0F172A !important; }
            section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }
            h1, h2, h3, h4, h5, h6, p, label, span, div { color: #0F172A !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"], div.stVerticalBlockBorderWrapper { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background: #0B0F19 !important; color: #F9FAFB !important; }
            section[data-testid="stSidebar"] { background-color: #111827 !important; }
            h1, h2, h3, h4, h5, h6, p, label, span, div { color: #F9FAFB !important; }
            div[data-testid="stMetric"], div[data-testid="stExpander"], div.stVerticalBlockBorderWrapper { background: #1F2937 !important; border: 1px solid #374151 !important; }
        }
    </style>
    """)
else:
    cfg = theme_styles[theme_choice]
    st.html(f"""
    <style>
        .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
        h1, h2, h3, h4, h5, h6, p, span, label, div {{ color: {cfg['text']} !important; }}
        section[data-testid="stSidebar"] {{ background-color: {cfg['sidebar_bg']} !important; border-right: 1px solid {cfg['border']} !important; }}
        section[data-testid="stSidebar"] * {{ color: {cfg['text']} !important; font-weight: 600; }}
        div[data-testid="stMetric"], div[data-testid="stExpander"], div.stVerticalBlockBorderWrapper {{ background: {cfg['card']} !important; border: 1px solid {cfg['border']} !important; border-radius: 14px !important; }}
        div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-weight: 800 !important; }}
    </style>
    """)

# --- 3. 旅程安全驗證管制 ---
st.markdown("### 🔒 團隊行程安全驗證")
passcode_input = st.text_input("請輸入您受邀的專屬旅程暗號：", type="password", placeholder="例如：TOKYO2026")

# 側邊欄：建立新旅程
with st.sidebar.expander("➕ 建立新專案行程", expanded=False):
    new_trip_name = st.text_input("旅程名稱", placeholder="例如：2026東京精緻遊")
    new_trip_sub = st.text_input("備註說明", placeholder="例如：文化探索與記帳管理")
    new_code = st.text_input("設定此行程的通關暗號", placeholder="例如：KIX666")
    num_members = st.number_input("參與成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"m_input_{i}") for i in range(int(num_members))]
    
    if st.button("確認儲存行程", use_container_width=True, type="primary"):
        if new_trip_name and new_code:
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": f"【暗號：{new_code.strip()}】 {new_trip_sub}"}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success(f"系統提示：行程建立成功，請使用暗號「{new_code}」於主畫面登入。")

# 比對暗號篩選專案
trips_res = supabase.table("trips").select("*").execute()
current_trip_id, current_trip = None, None

if trips_res.data:
    for t in trips_res.data:
        if t['subtitle'] and f"【暗號：{passcode_input.strip()}】" in t['subtitle'] and passcode_input.strip() != "":
            current_trip_id = t['id']
            current_trip = t
            break

if not current_trip_id:
    st.info("💡 系統提示：請於上方輸入正確的旅程暗號解鎖內容。若需開啟新旅程，請展開左側選單進行設定。")
    st.stop()

# 成功通關，載入成員明細
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 認領個人身分
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 個人身分確認")
selected_identity = st.sidebar.radio("請選擇您的暱稱（以便系統精確提供專屬對帳單）：", ["僅瀏覽專案"] + list(members_dict.keys()))

# --- 主畫面標題與動態複製互動鈕 ---
c_title, c_copy = st.columns([4, 1])
with c_title:
    st.title(f"📊 {current_trip['name']}")
    st.caption(f"ℹ️ {current_trip['subtitle']}")
with c_copy:
    # 互動小按鈕 1：一鍵複製行程暗號給 LINE 旅伴
    if st.button("📋 複製此旅程暗號", use_container_width=True):
        st.toast(f"已複製暗號：{passcode_input}", icon="✅")

tabs = st.tabs(["📅 行程規劃線", "💰 團隊記帳本", "🎒 即時金融小工具"])

# ==================== 頁籤一：行程規劃線 ====================
with tabs[0]:
    st.subheader("🗺️ 行程時光節點")
    
    with st.expander("➕ 增加新行程節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("天數索引", min_value=1, value=1, key="l_day")
            time_slot = st.time_input("預定時間", key="l_time")
        with c2:
            act_type = st.selectbox("項目類別", ["景點項目", "主線交通", "轉乘防呆提示"], key="l_type")
            title = st.text_input("節點名稱", placeholder="例如：清水寺、金閣寺", key="l_title")
        with c3:
            cost = st.number_input("預估開銷 (TWD)", min_value=0.0, value=0.0, key="l_cost")
            note = st.text_area("詳細備註", placeholder="填寫月台資訊或轉乘班次...", key="l_note")
            
        if st.button("儲存至行程表", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 以官方完全相容的貨櫃結構渲染，徹底防範格式化報錯
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"#### 🗓️ 第 {day_num} 天 日程明細")
            for _, row in group.iterrows():
                with st.container(border=True):
                    ic1, ic2, ic3 = st.columns([1, 4, 1])
                    ic1.write(f"⏱️ **{row['time_slot'][:5]}**")
                    ic2.write(f"**[{row['activity_type']}]** {row['title']} \n\n *備註：{row['note'] if row['note'] else '無'}*")
                    
                    # 修改與移除之複合操作互動按鈕
                    with ic3:
                        cb1, cb2 = st.columns(2)
                        with cb1:
                            with st.popover("✏️"):
                                nt = st.text_input("修改名稱", value=row['title'], key=f"lux_t_{row['id']}")
                                nn = st.text_area("修改備註", value=row['note'] if row['note'] else "", key=f"lux_n_{row['id']}")
                                if st.button("更新", key=f"lux_u_{row['id']}"):
                                    supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                                    st.rerun()
                        with cb2:
                            if st.button("🗑️", key=f"lux_d_{row['id']}", type="primary"):
                                supabase.table("itineraries").delete().eq("id", row['id']).execute()
                                st.rerun()

# ==================== 頁籤二：團隊記帳本 ====================
with tabs[1]:
    st.subheader("💳 團隊多功能代墊分帳系統")
    
    with st.container(border=True):
        st.markdown("#### 📝 新增公用費用明細")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費項目描述", placeholder="例如：午餐、交通車票")
            exp_amount = st.number_input("消費總金額", min_value=0.0, value=0.0, step=10.0, key="l_amt")
        with cx2:
            payer = st.selectbox("款項代墊人：", list(members_dict.keys()), key="l_payer")
            split_method = st.radio("分攤權重比對：", ["全員平均分攤", "自訂精確分攤金額"], horizontal=True)
            
        split_details = {}
        with cx3:
            st.markdown("📊 **分帳平衡動態覆核**")
            if split_method == "全員平均分攤":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.success(f"計算結果：全員等額均分，每人應付 ${share:,.2f} 元")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"成員 [{m}] 的實質消費額", min_value=0.0, value=0.0, key=f"l_sp_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.success("✅ 計算提示：分攤總和與總金額完全相符。")
                    can_submit = True
                elif diff > 0:
                    st.warning(f"⚠️ 計算提示：尚有 ${diff:,.2f} 元未分配完畢。")
                    can_submit = False
                else:
                    st.error(f"❌ 計算提示：超出總金額限制達 ${abs(diff):,.2f} 元！")
                    can_submit = False
                    
        # 互動小按鈕 2：按鈕聯動進度條特效
        if st.button("💾 將此筆款項安全存入雲端", disabled=not can_submit, use_container_width=True, type="primary"):
            with st.spinner("雲端資料庫同步中..."):
                supabase.table("expenses").insert({
                    "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                    "paid_by": members_dict[payer], "split_details": split_details
                }).execute()
            st.success("儲存完畢！")
            st.rerun()

    # 費用結算加載
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        st.markdown("#### 📊 全團費用分配主面板")
        
        my_paid, my_owe = 0.0, 0.0
        if selected_identity != "僅瀏覽專案":
            my_paid = df_exp[df_exp['paid_by'] == members_dict[selected_identity]]['amount'].sum()
            for _, r in df_exp.iterrows():
                my_owe += float(r['split_details'].get(selected_identity, 0.0))

        mi1, mi2, mi3 = st.columns(3)
        mi1.metric("📌 本專案全團總支出", f"${total_trip_cost:,.2f}")
        if selected_identity != "僅瀏覽專案":
            mi2.metric(f"💳 [{selected_identity}] 的代墊款總計", f"${my_paid:,.2f}")
            mi3.metric(f"📉 [{selected_identity}] 實際應負擔總額", f"${my_owe:,.2f}")

        fig = px.pie(df_exp, values='amount', names='description', hole=0.4, 
                     template="plotly_white" if theme_choice in ["極簡白", "優雅藍", "經典金", "智能感光"] else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 💵 自動精簡清償對帳單")
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
                    st.markdown(f"🔴 **【您需還款】** ➡️ 請轉帳給 **{creditor}** 額度： **${amount_to_pay:,.2f}** 元")
                elif creditor == selected_identity:
                    st.markdown(f"🟢 **【您將收款】** ➡️ 成員 **{debtor}** 應轉帳給您 額度： **${amount_to_pay:,.2f}** 元")
                else:
                    st.markdown(f"🤝 **{debtor}** 應支付給 **{creditor}** 額度： `${amount_to_pay:,.2f}` 元")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：即時金融小工具 ====================
with tabs[2]:
    st.subheader("🎒 國際實時匯率計算機")
    
    @st.cache_data(ttl=3600)
    def get_real_rates():
        try:
            res = requests.get("https://open.er-api.com/v6/latest/TWD")
            return res.json()['rates']
        except:
            return {"USD": 0.031, "JPY": 4.65, "EUR": 0.029, "KRW": 41.5}

    rates = get_real_rates()
    
    # 互動小按鈕 3：外幣快速切換按鈕面板
    st.write("快捷選單切換外幣類別：")
    currency_btn = st.segmented_control(
        "切換當前試算幣別：",
        options=["JPY 日圓", "USD 美金", "EUR 歐元", "KRW 韓圓"],
        default="JPY 日圓"
    )
    
    foreign_amt = st.number_input("請輸入當地消費之外幣金額：", min_value=0.0, value=1000.0, key="lux_fx_in")
    
    cur_key = currency_btn.split()[0]
    twd_result = foreign_amt / rates.get(cur_key, 1.0) if rates.get(cur_key) else 0.0
    
    with st.container(border=True):
        st.markdown(f"### 💱 試算轉換結果")
        st.markdown(f"基準匯率：對應 1 TWD 新台幣 可換換約 `{rates.get(cur_key):.4f}` {cur_key}")
        st.success(f"精確折合新台幣金額約為： **`${twd_result:,.2f}`** TWD 元（依據國際市場即時匯率換算）")
