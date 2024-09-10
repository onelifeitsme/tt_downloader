import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector

async def fetch_info():
    connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get('https://ipinfo.io', headers={'Accept': 'application/json'}) as response:
            info = await response.json()
            print(info)

async def main():
    await fetch_info()

if __name__ == '__main__':
    asyncio.run(main())