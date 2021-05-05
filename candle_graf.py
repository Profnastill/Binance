import plotly.graph_objects as go
import stocker
import time
import dash
from find_sharp_sortino import take_data_candle, ask_input

# from stocker import
stiker = stocker.predict.tomorrow('AAPL')

print(stiker)


def grapf(asset, day_interval):
    """Функция построения графиков для необходимых инструментов"""
    candel_tb = take_data_candle(asset, day_interval)

    fig = go.Figure(data=[go.Candlestick(x=candel_tb['Open time'],
                                         open=candel_tb['Open'],
                                         high=candel_tb['High'],
                                         low=candel_tb['Low'],
                                         close=candel_tb['Close'])])
    fig.update_layout(title=asset, yaxis_title='price')

    fig.show()
    time.sleep(20)

if __name__ == '__main__':
    table = ask_input()
    table.apply(lambda x: grapf(x.asset, 120), axis=1)

    # table.apply(lambda x:take_data_candle(x.asset,10),axis=1)
