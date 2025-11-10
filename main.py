import os
import json
from fastapi import FastAPI, Request, HTTPException
import oandapyV20
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.contrib.requests import MarketOrderRequest

app = FastAPI()

OANDA_TOKEN       = os.getenv("OANDA_TOKEN")
OANDA_ACCOUNT_ID  = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ENV         = "practice"
TRADINGVIEW_SECRET = os.getenv("TRADINGVIEW_SECRET")

api = oandapyV20.API(access_token=OANDA_TOKEN, environment=OANDA_ENV)

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()

    if body.get("secret") != TRADINGVIEW_SECRET:
        raise HTTPException(status_code=403, detail="bad secret")

    action = body.get("action") # BUY / SELL
    symbol = body.get("symbol")
    units  = int(body.get("units", 1000))

    if not action or not symbol:
        raise HTTPException(status_code=400, detail="missing action/symbol")

    signed_units = units if action.upper() == "BUY" else -units

    mktOrder = MarketOrderRequest(instrument=symbol, units=signed_units)
    order = OrderCreate(accountID=OANDA_ACCOUNT_ID, data=mktOrder.data)

    try:
        resp = api.request(order)
        return {"status":"sent","resp":resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
