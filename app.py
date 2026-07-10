else:
    cfg = theme_styles[theme_choice]
    # 殿堂級美學架構：精準重構底層 React 組件之視覺權重，徹底杜絕文字隱形與色彩黏滯
    st.html(f"""
    <style>
        /* ==================== 1. 全域底色與奢華字體重構 ==================== */
        .stApp {{ 
            background: {cfg['bg']} !important; 
            color: {cfg['text']} !important; 
        }}
        h1, h2, h3, h4, h5, h6, p, span, label {{ 
            color: {cfg['text']} !important; 
        }}
        
        /* ==================== 2. 側邊欄高階染色與對比度校正 ==================== */
        section[data-testid="stSidebar"] {{ 
            background-color: {cfg['sidebar_bg']} !important; 
            border-right: 1px solid {cfg['border']} !important; 
        }}
        section[data-testid="stSidebar"] *, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {{ 
            color: {cfg['sidebar_text']} !important; 
        }}
        
        /* ==================== 3. 核心打擊：精準修復下拉選單（收合與展開狀態） ==================== */
        
        /* A. 強制修正收合狀態下，輸入框內部的真正文字顏色與背景 */
        div[data-baseweb="select"] div[role="button"] {{
            color: #0F172A !important; /* 不管外圍主題如何變化，只要外框是白色，內部文字一律強制極高對比之深色 */
            background-color: #FFFFFF !important;
            font-weight: 600 !important;
        }}
        
        /* B. 強制修正輸入框內部的 placeholder 或單一值容器 */
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {{
            color: #0F172A !important;
            font-weight: 600 !important;
        }}
        
        /* C. 強制拉開下拉選單右側小箭頭圖標的對比度，避免與白底融為一體 */
        div[data-baseweb="select"] svg {{
            fill: #334155 !important;
            color: #334155 !important;
        }}

        /* D. 當下拉選單展開時，強制彈出的清單選項與容器底色 */
        ul[role="listbox"] {{
            background-color: #FFFFFF !important;
            border: 1px solid {cfg['border']} !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
        }}
        ul[role="listbox"] li {{
            color: #0F172A !important; 
            background-color: #FFFFFF !important;
            padding: 10px 16px !important;
            transition: all 0.2s ease !important;
        }}
        
        /* E. 當清單選項被滑鼠懸停（Hover）或處於選中狀態時的高奢視覺反轉 */
        ul[role="listbox"] li:hover, 
        ul[role="listbox"] li[aria-selected="true"] {{
            background-color: {cfg['border']} !important; 
            color: {cfg['text']} !important; 
            font-weight: 700 !important;
        }}
        
        /* ==================== 4. 高級微奢卡片與數據指標工藝 ==================== */
        div[data-testid="stMetric"] {{ 
            background: {cfg['card']} !important; 
            border: 1px solid {cfg['border']} !important; 
            box-shadow: {cfg['shadow']} !important; 
            border-radius: 18px !important; 
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 40px rgba(0,0,0,0.06) !important;
        }}
        div[data-testid="stMetricValue"] {{ 
            color: {cfg['accent']} !important; 
            font-weight: 800 !important; 
            font-size: 2.3rem !important; 
            letter-spacing: -0.05em !important;
        }}
        
        /* 折疊面板（Expander）奢華圓角與微光邊框 */
        div[data-testid="stExpander"] {{ 
            background: {cfg['card']} !important; 
            border: 1px solid {cfg['border']} !important; 
            border-radius: 16px !important; 
            box-shadow: {cfg['shadow']} !important; 
        }}
        
        /* 奢華高階頁籤（Tabs）微調 */
        .stTabs [data-baseweb="tab"] {{ 
            color: {cfg['subtext']} !important; 
            font-weight: 700 !important; 
            font-size: 1.15rem !important; 
            padding: 14px 28px !important; 
            border-bottom-width: 3px !important;
            transition: all 0.2s ease !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{ 
            color: {cfg['accent']} !important; 
            border-bottom-color: {cfg['accent']} !important; 
        }}
    </style>
    """)
