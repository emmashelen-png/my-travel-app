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

# --- 3. 暴力權重 CSS 注入（直覺改掉字體顏色，徹底解決隱形與灰色問題） ---
if theme_choice == "🌓 智能感光 (隨系統自動日夜切換)":
    st.html("""
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
    """)
    cfg = theme_styles["✨ 經典純白 (極簡日間模式)"]
else:
    cfg = theme_styles[theme_choice]
    
    # 決定下拉選單收合狀態與展開清單的極致色彩防禦
    list_text_color = "#1E293B" if not cfg['is_dark'] else "#F8FAFC"
    list_bg_color = "#FFFFFF" if not cfg['is_dark'] else "#1E293B"
    
    st.html(f"""
    <style>
        /* 全域底色與文字強制顯色 */
        .stApp {{ background: {cfg['bg']} !important; color: {cfg['text']} !important; }}
        h1, h2, h3, h4, h5, h6, p, span, label {{ color: {cfg['text']} !important; }}
        
        /* 側邊欄外觀重編 */
        section[data-testid="stSidebar"] {{ background-color: {cfg['sidebar_bg']} !important; border-right: 1px solid {cfg['border']} !important; }}
        section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {{ color: {cfg['sidebar_text']} !important; }}
        
        /* 🔥 直球修正：強制將下拉選單收合與點開的文字顏色改掉，絕不允許出現灰色隱形 */
        div[data-baseweb="select"] div[role="button"],
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {{
            color: #1E293B !important; /* 確保輸入框內文字絕對是極高對比度的深石墨色 */
            font-weight: 600 !important;
        }}
        div[data-baseweb="select"] svg {{ fill: #475569 !important; }} /* 小箭頭同步加深 */

        /* 下拉選單展開後的清單防護 */
        ul[role="listbox"] {{ background-color: {list_bg_color} !important; border: 1px solid {cfg['border']} !important; border-radius: 12px !important; }}
        ul[role="listbox"] li {{ color: {list_text_color} !important; background-color: {list_bg_color} !important; padding: 10px 16px !important; }}
        ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] {{
            background-color: {cfg['accent']} !important;
            color: #FFFFFF !important; /* 反白時文字強制變純白 */
        }}
        
        /* 📊 數據指標與折疊卡片微浮動與微縮放動畫 */
        div[data-testid="stMetric"], div[data-testid="stExpander"] {{
            background: {cfg['card']} !important;
            border: 1px solid {cfg['border']} !important;
            border-radius: 14px !important;
            box-shadow: {cfg['shadow']} !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px) scale(1.01) !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.08) !important;
        }}
        div[data-testid="stMetricValue"] {{ color: {cfg['accent']} !important; font-weight: 800 !important; }}
        
        /* 🚀 按鈕動態回饋動畫（點擊微縮放與平滑漸變） */
        div.stButton > button {{
            border-radius: 10px !important;
            transition: all 0.2s ease-in-out !important;
        }}
        div.stButton > button:hover {{
            transform: scale(1.02) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}
        div.stButton > button:active {{
            transform: scale(0.97) !important;
        }}
    </style>
    """)

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

    # 高相容性安全渲染
    iti_res = supabase.table("itineraries").select("*").eq("trip_id", current_trip_id).order("day_number").order("time_slot").execute()
    if iti_res.data:
        df_iti = pd.DataFrame(iti_res.data)
        for day_num, group in df_iti.groupby("day_number"):
            st.markdown(f"#### 🗓️ 第 {day_num} 天 行程清單")
            for _, row in group.iterrows():
                with st.container(border=True):
                    ic1, ic2 = st.columns([1, 5])
                    ic1.markdown(f"⏱️ **{row['time_slot'][:5]}**")
                    ic2.markdown(f"**[{row['activity_type']}] {row['title']}**\n\n說明：*{row['note'] if row['note'] else '無'}*")
                    
                    # 修改與移除（內建微縮放互動動畫按鈕）
                    b1, b2, _ = st.columns([1, 1, 8])
                    with b1:
                        with st.popover("✏️ 編輯明細"):
                            nt = st.text_input("更新項目名稱", value=row['title'], key=f"c_t_{row['id']}")
                            nn = st.text_area("更新備註說明", value=row['note'] if row['note'] else "", key=f"c_n_{row['id']}")
                            if st.button("確認修改", key=f"c_u_{row['id']}", type="primary"):
                                supabase.table("itineraries").update({"title": nt, "note": nn}).eq("id", row['id']).execute()
                                st.rerun()
                    with b2:
                        # 🛠️ 二次安全確認防呆彈窗（帶有平滑互動動畫）
                        with st.popover("🗑️ 移除節點"):
                            st.warning("確定
