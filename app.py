import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="纳指100投资观察站",
    page_icon="📈",
    layout="centered"
)

st.title("📈 纳指100投资观察站")
st.caption("市场观察工具 · 不构成投资建议")

@st.cache_data(ttl=900)
def get_data(period):
    data = yf.download(
        "^NDX",
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False
    )
    return data.dropna()

period_options = {
    "1个月": "1mo",
    "3个月": "3mo",
    "6个月": "6mo",
    "1年": "1y",
    "5年": "5y"
}

period_name = st.radio(
    "查看走势",
    list(period_options.keys()),
    horizontal=True
)

with st.spinner("正在获取最新行情…"):
    data = get_data(period_options[period_name])

if data.empty:
    st.error("暂时无法获取行情，请稍后重试。")
    st.stop()

close = data["Close"]

if hasattr(close, "columns"):
    close = close.iloc[:, 0]

close = close.dropna()

if len(close) < 2:
    st.warning("目前可用行情数据不足。")
    st.stop()

latest = float(close.iloc[-1])
previous = float(close.iloc[-2])
day_change = (latest / previous - 1) * 100

def pct_change_n(series, days):
    if len(series) <= days:
        return None
    return (float(series.iloc[-1]) / float(series.iloc[-1-days]) - 1) * 100

week_change = pct_change_n(close, 5)
month_change = pct_change_n(close, 21)

date_text = close.index[-1].strftime("%Y-%m-%d")

st.subheader("最新行情")
st.metric("纳指100指数", f"{latest:,.2f}", f"{day_change:+.2f}%")

col1, col2 = st.columns(2)

with col1:
    if week_change is not None:
        st.metric("近5个交易日", f"{week_change:+.2f}%")
    else:
        st.metric("近5个交易日", "数据不足")

with col2:
    if month_change is not None:
        st.metric("近1个月（约21个交易日）", f"{month_change:+.2f}%")
    else:
        st.metric("近1个月", "数据不足")

st.caption(f"最近一个数据日期：{date_text}")
st.caption("数据来源：Yahoo Finance（通过 yfinance 获取）")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=close.index,
    y=close.values,
    mode="lines",
    name="纳指100"
))

fig.update_layout(
    title=f"纳指100 · {period_name}走势",
    xaxis_title="日期",
    yaxis_title="指数点位",
    height=380,
    margin=dict(l=10, r=10, t=55, b=10),
    showlegend=False
)

fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1月", step="month", stepmode="backward"),
            dict(count=3, label="3月", step="month", stepmode="backward"),
            dict(count=1, label="1年", step="year", stepmode="backward"),
            dict(step="all", label="全部")
        ]
    )
)

st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("风险观察")

if day_change <= -2:
    st.warning("指数单日跌幅较大，建议关注波动与自身风险承受能力。")
elif day_change >= 2:
    st.warning("指数单日涨幅较大，注意市场波动，不要只根据单日表现决策。")
else:
    st.info("单日涨跌幅未达到本工具设定的明显波动提示阈值。")

st.caption(
    "本页面用于辅助观察市场，不预测未来涨跌，也不自动生成买卖指令。"
)
st.caption(f"页面生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")