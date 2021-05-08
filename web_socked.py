from binance.websockets import BinanceSocketManager as websocket
import json
from turtle import *
import time




t = Turtle()
t.screen.setup(800, 550)
t.screen.bgcolor("#002137")
t.color('yellow')
b = 1


def on_message(ws, message):
    obj = json.loads(message)
    print(obj["s"], obj["p"])
    price = float(obj["p"])
    print(price)
    t.clear()
    t.color('yellow')
    t.goto(-400, 130)
    t.write((price), font=("Arial", 100, "bold"))
    t.color('yellow')
    t.goto(-400, 20)
    t.write(('BINANCE BTC USDT'), font=("Arial", 50, "bold"))
    time.sleep(1)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("### connected ###")

if __name__ == "__main__":
    # ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream?streams=ltcbtc@aggTrade/ethbtc@aggTrade",
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@aggTrade",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
"""
    t.clear()
    t.color('yellow')
    t.goto(-400,130)
    t.write((price),font=("Arial", 100, "bold"))
    t.color('yellow')
    t.goto(-400,20)
    t.write(('BINANCE SPOT Account'),font=("Arial", 50, "bold"))
"""
ws.on_open = on_open
ws.run_forever()