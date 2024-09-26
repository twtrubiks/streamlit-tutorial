import streamlit as st

# 買賣差獲利價錢
#
# 如果當沖證交稅0.15%

Handling_Fee = 2.5 / 10 * 0.1425 / 100
Certificate_Tax = 0.3 / 100               # 非當沖
day_trade_Certificate_Tax = 0.3 / 2 / 100 # 當沖

def stock_fee(stock_type, day_trade, stock_price_per, stock_num):
    stock_price = stock_price_per * stock_num
    stock_handling_fee = round(stock_price * Handling_Fee)
    st.write(f'券商手續費: ${stock_handling_fee}')
    if stock_type == 'buy':
        total = int(stock_price + stock_handling_fee)
        st.write(f'買入總價格: ${total}')
    elif stock_type == 'sell':
        if not day_trade:
            # 非當沖
            stock_tax = round(stock_price * Certificate_Tax)
            st.write(f'非當沖證交稅: ${stock_tax}')
            total = int(stock_price - stock_handling_fee - stock_tax)
            st.write(f'非當沖賣出總價格: ${total}')
        else:
            # 當沖
            day_trade_stock_tax = round(stock_price * day_trade_Certificate_Tax)
            st.write(f'當沖證交稅: ${day_trade_stock_tax}')
            total = int(stock_price - stock_handling_fee - day_trade_stock_tax)
            st.write(f'當沖賣出總價格: ${total}')
    else:
        raise Exception('Error stock_type', stock_type)
    st.write('======================')
    return total

st.title("韭菜計算機 :sunglasses:")
st.subheader("手續費0.1425% 證交稅0.3% 如果當沖證交稅0.15%", divider=True)

buy_stock_price = st.number_input(
    "買入價格", value=100, placeholder="100..."
)

sell_stock_price = st.number_input(
    "賣出價格", value=120, placeholder="120..."
)

num = st.number_input(
    "張數", value=1, placeholder="1..."
)

handling = st.number_input(
    "券商折數", value=2.5, placeholder="2.5...(折)"
)
if handling:
    Handling_Fee = handling / 10 * 0.1425 / 100

IS_DAY_TRADE = st.checkbox("是否當沖")

if st.button("開始計算", type="primary"):
    stock_num = num * 1000
    buy_stock_num = stock_num
    sell_stock_num = stock_num

    st.write(f'買入: ${buy_stock_price}')
    buy_total = stock_fee('buy', False, buy_stock_price, buy_stock_num)

    st.write(f'賣出: ${buy_stock_price}')
    sell_total = stock_fee('sell', IS_DAY_TRADE, sell_stock_price, sell_stock_num)

    if buy_stock_price == 0:
        st.write(f'收回: ${sell_total}')
    elif sell_stock_price == 0:
        st.write(f'花費: ${buy_total}')
    else:
        profit = sell_total - buy_total
        st.write(f'獲利: ${profit}')
        st.write(f'獲利率: {profit / buy_total:.3%}')