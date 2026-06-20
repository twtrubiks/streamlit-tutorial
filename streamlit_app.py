import streamlit as st

st.set_page_config(page_title="韭菜計算機", page_icon="🌱", layout="centered")

# 買賣差獲利價錢
#
# 如果當沖證交稅0.15%

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

st.title("韭菜計算機 :sunglasses:")
st.subheader("手續費0.1425% 證交稅0.3% 如果當沖證交稅0.15%", divider=True)

buy_stock_price = st.number_input(
    "買入價格", value=100.00, placeholder="100.00...",
    format="%.2f", step=0.01,
)

sell_stock_price = st.number_input(
    "賣出價格", value=120.00, placeholder="120.00...",
    format="%.2f", step=0.01,
)

num = st.number_input(
    "張數", value=1, placeholder="1..."
)

handling = st.number_input(
    "券商折數", value=2.50, placeholder="2.50...(折)",
    format="%.2f", step=0.01,
)
if handling:
    Handling_Fee = handling / 10 * 0.1425 / 100

trade_mode = st.segmented_control(
    "交易類別", ["現股", "當沖"], default="現股", required=True,
)
IS_DAY_TRADE = trade_mode == "當沖"
st.badge(
    "當沖 · 證交稅減半" if IS_DAY_TRADE else "現股 · 非當沖",
    icon="⚡" if IS_DAY_TRADE else "📈",
    color="orange" if IS_DAY_TRADE else "blue",
)

if st.button("開始計算", type="primary"):
    shares = num * 1000
    buy = calc_buy(buy_stock_price, shares, Handling_Fee)
    sell = calc_sell(sell_stock_price, shares, Handling_Fee, IS_DAY_TRADE)
    profit = sell["net"] - buy["total"]
    profit_rate = profit / buy["total"] if buy["total"] else 0

    # 結果卡片: 三欄 metric, 獲利欄用 delta 自動紅綠配色
    c1, c2, c3 = st.columns(3)
    c1.metric("買入總成本", f"${buy['total']:,}", border=True)
    c2.metric("賣出淨收", f"${sell['net']:,}", border=True)
    c3.metric("獲利", f"${profit:,}", delta=f"{profit_rate:.2%}", border=True)

    st.badge(
        f"獲利 ${profit:,}" if profit >= 0 else f"虧損 ${profit:,}",
        icon="🟢" if profit >= 0 else "🔴",
        color="green" if profit >= 0 else "red",
    )