import io

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from categorize import categorize_statement
from pdf_extract import extract_text

load_dotenv()


def fmt_inr(amount: float) -> str:
    """Compact Indian-currency formatting so metric tiles never truncate."""
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= 1e7:
        return f"{sign}₹{amount / 1e7:.2f}Cr"
    if amount >= 1e5:
        return f"{sign}₹{amount / 1e5:.2f}L"
    if amount >= 1e3:
        return f"{sign}₹{amount / 1e3:.1f}k"
    return f"{sign}₹{amount:.0f}"

st.set_page_config(
    page_title="Bank Statement Spending Analyzer",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Categorical palette (fixed order — validated for CVD safety, see dataviz skill)
PALETTE = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

CUSTOM_CSS = """
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background:
            radial-gradient(ellipse 900px 500px at 20% -10%, rgba(139,108,240,0.20), transparent 60%),
            radial-gradient(ellipse 700px 400px at 100% 0%, rgba(139,108,240,0.12), transparent 55%),
            #0a0a12;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    .hero {
        position: relative;
        background: linear-gradient(180deg, rgba(139,108,240,0.14) 0%, rgba(19,19,31,0.6) 100%);
        border: 1px solid rgba(139,108,240,0.35);
        border-radius: 16px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.75rem;
        color: #f2f0fb;
        overflow: hidden;
    }
    .hero::before {
        content: "";
        position: absolute;
        top: -60%; left: 60%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(139,108,240,0.35), transparent 70%);
        pointer-events: none;
    }
    .hero h1 { margin: 0 0 0.35rem 0; font-size: 1.9rem; color: #f2f0fb; position: relative; }
    .hero p { margin: 0; opacity: 0.75; font-size: 1rem; position: relative; }

    /* eyebrow pill — small uppercase tag above a heading, per inspo */
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid rgba(167,139,250,0.45);
        border-radius: 100px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #c4b5fd;
        background: rgba(139,108,240,0.08);
        margin-bottom: 0.6rem;
    }

    /* corner-bracket card frame, echoing the inspo's dashed-corner panels */
    .bracket-card {
        position: relative;
        border: 1px solid rgba(139,108,240,0.28);
        border-radius: 12px;
        background: rgba(139,108,240,0.05);
    }
    .bracket-card::before, .bracket-card::after,
    div[data-testid="stMetric"]::before, div[data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        width: 10px; height: 10px;
        border-color: #a78bfa;
        pointer-events: none;
    }
    .bracket-card::before, div[data-testid="stMetric"]::before {
        top: -1px; left: -1px;
        border-top: 2px solid #a78bfa;
        border-left: 2px solid #a78bfa;
        border-top-left-radius: 4px;
    }
    .bracket-card::after, div[data-testid="stMetric"]::after {
        bottom: -1px; right: -1px;
        border-bottom: 2px solid #a78bfa;
        border-right: 2px solid #a78bfa;
        border-bottom-right-radius: 4px;
    }

    /* icon-circle badge, per inspo's feature-card icons */
    .icon-circle {
        width: 34px; height: 34px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #7c5cf0 0%, #a78bfa 100%);
        font-size: 0.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.6rem;
    }

    .feature-card {
        padding: 1rem 1.1rem 1.15rem 1.1rem;
        height: 100%;
    }
    .feature-card h4 { margin: 0 0 0.3rem 0; font-size: 0.98rem; color: #f2f0fb; }
    .feature-card p { margin: 0; font-size: 0.85rem; color: #a8a2c4; line-height: 1.4; }

    /* pill tag row, echoing the inspo's bottom capability tags */
    .tag-pill {
        display: inline-block;
        border: 1px solid rgba(139,108,240,0.35);
        border-radius: 8px;
        padding: 0.3rem 0.75rem;
        font-size: 0.78rem;
        color: #cfc9e8;
        background: rgba(139,108,240,0.06);
        margin: 0 0.4rem 0.4rem 0;
    }

    /* inset dark frame for chart containers, per inspo's screenshot frames */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(139,108,240,0.22) !important;
        border-radius: 12px !important;
        background: rgba(0,0,0,0.25);
    }

    div[data-testid="stMetric"] {
        position: relative;
        background: rgba(139,108,240,0.05);
        border: 1px solid rgba(139,108,240,0.28);
        border-radius: 12px;
        padding: 0.9rem 1rem 0.7rem 1rem;
    }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; opacity: 0.7; }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
        overflow: visible;
        white-space: nowrap;
        color: #f2f0fb;
    }

    .upload-card {
        padding: 1.25rem;
        color: #cfc9e8;
    }

    section[data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
        border: 1px dashed rgba(139,108,240,0.4) !important;
        background: rgba(139,108,240,0.04);
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 2.7rem;
        background: linear-gradient(135deg, #7c5cf0 0%, #a78bfa 100%);
        border: none;
        color: white;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #8b6cf0 0%, #b39dfb 100%);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: #0d0d17;
        border-right: 1px solid rgba(139,108,240,0.2);
    }

    div[data-baseweb="tab-list"] { gap: 4px; }
    button[data-baseweb="tab"] { color: #cfc9e8; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #a78bfa; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <span class="eyebrow">◆ AI-POWERED</span>
        <h1>Bank Statement Spending Analyzer</h1>
        <p>Upload a bank statement PDF — AI categorizes every transaction (food,
        subscriptions, transport, shopping, EMIs, UPI transfers) and breaks down your
        spending with charts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None

st.markdown('<span class="eyebrow">⌘ HOW IT WORKS</span>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3, gap="medium")
for col, icon, title, desc in [
    (f1, "01", "Upload", "Drop any HDFC, SBI, Axis, or ICICI netbanking PDF export."),
    (f2, "02", "AI categorizes", "Groq reads every line — food, EMIs, UPI, subscriptions, and more."),
    (f3, "03", "Visualize", "See spend by category and over time, then export to Excel or CSV."),
]:
    col.markdown(
        f"""
        <div class="bracket-card feature-card">
            <div class="icon-circle">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        "**Who this is for**\n\n"
        "Individual consumers who want to understand where their money goes without "
        "manually categorizing every line of a bank statement. Works with HDFC, SBI, "
        "Axis, ICICI, and similar Indian bank statement formats."
    )
    st.markdown("---")
    st.caption(
        "Your statement is analyzed securely and is not stored "
        "by this app beyond the current session."
    )

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.markdown("#### Upload statement")
    uploaded_file = st.file_uploader(
        "Bank statement PDF", type=["pdf"], label_visibility="collapsed"
    )

    if uploaded_file:
        st.caption(uploaded_file.name)
        analyze_clicked = st.button(
            "Analyze statement", type="primary", use_container_width=True
        )

        if analyze_clicked:
            with st.spinner("Reading PDF..."):
                try:
                    text = extract_text(uploaded_file)
                except Exception as exc:
                    st.session_state.error = f"Could not read PDF: {exc}"
                    st.session_state.result = None
                    text = None

            if text is not None:
                if not text.strip():
                    st.session_state.error = (
                        "No text could be extracted from this PDF — it may be a scanned "
                        "image rather than a text-based statement."
                    )
                    st.session_state.result = None
                else:
                    with st.spinner("Categorizing transactions with AI..."):
                        try:
                            st.session_state.result = categorize_statement(text)
                            st.session_state.error = None
                        except Exception as exc:
                            st.session_state.error = f"Analysis failed: {exc}"
                            st.session_state.result = None
    else:
        st.markdown(
            '<div class="upload-card bracket-card">Drop a bank statement PDF above. '
            "Text-based PDF exports work best (most banks let you download one from "
            "netbanking).</div>",
            unsafe_allow_html=True,
        )

with right:
    st.markdown("#### Spending breakdown")

    if st.session_state.error:
        st.error(st.session_state.error)

    result = st.session_state.result

    if not result:
        if not st.session_state.error:
            st.info("Your spending breakdown will appear here.")
    else:
        transactions = result.get("transactions", [])
        df = pd.DataFrame(transactions)

        if df.empty:
            st.warning("No transactions could be extracted from this statement.")
        else:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            debits = df[df["type"] == "debit"]
            credits = df[df["type"] == "credit"]

            total_spent = debits["amount"].sum()
            total_income = credits["amount"].sum()
            net = total_income - total_spent

            if result.get("_truncated"):
                st.warning(
                    "This statement was long, so only the first portion was analyzed. "
                    "Totals below may be incomplete."
                )

            holder = result.get("account_holder")
            period = result.get("statement_period")
            if holder or period:
                st.caption(
                    f"{holder if holder else ''}"
                    f"{'  ·  ' if holder and period else ''}"
                    f"{period if period else ''}"
                )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total spent", fmt_inr(total_spent), help=f"₹{total_spent:,.2f}")
            m2.metric("Total income", fmt_inr(total_income), help=f"₹{total_income:,.2f}")
            m3.metric("Net", fmt_inr(net), help=f"₹{net:,.2f}")
            m4.metric("Transactions", len(df))

            tab_overview, tab_txns, tab_export = st.tabs(
                ["Overview", "Transactions", "Export"]
            )

            with tab_overview:
                if debits.empty:
                    st.info("No debit transactions found to break down.")
                else:
                    cat_df = (
                        debits.groupby("category")["amount"]
                        .sum()
                        .reset_index()
                        .sort_values("amount", ascending=False)
                    )
                    cat_df.columns = ["Category", "Amount"]

                    pills = "".join(
                        f'<span class="tag-pill">{cat}</span>' for cat in cat_df["Category"]
                    )
                    st.markdown(pills, unsafe_allow_html=True)

                    with st.container(border=True):
                        st.markdown("**Spending by category**")
                        colors = (PALETTE * ((len(cat_df) // len(PALETTE)) + 1))[: len(cat_df)]
                        bar = (
                            alt.Chart(cat_df)
                            .mark_bar(cornerRadiusEnd=4)
                            .encode(
                                x=alt.X("Amount:Q", title="Total spent (₹)"),
                                y=alt.Y("Category:N", sort="-x", title=None),
                                color=alt.Color(
                                    "Category:N",
                                    scale=alt.Scale(domain=list(cat_df["Category"]), range=colors),
                                    legend=None,
                                ),
                                tooltip=[
                                    alt.Tooltip("Category:N"),
                                    alt.Tooltip("Amount:Q", format=",.0f", title="Amount (₹)"),
                                ],
                            )
                            .properties(height=max(220, 32 * len(cat_df)))
                        )
                        st.altair_chart(bar, use_container_width=True)

                    try:
                        dates = pd.to_datetime(debits["date"], errors="coerce")
                        monthly = debits.assign(_month=dates.dt.to_period("M").astype(str))
                        monthly_sum = (
                            monthly.dropna(subset=["_month"])
                            .groupby("_month")["amount"]
                            .sum()
                            .reset_index()
                        )
                        monthly_sum.columns = ["Month", "Amount"]
                    except Exception:
                        monthly_sum = pd.DataFrame()

                    if len(monthly_sum) > 1:
                        st.markdown("**Spending over time**")
                        line = (
                            alt.Chart(monthly_sum)
                            .mark_line(
                                point=alt.OverlayMarkDef(size=80, color=PALETTE[0]),
                                color=PALETTE[0],
                                strokeWidth=2,
                            )
                            .encode(
                                x=alt.X("Month:N", title=None),
                                y=alt.Y("Amount:Q", title="Total spend (₹)"),
                                tooltip=[
                                    alt.Tooltip("Month:N"),
                                    alt.Tooltip("Amount:Q", format=",.0f", title="Amount (₹)"),
                                ],
                            )
                            .properties(height=250)
                        )
                        st.altair_chart(line, use_container_width=True)

                    st.markdown("**Category totals**")
                    st.dataframe(
                        cat_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Amount": st.column_config.NumberColumn(format="₹%.0f"),
                        },
                    )

            with tab_txns:
                display_df = df.rename(
                    columns={
                        "date": "Date",
                        "description": "Description",
                        "amount": "Amount",
                        "type": "Type",
                        "category": "Category",
                    }
                )[["Date", "Description", "Amount", "Type", "Category"]]

                categories_present = sorted(display_df["Category"].dropna().unique())
                selected_categories = st.multiselect(
                    "Filter by category", categories_present, default=[]
                )
                filtered = (
                    display_df[display_df["Category"].isin(selected_categories)]
                    if selected_categories
                    else display_df
                )

                st.dataframe(
                    filtered.sort_values("Date"),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.TextColumn(width="small"),
                        "Description": st.column_config.TextColumn(width="large"),
                        "Amount": st.column_config.NumberColumn(format="₹%.2f", width="small"),
                        "Type": st.column_config.TextColumn(width="small"),
                        "Category": st.column_config.TextColumn(width="medium"),
                    },
                )

            with tab_export:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    display_df.to_excel(writer, index=False, sheet_name="Transactions")
                    if not debits.empty:
                        cat_df.to_excel(writer, index=False, sheet_name="Category Summary")
                excel_buffer.seek(0)

                c1, c2 = st.columns(2)
                c1.download_button(
                    "Download as Excel",
                    excel_buffer,
                    file_name="spending_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    icon=":material/download:",
                    use_container_width=True,
                )
                c2.download_button(
                    "Download as CSV",
                    display_df.to_csv(index=False).encode("utf-8"),
                    file_name="spending_analysis.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    use_container_width=True,
                )
