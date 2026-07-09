import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import json

# --- 1. 初始化 Supabase 連線 ---
# 請將下方的 URL 和 KEY 替換成你在 Supabase 申請到的資料
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="📱 🧳 智慧隨身旅遊管家", layout="wide")

# --- 2. 旅程選擇與創建管理 ---
st.sidebar.title("🧳 我的旅遊庫")
with st.sidebar.expander("➕ 新增全新旅程", expanded=False):
    new_trip_name = st.text_input("旅程名稱", placeholder="例如：2026東京慶生團")
    new_trip_sub = st.text_input("副標題", placeholder="例如：暑假六天五夜吃貨之旅")
    
    # 動態成員輸入（免 Email，直接填稱呼）
    num_members = st.number_input("成員人數", min_value=1, max_value=10, value=2)
    member_names = []
    for i in range(int(num_members)):
        name = st.text_input(f"第 {i+1} 位成員暱稱", value=f"成員 {i+1}")
        member_names.append(name)
        
    if st.button("創建旅程"):
        if new_trip_name:
            trip_data = supabase.table("trips").insert({"name": new_trip_name, "subtitle": new_trip_sub}).execute()
            trip_id = trip_data.data[0]['id']
            for m_name in member_names:
                supabase.table("members").insert({"trip_id": trip_id, "name": m_name}).execute()
            st.success("旅程創建成功！請重新整理網頁。")

# 讀取現有所有旅程
trips_res = supabase.table("trips").select("*").execute()
trip_options = {t['name']: t['id'] for t in trips_res.data} if trips_res.data else {}

if not trip_options:
    st.info("👋 歡迎！請先在左側邊欄創建您的第一個旅遊行程。")
    st.stop()

selected_trip_name = st.sidebar.selectbox("切換目前查看的行程：", list(trip_options.keys()))
current_trip_id = trip_options[selected_trip_name]

# 獲取當前旅程詳情與成員
current_trip = supabase.table("trips").select("*").eq("id", current_trip_id).single().execute().data
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# --- 主畫面標題 ---
st.title(f"✈️ {current_trip['name']}")
if current_trip['subtitle']:
    st.caption(f"💡 {current_trip['subtitle']}")

# --- 3. 認領身分功能（免登入機制） ---
st.sidebar.markdown("---")
if 'my_identity' not in st.session_state:
    st.session_state['my_identity'] = "未認領"

selected_identity = st.sidebar.selectbox("👤 認領你是誰（方便記帳與清單打卡）：", ["瀏覽者"] + list(members_dict.keys()))
if selected_identity != "瀏覽者":
    st.session_state['my_identity'] = selected_identity

# --- 4. 頁籤分類：行程、記帳、工具 ---
tabs = st.tabs(["📅 時間線行程", "💰 Spliit 級即時分帳", "🎒 實用工具箱"])

# ==================== 頁籤一：時間線行程 ====================
with tabs[0]:
    st.header("行程與交通規劃")
    
    # 新增行程/交通表單
    with st.expander("➕ 新增景點或交通節點"):
        col1, col2, col3 = st.columns(3)
        with col1:
            day = st.number_input("第幾天", min_value=1, value=1)
            time_slot = st.time_input("時間")
        with col2:
            act_type = st.selectbox("類型", ["景點", "交通(主線)", "交通(轉乘防呆)"])
            title = st.text_input("名稱/項目", placeholder="例如：清水寺 或 關空特快 HARUKA")
        with col3:
            cost = st.number_input("預估花費 (可不填)", min_value=0.0, value=0.0)
            note = st.text_area("備註說明", placeholder="交通票券資訊、轉乘月台等")
            
        if st.button("加入時間線"):
            is_transit = "交通" in act_type
            supabase.table("itineraries").insert({
                "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                "activity_type": act_type, "title": title, "cost": cost, "note": note, "is_transit": is_transit
            }).execute()
            st.rerun()

    # 顯示時間線
    iti_res = supabase.table("itineraries").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.subheader(f"☀️ 第 {day_num} 天")
            for idx, row in group.iterrows():
                icon = "🚗" if "交通" in row['activity_type'] else "📍"
                indent = "  ↳ 🔄 [轉乘提示] " if "轉乘" in row['activity_type'] else ""
                
                # 佈局顯示
                c_time, c_content, c_cost = st.columns([1, 4, 1])
                c_time.write(f"`{row['time_slot'][:5]}`")
                c_content.markdown(f"**{indent}{icon} {row['title']}**\n*{row['note'] if row['note'] else ''}*")
                if row['cost'] > 0:
                    c_cost.write(f"💰 ${row['cost']:,}")
                    
                # 修改與刪除防呆
                if st.button("🗑️", key=f"del_{row['id']}"):
                    supabase.table("itineraries").delete().eq("id", row['id']).execute()
                    st.rerun()

# ==================== 頁籤二：即時分帳系統 ====================
with tabs[1]:
    st.header("分帳帳本 (Spliit 模式)")
    
    # 記帳輸入區
    with st.expander("📝 隨手記一筆支出", expanded=True):
        exp_desc = st.text_input("消費項目描述", placeholder="例如：一蘭拉麵、飯店住宿費")
        exp_amount = st.number_input("總金額", min_value=0.0, value=0.0, step=10.0)
        payer = st.selectbox("誰付的錢？", list(members_dict.keys()))
        
        st.write("📊 **分帳權重/金額自訂（即時修正）：**")
        split_method = st.radio("分帳方式", ["均分", "自訂金額"])
        
        split_details = {}
        if split_method == "均分":
            if len(members_dict) > 0:
                share = round(exp_amount / len(members_dict), 2)
                for m in members_dict.keys():
                    split_details[m] = share
                    st.caption(f" {m}： 均分 ${share}")
        else:
            current_total = 0.0
            for m in members_dict.keys():
                amt = st.number_input(f"{m} 應付金額", min_value=0.0, value=0.0, key=f"split_{m}")
                split_details[m] = amt
                current_total += amt
            # 防呆機制
            if abs(current_total - exp_amount) > 0.01:
                st.error(f"⚠️ 警告：自訂金額總和 (${current_total}) 與總金額 (${exp_amount}) 不符！")
                
        if st.button("儲存帳目"):
            if exp_amount > 0 and exp_desc:
                supabase.table("expenses").insert({
                    "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                    "paid_by": members_dict[payer], "split_details": split_details
                }).execute()
                st.success("記帳成功！")
                st.rerun()

    # 計算統計與誰欠誰錢（核心核心演算法）
    exp_res = supabase.table("expenses").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        st.subheader("📊 費用統計與圖表")
        df_exp = pd.DataFrame(exp_res.data)
        
        # 總支出
        total_trip_cost = df_exp['amount'].sum()
        st.metric("🎨 本次旅程總支出", f"${total_trip_cost:,.2f}")
        
        # 圓餅圖
        fig = px.pie(df_exp, values='amount', names='description', title='花費分佈圖')
        st.plotly_chart(fig, use_container_width=True)
        
        # 結算核心邏輯
        balances = {m: 0.0 for m in members_dict.keys()}
        for exp in exp_res.data:
            p_name = members_id_to_name[exp['paid_by']]
            balances[p_name] += float(exp['amount']) # 付錢的人加上正資產
            for m_name, s_amt in exp['split_details'].items():
                balances[m_name] -= float(s_amt) # 應該付錢的人扣掉
                
        st.subheader("💵 即時債務結算（誰該給誰多少錢）")
        debtors = [(k, v) for k, v in balances.items() if v < 0]
        creditors = [(k, v) for k, v in balances.items() if v > 0]
        
        # 簡單清償機制
        while debtors and creditors:
            debtor, d_bal = debtors[0]
            creditor, c_bal = creditors[0]
            amount_to_pay = min(abs(d_bal), c_bal)
            
            st.info(f"💳 **{debtor}** 應給 **{creditor}** 👉 `${amount_to_pay:,.2f}`")
            
            # 更新剩餘金額
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：實用工具箱 ====================
with tabs[2]:
    st.header("隨身工具")
    
    # AI 景點推薦接口（低依賴度、免輸入）
    st.subheader("🤖 輕量級 AI 旅程靈感助手")
    ai_prompt = st.text_input("想問 AI 什麼？（例如：京都傍晚推薦去哪裡？）")
    if st.button("詢問 AI"):
        with st.spinner("AI 正在思考中..."):
            # 這裡預留了擴充，新手可直接調用免費 API 或做靜態防呆指引
            st.write(f"💡 針對 '{ai_prompt}' 的建議：建議前往動態景點，並多預留 30 分鐘轉乘時間防止迷路！")
            
    # 匯率換算器
    st.subheader("💱 即時外幣換算")
    twd_amt = st.number_input("輸入台幣 (TWD)", min_value=0.0, value=1000.0)
    st.write(f"🇯🇵 折合日幣 (JPY) 約：`{twd_amt * 4.65:,.2f}` 日圓 (以 1:4.65 概算)")