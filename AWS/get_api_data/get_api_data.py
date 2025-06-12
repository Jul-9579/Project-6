import os
import json
import requests
from datetime import datetime

ALPHA_APIKEY = os.getenv("ALPHA_APIKEY")
ALPHA_ENDPOINT = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey={ALPHA_APIKEY}"

def lambda_handler(event, context):
    try:
        response = requests.get(ALPHA_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        ts = data.get("Time Series (Digital Currency Daily)")
        if not ts:
            return {"statusCode": 500, "body": json.dumps({"error": "Time Series data missing"})}

        today = datetime.utcnow().strftime("%Y-%m-%d")
        today_data = ts.get(today)

        if not today_data:
            return {"statusCode": 404, "body": json.dumps({"error": f"No data for {today}"})}

        return {
            "statusCode": 200,
            "body": json.dumps(today_data)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

