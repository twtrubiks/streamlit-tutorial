import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="韭菜計算機", page_icon="🌱", layout="centered")

# 買賣差獲利價錢 (費率預設為台股法定值, 可在「進階設定」自訂)
# 手續費 0.1425% / 證交稅 0.3% / 當沖證交稅減半 0.15%
# 以下三個費率變數會在主流程依使用者輸入重新計算
Handling_Fee = 2.5 / 10 * 0.1425 / 100
Certificate_Tax = 0.3 / 100               # 非當沖
day_trade_Certificate_Tax = 0.3 / 2 / 100 # 當沖


def calc_buy(price_per, shares, rate):
    """買入: 回傳成交金額、手續費、總成本 (純計算, 不負責畫面)"""
    gross = price_per * shares
    fee = round(gross * rate)
    return {"gross": gross, "fee": fee, "total": int(gross + fee)}


def calc_sell(price_per, shares, rate, day_trade):
    """賣出: 回傳成交金額、手續費、證交稅、淨收 (當沖證交稅減半)"""
    gross = price_per * shares
    fee = round(gross * rate)
    tax_rate = day_trade_Certificate_Tax if day_trade else Certificate_Tax
    tax = round(gross * tax_rate)
    return {"gross": gross, "fee": fee, "tax": tax, "net": int(gross - fee - tax)}


def money(n):
    """金額格式化, 負數顯示為 -$xxx"""
    return f"-${abs(n):,.0f}" if n < 0 else f"${n:,.0f}"


def qp_get(key, default, cast):
    """從網址參數讀值 (可分享連結), 失敗則回傳預設"""
    try:
        return cast(st.query_params[key])
    except (KeyError, TypeError, ValueError):
        return default


st.title("韭菜計算機 :sunglasses:")
st.subheader("手續費0.1425% 證交稅0.3% 如果當沖證交稅0.15%", divider=True)

buy_stock_price = st.number_input(
    "買入價格", value=qp_get("buy", 100.00, float), placeholder="100.00...",
    format="%.2f", step=0.01,
)

sell_stock_price = st.number_input(
    "賣出價格", value=qp_get("sell", 120.00, float), placeholder="120.00...",
    format="%.2f", step=0.01,
)

# 交易單位: 張 (1張=1000股) 或 股 (零股)
unit_default = qp_get("unit", "張", str)
if unit_default not in ("張", "股"):
    unit_default = "張"
unit = st.segmented_control(
    "交易單位", ["張", "股"], default=unit_default, required=True,
    help="零股請選「股」，一張 = 1000 股",
)
is_odd_lot = unit == "股"
qty = st.number_input(
    "股數（零股）" if is_odd_lot else "張數",
    min_value=1, value=max(1, qp_get("qty", 1, int)), step=1, key="qty_input",
)
shares = qty if is_odd_lot else qty * 1000
st.caption(f"= {shares:,} 股")

handling = st.number_input(
    "券商折數", value=qp_get("handling", 2.50, float), placeholder="2.50...(折)",
    format="%.2f", step=0.01,
)

mode_default = qp_get("mode", "現股", str)
if mode_default not in ("現股", "當沖"):
    mode_default = "現股"
trade_mode = st.segmented_control(
    "交易類別", ["現股", "當沖"], default=mode_default, required=True,
)
IS_DAY_TRADE = trade_mode == "當沖"
st.badge(
    "當沖 · 證交稅減半" if IS_DAY_TRADE else "現股 · 非當沖",
    icon="⚡" if IS_DAY_TRADE else "📈",
    color="orange" if IS_DAY_TRADE else "blue",
)

# 進階設定: 自訂費率 (預設為台股法定費率); expander type="compact" 為較精簡樣式
with st.expander("進階設定（費率）", icon="⚙️", type="compact"):
    fee_rate_pct = st.number_input(
        "券商手續費率 (%)", value=qp_get("fee_rate", 0.1425, float),
        min_value=0.0, step=0.0001, format="%.4f",
        help="台股法定上限 0.1425%，實際再乘上券商折數",
    )
    tax_rate_pct = st.number_input(
        "證交稅率 (%)", value=qp_get("tax_rate", 0.3, float),
        min_value=0.0, step=0.01, format="%.2f",
        help="現股 0.3%，當沖自動減半",
    )

# 由折數與費率算出實際費率 (當沖證交稅減半); 覆寫前面的預設值
Handling_Fee = (handling / 10 if handling else 1) * fee_rate_pct / 100
Certificate_Tax = tax_rate_pct / 100
day_trade_Certificate_Tax = tax_rate_pct / 2 / 100

# 把目前輸入同步到網址, 算完可直接複製連結分享
st.query_params.update(
    {
        "buy": str(buy_stock_price),
        "sell": str(sell_stock_price),
        "qty": str(qty),
        "unit": unit,
        "handling": str(handling),
        "mode": trade_mode,
        "fee_rate": str(fee_rate_pct),
        "tax_rate": str(tax_rate_pct),
    }
)

if st.button("開始計算", type="primary"):
    buy = calc_buy(buy_stock_price, shares, Handling_Fee)
    sell = calc_sell(sell_stock_price, shares, Handling_Fee, IS_DAY_TRADE)
    profit = sell["net"] - buy["total"]
    profit_rate = profit / buy["total"] if buy["total"] else 0

    # 損益兩平賣價 (近似值, 忽略整數進位): 賣到這個價格才回本
    tax_rate = day_trade_Certificate_Tax if IS_DAY_TRADE else Certificate_Tax
    break_even = buy["total"] / (shares * (1 - Handling_Fee - tax_rate)) if shares else 0

    # 掃描賣價算出「賣價 -> 獲利」曲線; 範圍涵蓋 買價/賣價/兩平點, 三者都會在圖內
    refs = [buy_stock_price, sell_stock_price, break_even]
    lo, hi = min(refs) * 0.9, max(refs) * 1.1
    if hi <= lo:
        hi = lo + 1
    prices = [round(lo + (hi - lo) / 40 * i, 2) for i in range(41)]
    curve = pd.DataFrame({"price": prices})
    curve["profit"] = [
        calc_sell(p, shares, Handling_Fee, IS_DAY_TRADE)["net"] - buy["total"]
        for p in prices
    ]

    # 結果卡片: 三欄 metric, 獲利欄用 delta 自動紅綠配色 + sparkline 走勢
    c1, c2, c3 = st.columns(3)
    c1.metric("買入總成本", f"${buy['total']:,}", border=True)
    c2.metric("賣出淨收", f"${sell['net']:,}", border=True)
    c3.metric(
        "獲利", f"${profit:,}", delta=f"{profit_rate:.2%}", border=True,
        chart_data=curve["profit"], chart_type="line",
    )

    # 結果橫幅: 用帶 title 的 alert (1.57) 醒目呈現賺賠, 標題放金額、內文放報酬率
    if profit >= 0:
        st.success(f"報酬率 {profit_rate:+.2%}", icon="🟢", title=f"獲利 {money(profit)}")
    else:
        st.error(f"報酬率 {profit_rate:+.2%}", icon="🔴", title=f"虧損 {money(profit)}")

    # 費用明細表 (st.table 在 1.55 起支援 hide_index)
    # 費用一律顯示正數金額; 只有「淨損益」會隨虧損顯示負號
    breakdown = pd.DataFrame(
        [
            {"項目": "買入成交金額", "金額": money(buy["gross"])},
            {"項目": "買入手續費", "金額": money(buy["fee"])},
            {"項目": "賣出成交金額", "金額": money(sell["gross"])},
            {"項目": "賣出手續費", "金額": money(sell["fee"])},
            {"項目": f"證交稅（{'當沖' if IS_DAY_TRADE else '非當沖'}）", "金額": money(sell["tax"])},
            {"項目": "淨損益", "金額": money(profit)},
        ]
    )
    st.table(breakdown, hide_index=True)

    st.caption(f"📉 損益兩平賣價約 ${break_even:,.2f}（賣到這個價格才不賠錢）")

    # ----- 損益視覺化 (Altair): 賺/賠上色 + Y=0 基準線 + 兩平點 + 你的賣價 -----
    # (1)+(4) 賺錢區綠、賠錢區紅 (以 0 為基準的面積圖, 線寬 2)
    area = (
        alt.Chart(curve)
        .transform_calculate(status="datum.profit >= 0 ? '獲利' : '虧損'")
        .mark_area(opacity=0.2, line={"strokeWidth": 2})
        .encode(
            x=alt.X("price:Q", title="賣出價格", scale=alt.Scale(zero=False)),
            y=alt.Y("profit:Q", title="獲利"),
            color=alt.Color(
                "status:N",
                scale=alt.Scale(domain=["獲利", "虧損"], range=["#16a34a", "#dc2626"]),
                legend=None,
            ),
        )
    )

    # (1) Y=0 紅色虛線: 賺賠分界
    zero_line = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(color="#dc2626", strokeDash=[6, 4], strokeWidth=1.5)
        .encode(y="y:Q")
    )

    # (2) 損益兩平點 + 標籤
    be = pd.DataFrame(
        {"price": [round(break_even, 2)], "profit": [0], "label": [f"兩平 ${break_even:,.2f}"]}
    )
    be_point = alt.Chart(be).mark_point(color="#dc2626", size=90, filled=True).encode(
        x="price:Q", y="profit:Q"
    )
    be_text = alt.Chart(be).mark_text(dy=-12, color="#dc2626", fontWeight="bold").encode(
        x="price:Q", y="profit:Q", text="label:N"
    )

    # (3) 你實際輸入的賣價那一點 + 標籤
    you = pd.DataFrame(
        {"price": [sell_stock_price], "profit": [profit], "label": [f"你的賣價 ${sell_stock_price:,.2f}"]}
    )
    you_point = alt.Chart(you).mark_point(
        color="#2563eb", size=120, filled=True, shape="diamond"
    ).encode(x="price:Q", y="profit:Q")
    you_text = alt.Chart(you).mark_text(dy=-14, color="#2563eb", fontWeight="bold").encode(
        x="price:Q", y="profit:Q", text="label:N"
    )

    chart = (area + zero_line + be_point + be_text + you_point + you_text).properties(
        height=320
    )
    st.altair_chart(chart, width="stretch")