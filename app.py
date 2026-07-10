import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- 1. 初始化 Supabase 連線 ---
SUPABASE_URL = "https://xmzpwmpvlfdndwnbxbxf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtenB3bXB2bGZkbmR3bmJ4YnhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MDIyNTMsImV4cCI6MjA5OTE3ODI1M30.lL44XcL7wvPqJrCUPAKL1K8K98YbcDQGWKIKgqLnH8o"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 頁面高質感設定
st.set_page_config(page_title="🧳 智慧隨身旅遊管家", layout="wide", initial_sidebar_state="expanded")

# --- 1.5 原生高質感 PWA 樣式注入（100% 繞過 markdown 類型檢查） ---
st.html("""
<style>
    /* 全域背景與優雅字體 */
    .stApp { 
        background: linear-gradient(135deg, #121214 0%, #1a1a1e 100%); 
        color: #f4f4f5;
    }
    /* 頂級數據指標卡片 */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    div[data-testid="stMetricValue"] { 
        font-size: 2rem !important; 
        font-weight: 800 !important; 
        color: #00f0ff !important; 
    }
    /* 精緻頁籤設計 */
    .stTabs [data-baseweb="tab"] { 
        font-size: 1.1rem; 
        font-weight: 600; 
        padding: 12px 24px;
        color: #a1a1aa;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
    }
    /* 行程與記帳高質感卡片 */
    .trip-card { 
        background: rgba(255, 255, 255, 0.04); 
        padding: 22px; 
        border-radius: 14px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        margin-bottom: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .expense-card { 
        background: rgba(0, 240, 255, 0.03); 
        padding: 18px; 
        border-radius: 10px; 
        border-left: 6px solid #00f0ff; 
        border-top: 1px solid rgba(0, 240, 255, 0.1);
        border-right: 1px solid rgba(0, 240, 255, 0.1);
        border-bottom: 1px solid rgba(0, 240, 255, 0.1);
        margin-bottom: 12px; 
    }
    .transit-card { 
        background: rgba(187, 134, 252, 0.03); 
        padding: 18px; 
        border-radius: 10px; 
        border-left: 6px solid #bb86fc; 
        border-top: 1px solid rgba(187, 134, 252, 0.1);
        border-right: 1px solid rgba(187, 134, 252, 0.1);
        border-bottom: 1px solid rgba(187, 134, 252, 0.1);
        margin-bottom: 12px; 
    }
</style>
""")

# --- 2. 側邊欄：旅程庫與管理 ---
st.sidebar.title("🧳 我的旅遊庫")

# 新增旅程
with st.sidebar.expander("➕ 建立全新旅程", expanded=False):
    new_trip_name = st.text_input("旅程名稱", placeholder="例如：2026東京慶生團")
    new_trip_sub = st.text_input("副標題", placeholder="例如：暑假吃貨之旅")
    num_members = st.number_input("成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"成員 {i+1}", key=f"new_m_{i}") for i in range(int(num_members))]
    
    if st.button("🚀 點我創建旅程", use_container_width=True):
        if new_trip_name:
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": new_trip_sub}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success("🎉 創建成功！")
            st.rerun()

# 讀取旅程
trips_res = supabase.table("trips").select("*").order("created_at").execute()
trip_options = {t['name']: t['id'] for t in trips_res.data} if trips_res.data else {}

if not trip_options:
    st.info("👋 歡迎！請先在左側邊欄創建您的第一個旅遊行程。")
    st.stop()

selected_trip_name = st.sidebar.selectbox("🧭 切換目前查看的行程：", list(trip_options.keys()))
current_trip_id = trip_options[selected_trip_name]

# 獲取旅程詳細資料
current_trip = supabase.table("trips").select("*").eq("id", current_trip_id).single().execute().data
members_res = supabase.table("members").select("*").eq("trip_id", current_trip_id).execute()
members_dict = {m['name']: m['id'] for m in members_res.data}
members_id_to_name = {m['id']: m['name'] for m in members_res.data}

# 認領身分機制
st.sidebar.markdown("---")
selected_identity = st.sidebar.selectbox("👤 認領你是誰（高亮你的帳目）：", ["僅瀏覽者"] + list(members_dict.keys()))

# 管理當前旅程（修改與刪除）
with st.sidebar.expander("⚙️ 修改/刪除當前旅程", expanded=False):
    edit_name = st.text_input("修改旅程名稱", value=current_trip['name'])
    edit_sub = st.text_input("修改副標題", value=current_trip['subtitle'] if current_trip['subtitle'] else "")
    if st.button("💾 儲存修改"):
        supabase.table("trips").update({"name": edit_name, "subtitle": edit_sub}).eq("id", current_trip_id).execute()
        st.success("修改成功！")
        st.rerun()
        
    st.markdown("---")
    st.warning("⚠️ 危險操作")
    if st.button("🗑️ 刪除整趟旅程（不可逆）", type="primary"):
        supabase.table("trips").delete().eq("id", current_trip_id).execute()
        st.sidebar.success("旅程已刪除")
        st.rerun()

# --- 主畫面大標題 ---
st.title(f"✈️ {current_trip['name']}")
if current_trip['subtitle']:
    st.caption(f"💡 {current_trip['subtitle']}")

tabs = st.tabs(["📅 時間線行程規劃", "💰 隨手分帳", "🎒 實用工具箱"])

# ==================== 頁籤一：時間線行程規劃 ====================
with tabs[0]:
    st.header("🗺️ 行程與交通節點")
    
    with st.expander("➕ 新增行程/交通節點"):
        c1, c2, c3 = st.columns(3)
        with c1:
            day = st.number_input("第幾天", min_value=1, value=1, key="iti_day")
            time_slot = st.time_input("時間", key="iti_time")
        with c2:
            act_type = st.selectbox("項目類型", ["📍 景點", "🚗 交通(主線)", "🔄 交通(轉乘提示)"], key="iti_type")
            title = st.text_input("項目名稱", placeholder="例如：清水寺 / 關空特快 HARUKA", key="iti_title")
        with c3:
            cost = st.number_input("預估花費 (TWD)", min_value=0.0, value=0.0, key="iti_cost")
            note = st.text_area("備註說明", placeholder="月台資訊、優惠券、口袋名單備註...", key="iti_note")
            
        if st.button("✨ 成功加入時間線", use_container_width=True):
            if title:
                supabase.table("itineraries").insert({
                    "trip_id": current_trip_id, "day_number": day, "time_slot": str(time_slot),
                    "activity_type": act_type, "title": title, "cost": cost, "note": note
                }).execute()
                st.rerun()

    # 顯示精美卡片式時間線
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"### ☀️ 第 {day_num} 天 行程")
            for _, row in group.iterrows():
                is_trans = "交通" in row['activity_type']
                card_class = "transit-card" if is_trans else "trip-card"
                
               # 美化卡片渲染（使用最新官方 HTML 標準，精緻卡片）
                st.html(f"""
                <div class="{card_class}">
                    <span style='color:#00efff; font-weight:bold; letter-spacing: 1px;'>⏱️ {row['time_slot'][:5]}</span> 
                    <span style='color: rgba(255,255,255,0.4); margin: 0 8px;'>|</span>
                    <span style='font-size:1.1rem; font-weight:600; color: #ffffff;'>{row['activity_type']} - {row['title']}</span>
                    <div style='margin-top: 6px; font-size: 0.9rem; color:#a1a1aa; line-height: 1.4;'>ℹ️ {row['note'] if row['note'] else '無備註说明'}</div>
                </div>
                """)
                
                # 修改與刪除按鈕排版
                cb1, cb2, _ = st.columns([1, 1, 8])
                with cb1:
                    with st.popover("✏️ 修改"):
                        new_t = st.text_input("修改名稱", value=row['title'], key=f"edit_it_t_{row['id']}")
                        new_n = st.text_area("修改備註", value=row['note'] if row['note'] else "", key=f"edit_it_n_{row['id']}")
                        new_c = st.number_input("修改花費", value=float(row['cost']), key=f"edit_it_c_{row['id']}")
                        if st.button("更新", key=f"up_it_{row['id']}"):
                            supabase.table("itineraries").update({"title": new_t, "note": new_n, "cost": new_c}).eq("id", row['id']).execute()
                            st.rerun()
                with cb2:
                    if st.button("🗑️ 刪除", key=f"del_it_{row['id']}", type="primary"):
                        supabase.table("itineraries").delete().eq("id", row['id']).execute()
                        st.rerun()

# ==================== 頁籤二：Spliit 級隨手分帳系統 ====================
with tabs[1]:
    st.header("💰 智慧帳本")
    
    # 記帳輸入區
    with st.container(border=True):
        st.subheader("📝 隨手記一筆新支出")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費項目描述", placeholder="例如：一蘭拉麵、金閣寺門票")
            exp_amount = st.number_input("總金額", min_value=0.0, value=0.0, step=10.0)
        with cx2:
            payer = st.selectbox("誰付的錢？", list(members_dict.keys()), key="payer_box")
            split_method = st.radio("分帳方式", ["均分 (Equal)", "自訂金額 (Exact)"], horizontal=True)
        
        # 精準照搬 Spliit 的即時修正互動邏輯
        split_details = {}
        with cx3:
            st.markdown("🎯 **分帳即時即時分配計算**")
            if split_method == "均分 (Equal)":
                if len(members_dict) > 0:
                    share = round(exp_amount / len(members_dict), 2)
                    for m in members_dict.keys():
                        split_details[m] = share
                    st.info(f"💡 每人均分：${share:,.2f} 元")
                    can_submit = True if exp_amount > 0 else False
            else:
                # 自訂金額動態修正
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"{m} 應付金額", min_value=0.0, value=0.0, key=f"js_split_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                # 即時動態提示
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.success("✅ 金額完全吻合！可以儲存。")
                    can_submit = True
                elif diff > 0:
                    st.warning(f" 還有 `${diff:,.2f}` 元尚未分配！")
                    can_submit = False
                else:
                    st.error(f"⚠️ 已超出總金額 `${abs(diff):,.2f}` 元！")
                    can_submit = False
                    
        if st.button("💾 儲存此筆帳目", disabled=not can_submit, use_container_width=True, type="primary"):
            supabase.table("expenses").insert({
                "trip_id": current_trip_id, "description": exp_desc, "amount": exp_amount,
                "paid_by": members_dict[payer], "split_details": split_details
            }).execute()
            st.success("記帳成功！")
            st.rerun()

    # 數據視覺化指標卡片
    exp_res = supabase.table("expenses").select("*").eq("trip_id", current_trip_id).execute()
    if exp_res.data:
        df_exp = pd.DataFrame(exp_res.data)
        total_trip_cost = df_exp['amount'].sum()
        
        st.markdown("---")
        st.subheader("📊 本次旅程花費數據統計")
        
        # 計算個人總支出（我付了多少、我該負擔多少）
        my_paid = 0.0
        my_owe = 0.0
        if selected_identity != "僅瀏覽者":
            # 我墊付的
            my_paid_df = df_exp[df_exp['paid_by'] == members_dict[selected_identity]]
            my_paid = my_paid_df['amount'].sum()
            # 我應該出的
            for _, r in df_exp.iterrows():
                my_owe += float(r['split_details'].get(selected_identity, 0.0))

        mi1, mi2, mi3 = st.columns(3)
        with mi1:
            st.metric("🎨 全團總花費", f"${total_trip_cost:,.2f}")
        with mi2:
            if selected_identity != "僅瀏覽者":
                st.metric(f"💳 {selected_identity} 總共代墊", f"${my_paid:,.2f}")
        with mi3:
            if selected_identity != "僅瀏覽者":
                st.metric(f"📉 {selected_identity} 實際個人消費", f"${my_owe:,.2f}")

        # 高質感圓餅圖
        fig = px.pie(df_exp, values='amount', names='description', hole=0.4,
                     template="plotly_dark", color_discrete_sequence=px.colors.sequential.Cyan_r)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # 歷史明細管理（支援修改與刪除）
        st.subheader("📋 帳目歷史明細與維護")
        for _, row in df_exp.iterrows():
            payer_name = members_id_to_name[row['paid_by']]
            
            # 高亮顯示跟我有關的卡片
            is_my_involvement = (payer_name == selected_identity)
            border_style = "border-left: 5px solid #ff4b4b;" if is_my_involvement else ""
            
            st.markdown(f"""
            <div class="expense-card" style="{border_style}">
                <strong>項目：{row['description']}</strong> | 總額：<span style='color:#00efff;'>${row['amount']:,}</span> 
                <br><small style='color:#a1a1aa;'>由 {payer_name} 支付</small>
            </div>
            """, unsafe_allowed_html=True)
            
            mx1, mx2, _ = st.columns([1, 1, 8])
            with mx1:
                with st.popover("✏️ 修改金額/描述"):
                    new_desc = st.text_input("修改描述", value=row['description'], key=f"ed_ex_d_{row['id']}")
                    new_amt = st.number_input("修改總額", value=float(row['amount']), key=f"ed_ex_a_{row['id']}")
                    st.caption("均分比例將在更新後自動重新配置")
                    if st.button("更新帳目", key=f"up_ex_{row['id']}"):
                        # 自動平分防呆更新
                        new_share = round(new_amt / len(members_dict), 2)
                        new_details = {m: new_share for m in members_dict.keys()}
                        supabase.table("expenses").update({"description": new_desc, "amount": new_amt, "split_details": new_details}).eq("id", row['id']).execute()
                        st.rerun()
            with mx2:
                if st.button("🗑️ 刪除", key=f"del_ex_{row['id']}", type="primary"):
                    supabase.table("expenses").delete().eq("id", row['id']).execute()
                    st.rerun()

        # 債務精簡演算法（誰欠誰錢）
        st.markdown("---")
        st.subheader("💵 即時債務結算帳單")
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
            
            # 高亮標注與「我」相關的債務提示
            if debtor == selected_identity:
                st.error(f"🔴 【你需要還錢】 ➡️ 你需要轉帳給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            elif creditor == selected_identity:
                st.success(f"🟢 【等著收錢】 ➡️ **{debtor}** 應該轉帳給你 👉 `${amount_to_pay:,.2f}` 元")
            else:
                st.info(f"💳 **{debtor}** 應給 **{creditor}** 👉 `${amount_to_pay:,.2f}` 元")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：實用工具箱 ====================
with tabs[2]:
    st.header("🎒 隨身小工具")
    st.caption("AI 助手與即時匯率換算")
    # (保留原有的輕量 AI 與匯率換算程式碼...)
