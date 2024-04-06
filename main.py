import asyncio
import logging
from datetime import datetime, timedelta
import sys
import json

from aiohttp import ClientSession, ClientConnectorError

URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
DATE = datetime.now().date()
CCY = ['USD', 'EUR']

async def request(url, day):
    async with ClientSession() as session:
        try:
            async with session.get(url + day) as response:
                if response.ok:
                    result = await response.json()
                    return result
                logging.error(f"Error status: {response.status} for {url + day}")
                return None
        except ClientConnectorError as e:
            logging.error(f"Connection error: {str(e)}")
            return None

async def get_exchange(date, data, currencys): 
    result_dict = {}
    if data:
        result_dict[date] = {}
        for ccy in data['exchangeRate']:
            if ccy['currency'] in currencys:
                result_dict[date][ccy['currency']] = {
                    'sale': f"{ccy['saleRate']}",
                    'purchase': f"{ccy['purchaseRate']}"
                }
        return result_dict

async def main(days, currencys):
    exchanges = []
    if int(days) in range(1, 11):
        for i in range(int(days)):
            day = DATE - timedelta(days=i)
            day = day.strftime('%d.%m.%Y')
            data = await request(URL, day)
            if data:
                result = await get_exchange(day, data, currencys)
                exchanges.append(result)
        return exchanges
    else:
        return f'Exchange rate available only for the last 10 days'

if __name__ == '__main__':
    days = sys.argv[1]
    if sys.argv[2:]:
        for i in sys.argv[2:]:
            CCY.append(i)
    currencys = CCY
    result = asyncio.run(main(days, currencys))
    print(json.dumps(result, indent=4))
