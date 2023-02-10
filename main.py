import asyncio
import aiohttp
import time


def data_processing(response, response_json):
    if response.status == 200:
        last_price = float(response_json['lastPrice'])
        high_price = float(response_json['highPrice'])
        percent_of_max = round(high_price * 0.01, 6)
        difference = round(high_price - last_price, 6)
        if difference >= percent_of_max:
            print('The price XRP/USDT dropped by 1% of the maximum price in the last hour')
    elif response.status in [418, 429]:
        timeout = int(response.headers['Retry-After'])
        time.sleep(timeout)
        raise Exception()


async def fetch_content(url, session):
    response = await session.get(url)
    response_json = await response.json()
    data_processing(response, response_json)


threshold = 7


async def main():
    global threshold
    url = 'https://api.binance.com/api/v3/ticker?symbol=XRPUSDT&windowSize=1h'
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            for _ in range(threshold):
                task = asyncio.create_task(fetch_content(url, session))
                tasks.append(task)
            try:
                await asyncio.gather(*tasks)
            except Exception:
                for task in tasks:
                    task.cancel()
                threshold -= 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
