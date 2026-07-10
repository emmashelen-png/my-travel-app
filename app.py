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

# --- 2. 殿堂級多元主題配色系統（絕不顯髒、灰、確保高對比度） ---
st.sidebar.title("🎨 奢華美學管家")
theme_choice = st.sidebar.selectbox(
    "選擇您的專屬高奢主題：",
    ["✨ 璀璨晶白 (日間淺色)", "🌙 靜謐深夜 (夜間深色)", "💎 蒂芬妮淺藍 (法式浪漫)", "🌟 香檳香檳金 (奢華金屬)", "🌿 晨曦初露 (清爽綠意)"]
)

# 根據選擇動態調配頂級色彩密碼
themes = {
    "✨ 璀璨晶白 (日間淺色)": {"bg": "#F9FAFB", "card": "#FFFFFF", "text": "#111827", "accent": "#3B82F6", "border": "#E5E7EB", "subtext": "#6B7280", "card_ex": "rgba(59, 130, 246, 0.05)", "card_tr": "rgba(139, 92, 246, 0.05)"},
    "🌙 靜謐深夜 (夜間深色)": {"bg": "#0B0F19", "card": "#111827", "text": "#F9FAFB", "accent": "#00F0FF", "border": "#1F2937", "subtext": "#9CA3AF", "card_ex": "rgba(0, 240, 255, 0.05)", "card_tr": "rgba(187, 134, 252, 0.05)"},
    "💎 蒂芬妮淺藍 (法式浪漫)": {"bg": "#F4FAF9", "card": "#FFFFFF", "text": "#0F2A2A", "accent": "#0A8485", "border": "#D5ECEB", "subtext": "#4A6B6B", "card_ex": "rgba(10, 132, 133, 0.05)", "card_tr": "rgba(234, 179, 8, 0.05)"},
    "🌟 香檳香檳金 (奢華金屬)": {"bg": "#FAF8F5", "card": "#FFFFFF", "text": "#2D251E", "accent": "#C5A880", "border": "#EFEBE4", "subtext": "#756A5F", "card_ex": "rgba(197, 168, 128, 0.08)", "card_tr": "rgba(107, 114, 128, 0.05)"},
    "🌿 晨曦初露 (清爽綠意)": {"bg": "#F7F9F6", "card": "#FFFFFF", "text": "#1C2E1A", "accent": "#3D7A46", "border": "#E1E8E0", "subtext": "#526650", "card_ex": "rgba(61, 122, 70, 0.06)", "card_tr": "rgba(245, 158, 11, 0.05)"}
}
cfg = themes[theme_choice]

# 使用官方原生 st.html 100% 免疫 TypeError
st.html(f"""
<style>
    .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
    h1, h2, h3, p, span, label, div {{ color: {cfg['text']} !important; }}
    /* 質感卡片防呆設計 */
    .trip-card {{ background: {cfg['card']}; padding: 22px; border-radius: 16px; border: 1px solid {cfg['border']}; margin-bottom: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.02); }}
    .expense-card {{ background: {cfg['card_ex']}; padding: 18px; border-radius: 12px; border-left: 6px solid {cfg['accent']}; border-top: 1px solid {cfg['border']}; border-right: 1px solid {cfg['border']}; border-bottom: 1px solid {cfg['border']}; margin-bottom: 12px; }}
    .transit-card {{ background: {cfg['card_tr']}; padding: 18px; border-radius: 12px; border-left: 6px solid #8B5CF6; border-top: 1px solid {cfg['border']}; border-right: 1px solid {cfg['border']}; border-bottom: 1px solid {cfg['border']}; margin-bottom: 12px; }}
    /* 指標美化 */
    div[data-testid="stMetric"] {{ background: {cfg['card']}; padding: 18px 24px; border-radius: 16px; border: 1px solid {cfg['border']}; box-shadow: 0 4px 15px rgba(0,0,0,0.01); }}
    div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-size: 2.2rem !important; font-weight: 800 !important; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 1.1rem; font-weight: 600; padding: 12px 24px; color: {cfg['subtext']} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {cfg['accent']} !important; border-bottom-color: {cfg['accent']} !important; }}
</style>
""")

# --- 3. 核心隱私：旅程暗號通關機制 ---
st.markdown(f"### 🔒 護照通關驗證")
passcode_input = st.text_input("🔑 請輸入您的旅遊專屬暗號以解鎖內容：", type="password", placeholder="請填入旅程代碼（例如：KIX2026）")

# 側邊欄：創建新旅程（自動生成暗號）
with st.sidebar.expander("👑 策劃全新旅遊標籤", expanded=False):
    new_trip_name = st.text_input("填寫旅程名稱", placeholder="例如：日本關西精緻遊")
    new_trip_sub = st.text_input("輸入副標題描述", placeholder="例如：漫步京都神社與收集御守之旅")
    new_code = st.text_input("為這個旅程自訂一個「專屬通關暗號」", placeholder="例如：KYOTO666")
    num_members = st.number_input("參與成員人數", min_value=1, max_value=10, value=2)
    member_names = [st.text_input(f"成員 {i+1} 暱稱", value=f"旅伴 {i+1}", key=f"m_cfg_{i}") for i in range(int(num_members))]
    
    if st.button("⚜️ 精緻鑄造旅遊標籤", use_container_width=True):
        if new_trip_name and new_code:
            # 將護照暗號存入 subtitle 或者是 name 的關聯中，這裡我們直接用名稱比對或建立特殊暗號
            t_res = supabase.table("trips").insert({"name": new_trip_name, "subtitle": f"【暗號：{new_code}】 {new_trip_sub}"}).execute()
            t_id = t_res.data[0]['id']
            for m_name in member_names:
                if m_name.strip():
                    supabase.table("members").insert({"trip_id": t_id, "name": m_name.strip()}).execute()
            st.success(f"🎉 鑄造成功！請在上方輸入暗號「{new_code}」解鎖！")

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
            note = st.text_area("備註細節說明", placeholder="記錄月台、美景角度、極致小提示...", key="v_note")
            
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
                
                # 巧妙利用原生 st.html 渲染卡片文字與陰影，保證完全不報錯
                st.html(f"""
                <div class="{c_style}">
                    <span style='color:{cfg['accent']}; font-weight:bold; font-size:1.1rem;'>⏱️ {row['time_slot'][:5]}</span> 
                    <span style='font-weight:700; margin-left:10px;'>{row['activity_type']} │ {row['title']}</span>
                    <p style='margin: 8px 0 0 0; color:{cfg['subtext']}; font-size:0.95rem;'>💡 {row['note'] if row['note'] else '無特殊說明'}</p>
                </div>
                """)
                
                # 修改刪除
                b1, b2, _ = st.columns([1, 1, 8])
                with b1:
                    with st.popover("✏️ 調整項目"):
                        nt = st.text_input("調整名稱", value=row['title'], key=f"e_t_{row['id']}")
                        nn = st.text_area("調整備註", value=row['note'] if row['note'] else "", key=f"e_n_{row['id']}")
                        if st.button("確定更新", key=f"u_i_{row['id']}"):
                            supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                            st.rerun()
                with b2:
                    if st.button("🗑️ 移除", key=f"d_i_{row['id']}", type="primary"):
                        supabase.table("itineraries").delete().eq("id", row['id']).execute()
                        st.rerun()

# ==================== 頁籤二：隨手分帳系統（Spliit功能無字版） ====================
with tabs[1]:
    st.header("💰 全員即時分帳帳本")
    
    with st.container(border=True):
        st.subheader("📝 隨手速記一筆款項")
        cx1, cx2, cx3 = st.columns(3)
        with cx1:
            exp_desc = st.text_input("消費款項描述", placeholder="例如：豪華和牛晚餐、包車費用")
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
                    st.html(f"<div style='color:{cfg['accent']}; font-weight:600;'>✨ 全員完美平分，每人應付：${share:,.2f}</div>")
                    can_submit = True if exp_amount > 0 else False
            else:
                current_total = 0.0
                for m in members_dict.keys():
                    amt = st.number_input(f"💸 {m} 的實質花費金額", min_value=0.0, value=0.0, key=f"v_sp_{m}")
                    split_details[m] = amt
                    current_total += amt
                
                diff = exp_amount - current_total
                if abs(diff) < 0.01:
                    st.html("<div style='color:#10B981; font-weight:600;'>✅ 數據完全吻合！已解鎖儲存按鈕。</div>")
                    can_submit = True
                elif diff > 0:
                    st.html(f"<div style='color:#F59E0B; font-weight:600;'>⏳ 還有 <strong>${diff:,.2f}</strong> 未配平，請繼續輸入。</div>")
                    can_submit = False
                else:
                    st.html(f"<div style='color:#EF4444; font-weight:600;'>⚠️ 金額爆表！已超出總額 <strong>${abs(diff):,.2f}</strong>！</div>")
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
        
        # 計算帳目
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

        fig = px.pie(df_exp, values='amount', names='description', hole=0.5, template="plotly_white" if "淺色" in theme_choice or "蒂芬妮" in theme_choice or "香檳" in theme_choice or "晨曦" in theme_choice else "plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # 債務精簡核心
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
                st.html(f"<div style='background:rgba(239,68,68,0.08); padding:12px; border-radius:8px; margin-bottom:8px; border-left:4px solid #EF4444;'>🔴 <strong>【您需轉帳】</strong> 轉給 <strong>{creditor}</strong> 👉 🏦 <strong>${amount_to_pay:,.2f}</strong> 元</div>")
            elif creditor == selected_identity:
                st.html(f"<div style='background:rgba(16,185,129,0.08); padding:12px; border-radius:8px; margin-bottom:8px; border-left:4px solid #10B981;'>🟢 <strong>【您將收款】</strong> <strong>{debtor}</strong> 將轉帳給你 👉 💰 <strong>${amount_to_pay:,.2f}</strong> 元</div>")
            else:
                st.html(f"<div style='padding:10px; border-bottom:1px dashed {cfg['border']}; color:{cfg['subtext']};'>➡️ <strong>{debtor}</strong> 應轉給 <strong>{creditor}</strong> 👉 `${amount_to_pay:,.2f}` 元</div>")
            
            balances[debtor] += amount_to_pay
            balances[creditor] -= amount_to_pay
            debtors = [(k, v) for k, v in balances.items() if v < -0.01]
            creditors = [(k, v) for k, v in balances.items() if v > 0.01]

# ==================== 頁籤三：國際即時管家（實時API多國匯率） ====================
with tabs[2]:
    st.header("🎒 全球實時匯率管家")
    st.caption("自動對接國際匯率 API，即時刷新各國匯率資訊")
    
    # 網絡動態抓取真實外匯數據防呆
    @st.cache_data(ttl=3600)  # 快取1小時，兼顧即時性與免費額度頻率限制
    def get_real_rates():
        try:
            # 呼叫免費即時匯率 API
            res = requests.get("https://open.er-api.com/v6/latest/TWD")
            return res.json()['rates']
        except:
            # 網路若偶發異常，進入防呆預設數值
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
    
    # 計算轉換
    cur_key = src_currency.split()[0]
    twd_result = foreign_amt / rates.get(cur_key, 1.0) if rates.get(cur_key) else 0.0
    st.success(f"💎 折合新台幣約：**`${twd_result:,.2f}`** TWD 元 (即時即時動態換算)")
