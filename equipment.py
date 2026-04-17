import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz

st.set_page_config(
    page_title="ครุภัณฑ์ Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Category definitions ──────────────────────────────────────────────────────
CATEGORIES = {
    "ครุภัณฑ์ก่อสร้าง": {
        "en": "Construction",
        "sitem_names": ["ครุภัณฑ์ก่อสร้าง", "ครุภัณฑ์เครื่องจักรกล"],
        "keywords": ["ก่อสร้าง", "เครื่องจักรกล", "รถแบ็คโฮ", "รถดันดิน", "รถตักหน้าขุดหลัง", "เครื่องอัดถนน"],
    },
    "ครุภัณฑ์การเกษตร": {
        "en": "Agriculture",
        "sitem_names": ["ครุภัณฑ์การเกษตร", "ครุภัณฑ์นวัตกรรมไทย-ด้านการเกษตร"],
        "keywords": ["เครื่องสีข้าว", "เกษตร", "สมาร์ทฟาร์ม", "Smart Farm", "นวัตกรรมเกษตร", "เกษตรอัจฉริยะ", "รถไถนา", "เครื่องเกี่ยวข้าว"],
    },
    "ครุภัณฑ์การแพทย์": {
        "en": "Medical",
        "sitem_names": ["ครุภัณฑ์การแพทย์", "ครุภัณฑ์นวัตกรรมไทย-ด้านการแพทย์"],
        "keywords": ["เครื่องวัดความดัน", "รถเข็น", "หุ่นจำลองฝึกปฏิบัติ", "เครื่องชั่งน้ำหนัก", "AED", "เตียงตรวจ", "เครื่องผลิตและสลายก๊าซโอโซน", "อุปกรณ์การแพทย์"],
    },
    "ครุภัณฑ์การศึกษา": {
        "en": "Education",
        "sitem_names": ["ครุภัณฑ์การศึกษา"],
        "keywords": ["ห้องเรียนอัจฉริยะ", "DLTV", "ห้องปฏิบัติการ", "ชุดปฏิบัติการ", "อุปกรณ์การเรียน", "ชุดครุภัณฑ์ห้องปฏิบัติการ"],
    },
    "ครุภัณฑ์โฆษณาและเผยแพร่": {
        "en": "Advertising",
        "sitem_names": ["ครุภัณฑ์โฆษณาและเผยแพร่"],
        "keywords": ["โทรทัศน์", "LED TV", "จอแสดงผล", "กล้องถ่ายภาพ", "กล้องวิดีโอ", "เครื่องเสียง", "ไมโครโฟน", "โปรเจคเตอร์"],
    },
    "ครุภัณฑ์งานบ้านงานครัว": {
        "en": "Household",
        "sitem_names": ["ครุภัณฑ์งานบ้านงานครัว"],
        "keywords": ["ตู้เย็น", "เตาแก๊ส", "เครื่องซักผ้า", "เครื่องอบผ้า", "หม้อหุงข้าว", "ไมโครเวฟ", "เครื่องดูดฝุ่น"],
    },
    "ครุภัณฑ์ไฟฟ้าและวิทยุ": {
        "en": "Electrical & Radio",
        "sitem_names": ["ครุภัณฑ์ไฟฟ้าและวิทยุ", "ครุภัณฑ์นวัตกรรมไทย-ด้านไฟฟ้า อิเล็กทรอนิกส์ และโทรคมนาคม"],
        "keywords": ["เครื่องปรับอากาศ", "เครื่องกำเนิดไฟฟ้า", "โคมไฟ", "ไฟถนน", "แอลอีดี", "LED", "เครื่องสูบน้ำ", "ระบบไฟฟ้า", "เครื่องสำรองไฟฟ้า", "วิทยุสื่อสาร", "เครื่องรับส่งวิทยุ"],
    },
    "ครุภัณฑ์ยานพาหนะและขนส่ง": {
        "en": "Vehicles & Transport",
        "sitem_names": ["ครุภัณฑ์ยานพาหนะและขนส่ง", "ครุภัณฑ์นวัตกรรมไทย-ด้านยานพาหนะและขนส่ง"],
        "keywords": ["รถยนต์", "รถจักรยานยนต์", "รถตรวจการณ์", "รถนั่งส่วนกลาง", "รถบรรทุก", "รถเกราะ", "เรือ", "เรือตรวจการณ์"],
    },
    "ครุภัณฑ์โรงงาน": {
        "en": "Factory",
        "sitem_names": ["ครุภัณฑ์โรงงาน"],
        "keywords": ["เครื่องกลึง", "เครื่องเชื่อม", "เครื่องตัด", "เครื่องมือกล", "อุปกรณ์โรงงาน", "แม่แรง"],
    },
    "ครุภัณฑ์สำนักงาน": {
        "en": "Office",
        "sitem_names": ["ครุภัณฑ์สำนักงาน"],
        "keywords": ["โต๊ะ", "เก้าอี้", "ชั้นเหล็ก", "ชั้นไม้", "ตู้เก็บเอกสาร", "เครื่องทำลายเอกสาร", "เครื่องฟอกอากาศ", "ป้าย"],
    },
    "ครุภัณฑ์สำรวจ": {
        "en": "Survey",
        "sitem_names": ["ครุภัณฑ์สำรวจ", "ครุภัณฑ์สนาม"],
        "keywords": ["กล้องสำรวจ", "เครื่องวัดระยะ", "GPS", "อุปกรณ์สำรวจ", "กล้องระดับ", "เครื่องวัดมุม"],
    },
    "ครุภัณฑ์วิทยาศาสตร์": {
        "en": "Scientific",
        "sitem_names": ["ครุภัณฑ์วิทยาศาสตร์"],
        "keywords": ["เครื่องมือวิทยาศาสตร์", "เซนเซอร์", "ห้องแล็บ", "นิวเคลียร์", "กล้องจุลทรรศน์", "เครื่องวิเคราะห์"],
    },
}
OTHER_LABEL = "ครุภัณฑ์อื่น ๆ / นอกบัญชี"

# ── NLP classification ────────────────────────────────────────────────────────
_SITEM_MAP = {}
for cat_key, meta in CATEGORIES.items():
    for s in meta["sitem_names"]:
        _SITEM_MAP[s] = cat_key

def fuzzy_match_score(a, b):
    return fuzz.partial_ratio(a, b)

def classify(sitem_name, item_name):
    if pd.notna(sitem_name):
        hit = _SITEM_MAP.get(str(sitem_name).strip())
        if hit:
            return hit

    src = str(item_name).lower() if pd.notna(item_name) else ""

    best_cat = None
    best_score = 0

    # 2. วนทุก category + keyword
    for cat_key, meta in CATEGORIES.items():
        for kw in meta["keywords"]:
            score = fuzzy_match_score(kw.lower(), src)

            if score > best_score:
                best_score = score
                best_cat = cat_key

    # 3. ตั้ง threshold (สำคัญมาก!)
    if best_score >= 70:   # ปรับได้ 60–85
        return best_cat

    return OTHER_LABEL

@st.cache_data
def load_and_classify(file):
    sheets = pd.read_excel(file, sheet_name=None)
    frames = []
    for name, sheet_df in sheets.items():
        sheet_df = sheet_df.copy()
        sheet_df["source_sheet"] = name
        frames.append(sheet_df)
    combined = pd.concat(frames, ignore_index=True)
    combined["category"] = combined.apply(
        lambda r: classify(r.get("sitem_name"), r.get("chk_item_name")), axis=1
    )
    return combined

def aggregate(df):
    agg = (
        df.groupby("category")
        .agg(
            total_budget=("p_total_bud", "sum"),
            record_count=("p_total_bud", "count"),
            avg_budget=("p_total_bud", "mean"),
        )
        .reset_index()
    )
    agg["_sort"] = agg["category"].apply(
        lambda c: list(CATEGORIES.keys()).index(c) if c in CATEGORIES else 99
    )
    agg = agg.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    agg["pct_of_total"] = agg["total_budget"] / agg["total_budget"].sum() * 100
    agg["en"] = agg["category"].map(
        {k: v["en"] for k, v in CATEGORIES.items()}
    ).fillna("Other/Off-list")
    return agg

# ── Page UI ───────────────────────────────────────────────────────────────────
st.title("📊 ครุภัณฑ์ Budget Dashboard")
st.markdown("NLP Equipment Categorization — บัญชีราคามาตรฐานครุภัณฑ์")

uploaded = st.file_uploader("อัปโหลดไฟล์ข้อมูล (.xlsx)", type=["xlsx"])

if uploaded is None:
    st.info("กรุณาอัปโหลดไฟล์ Excel (data.xlsx) เพื่อเริ่มต้น")
    st.stop()

with st.spinner("กำลังโหลดและจำแนกประเภทข้อมูล..."):
    df = load_and_classify(uploaded)
    agg = aggregate(df)

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 ตัวกรอง")
all_cats = agg["category"].tolist()
selected_cats = st.sidebar.multiselect(
    "ประเภทครุภัณฑ์", options=all_cats, default=all_cats
)

budget_types = (
    sorted(df["งบรายจ่าย"].dropna().unique()) if "งบรายจ่าย" in df.columns else []
)
selected_budget = st.sidebar.multiselect(
    "งบรายจ่าย", options=budget_types, default=budget_types
)

# Apply filters
df_f = df[df["category"].isin(selected_cats)]
if selected_budget and "งบรายจ่าย" in df.columns:
    df_f = df_f[df_f["งบรายจ่าย"].isin(selected_budget)]

agg_f = aggregate(df_f)
grand_total = agg_f["total_budget"].sum()
grand_records = agg_f["record_count"].sum()

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.markdown("### สรุปภาพรวม")
c1, c2, c3, c4 = st.columns(4)
c1.metric("ยอดรวมงบประมาณ", f"฿{grand_total:,.0f}")
c2.metric("รายการทั้งหมด", f"{grand_records:,}")
c3.metric("ประเภทครุภัณฑ์", f"{len(agg_f)}")
c4.metric("เฉลี่ยต่อรายการ", f"฿{grand_total/grand_records:,.2f}" if grand_records else "-")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 ตามประเภทครุภัณฑ์", "💰 ตามงบรายจ่าย", "📋 ตาม Source Sheet"])

# Tab 1 ── By category
with tab1:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### ยอดงบประมาณตามประเภท")
        bar_df = agg_f.sort_values("total_budget", ascending=True)
        fig_bar = px.bar(
            bar_df, x="total_budget", y="category", orientation="h",
            text=bar_df["total_budget"].apply(lambda v: f"฿{v/1e9:.1f}B"),
            color="total_budget", color_continuous_scale="Blues",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            height=460, showlegend=False, coloraxis_showscale=False,
            xaxis_title="งบประมาณ (฿)", yaxis_title="",
            margin=dict(l=0, r=60, t=10, b=10),
        )
        fig_bar.update_xaxes(tickformat=",d")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        st.markdown("#### สัดส่วนงบประมาณ")
        fig_pie = px.pie(agg_f, values="total_budget", names="category", hole=0.4)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            height=460, showlegend=False, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("#### ตารางรายละเอียด")
    tbl = agg_f[["category", "en", "total_budget", "record_count", "avg_budget", "pct_of_total"]].copy()
    tbl.columns = ["ประเภทครุภัณฑ์", "EN", "ยอดรวม (฿)", "รายการ", "เฉลี่ย (฿)", "%"]
    tbl["ยอดรวม (฿)"] = tbl["ยอดรวม (฿)"].apply(lambda v: f"{v:,.0f}")
    tbl["รายการ"] = tbl["รายการ"].apply(lambda v: f"{v:,}")
    tbl["เฉลี่ย (฿)"] = tbl["เฉลี่ย (฿)"].apply(lambda v: f"{v:,.0f}")
    tbl["%"] = tbl["%"].apply(lambda v: f"{v:.1f}%")
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# Tab 2 ── By budget type
with tab2:
    if "งบรายจ่าย" not in df.columns:
        st.warning("ไม่พบคอลัมน์ 'งบรายจ่าย' ในข้อมูล")
    else:
        cross = (
            df_f.groupby(["category", "งบรายจ่าย"])["p_total_bud"]
            .sum().reset_index()
        )
        cross["en"] = cross["category"].map(
            {k: v["en"] for k, v in CATEGORIES.items()}
        ).fillna("Other/Off-list")

        st.markdown("#### งบรายจ่ายแยกตามประเภทครุภัณฑ์")
        fig_stack = px.bar(
            cross, x="p_total_bud", y="category", color="งบรายจ่าย",
            orientation="h", barmode="stack",
        )
        fig_stack.update_layout(
            height=500, xaxis_title="งบประมาณ (฿)", yaxis_title="",
            legend_title="งบรายจ่าย", margin=dict(l=0, r=10, t=10, b=10),
        )
        fig_bar.update_xaxes(tickformat=",d")
        st.plotly_chart(fig_stack, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### สัดส่วนงบรายจ่าย")
            bsum = df_f.groupby("งบรายจ่าย")["p_total_bud"].sum().reset_index()
            fig_bp = px.pie(bsum, values="p_total_bud", names="งบรายจ่าย", hole=0.4)
            fig_bp.update_traces(textinfo="percent+label")
            fig_bp.update_layout(height=340, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bp, use_container_width=True)

        with col_b:
            st.markdown("#### ยอดรวมงบรายจ่าย")
            st.dataframe(
                bsum.rename(columns={"งบรายจ่าย": "ประเภทงบ", "p_total_bud": "ยอดรวม (฿)"})
                .assign(**{"ยอดรวม (฿)": bsum["p_total_bud"].apply(lambda v: f"{v:,.0f}")}),
                use_container_width=True, hide_index=True,
            )

        st.markdown("#### ตาราง Cross-tab")
        pivot = (
            df_f.groupby(["ประเภทครุภัณฑ์", "งบรายจ่าย"])["p_total_bud"]
            .sum().unstack(fill_value=0)
        )
        pivot["รวม"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("รวม", ascending=False)
        st.dataframe(pivot.applymap(lambda v: f"{v:,.0f}"), use_container_width=True)

# Tab 3 ── By source sheet
with tab3:
    sheet_agg = (
        df_f.groupby("source_sheet")
        .agg(total_budget=("p_total_bud", "sum"), records=("p_total_bud", "count"))
        .sort_values("total_budget", ascending=False).reset_index()
    )
    sheet_agg["pct"] = sheet_agg["total_budget"] / sheet_agg["total_budget"].sum() * 100

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### งบประมาณตาม Source Sheet")
        fig_sh = px.bar(
            sheet_agg, x="source_sheet", y="total_budget",
            text=sheet_agg["total_budget"].apply(lambda v: f"฿{v/1e9:.1f}B"),
            color="total_budget", color_continuous_scale="Teal",
        )
        fig_sh.update_traces(textposition="outside")
        fig_sh.update_layout(
            height=380, showlegend=False, coloraxis_showscale=False,
            xaxis_title="", yaxis_title="งบประมาณ (฿)",
            margin=dict(l=0, r=10, t=10, b=10),
        )
        fig_sh.update_xaxes(tickangle=30)
        fig_sh.update_yaxes(tickformat=",d")
        st.plotly_chart(fig_sh, use_container_width=True)

    with col_b:
        st.markdown("#### สัดส่วนรายการตาม Source Sheet")
        fig_sp = px.pie(sheet_agg, values="records", names="source_sheet", hole=0.4)
        fig_sp.update_traces(textinfo="percent+label")
        fig_sp.update_layout(height=380, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_sp, use_container_width=True)

    st.markdown("#### ตาราง Source Sheet")
    sd = sheet_agg.copy()
    sd.columns = ["Source Sheet", "ยอดรวม (฿)", "รายการ", "%"]
    sd["ยอดรวม (฿)"] = sd["ยอดรวม (฿)"].apply(lambda v: f"{v:,.0f}")
    sd["รายการ"] = sd["รายการ"].apply(lambda v: f"{v:,}")
    sd["%"] = sd["%"].apply(lambda v: f"{v:.1f}%")
    st.dataframe(sd, use_container_width=True, hide_index=True)
    
    st.markdown("### 🔝 Top 50 รายการงบสูงสุดต่อ Source Sheet")

    # เลือก sheet
    selected_sheet = st.selectbox(
        "เลือก Source Sheet",
        options=sorted(df_f["source_sheet"].unique())
    )

    # filter ตาม sheet
    df_sheet = df_f[df_f["source_sheet"] == selected_sheet]

    # เลือกคอลัมน์ชื่อ item (กันพัง)
    item_col = "chk_item_name" if "chk_item_name" in df_sheet.columns else df_sheet.columns[0]

    # group + sum
    top_items = (
        df_sheet.groupby(item_col)["p_total_bud"]
        .sum()
        .reset_index()
        .sort_values("p_total_bud", ascending=False)
        .head(50)
    )

    top_items.columns = ["รายการครุภัณฑ์", "งบประมาณ (฿)"]
    top_items["งบประมาณ (฿)"] = top_items["งบประมาณ (฿)"].apply(lambda v: f"{v:,.0f}")

    st.dataframe(top_items, use_container_width=True, hide_index=True)

st.divider()
st.caption("NLP Equipment Categorization Dashboard • Built with Streamlit + Plotly -- By Gul")