import requests
import json






class StockMarket:
    """This implements a game of Connect4"""
    def __init__(self, state=None, players=None):
        #Game Constants
        self.startValue = 10**6
        self.interval = 15

        if state:
            self.state = state
        else:
            self.state = {
                "endDate": "endDate",
                "symbols": ["FB"],#,"AMZN","AAPL","NFLX","GOOGL"],
                "data":{},
                "players": players,
                "portfolios":{}
            }

            for s in self.state["symbols"]:
                self.state["data"][s] = {
                    "all":{},
                    "last":{}
                }

            for p in players:
                self.state["portfolios"][p.id] = {
                    "cash":self.startValue,
                    "stocks":{},
                    "trades":[]
                }

    def print(self):
        print("---------------")
        for id, port in self.state["portfolios"].items():
            print(id)
            print(port['cash'])
            print(port['stocks'])
        print("---------------")

    def gatherStockData(self):
        for sym in self.state["symbols"]:
            data, last = self.getStockData(sym, str(self.interval)+"min")
            for date, value in data.items():
                self.state["data"][sym]["all"][date] = value
            self.state["data"][sym]["last"] = data[last]
            print(self.state["data"][sym])

    def getStockData(self, symbol, interval):
        payload = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": APIKey
        }

        r = requests.get("https://www.alphavantage.co/query", payload)
        if r.status_code == 200:
            data = json.loads(r.content.decode())
            last = data["Meta Data"]["3. Last Refreshed"]
            return data["Time Series (" + interval + ")"], last
        else:
            print("An error occured:", r.status_code, r.content)

    def validateMove(self, move):
        portfolio = self.state['portfolios'][move['aid']]
        for trade in move['trades']:
            if not self.validateTrade(trade,portfolio):
                return False
        return True

    def validateTrade(self, trade, portfolio):
        if trade["symbol"] in self.state["symbols"]:
            if trade["action"] == "buy":
                cost = trade["quantity"] * self.state["stocks"][trade["symbol"]]["cost"]
                if cost < portfolio['cash']:
                    return True
            elif trade["action"] == "sell":
                if trade["symbol"] in portfolio["stocks"] and trade["quantity"] <= portfolio["stocks"]["quantity"]:
                    return True
        return False

    def makeMove(self, move):#assumes move has been validated
        pass


    def postMove(self):
        pass

    def endGame(self, winner):
        #print("Winner", winner)
        #print(self.state["players"][winner])
        self.state["Winner"] = winner



if __name__ == "__main__":
    sm = StockMarket(players=[])
    sm.gatherStockData()