import json
import random
from typing import List

import aiohttp

from asyncio import gather

from aiohttp_socks import ProxyConnector

from schema.proxy_schema import ProxySchema
from service.proxy_abstract_service import ProxyAbstractService



class ProxyService(ProxyAbstractService):
    proxy_list: List[ProxySchema] = [
        ProxySchema(url="http://5.10.245.118:80"),
        ProxySchema(url="http://194.152.44.40:80"),
        ProxySchema(url="socks5://user:PyAt!g0rets@202.148.55.193:39937"),
        ProxySchema(url="socks5://185.93.89.147:4002"),
    ]


    async def get_all(self) -> List[ProxySchema]:
        return self.proxy_list


    async def add_proxy(self, proxy: List[ProxySchema]) -> List[ProxySchema]:
        self.proxy_list += proxy
        return self.proxy_list


    async def remove_proxy(self, url: str) -> List[ProxySchema] | None:
        for find_proxy in self.proxy_list:
            if find_proxy.url == url:
                self.proxy_list.remove(find_proxy)
                return self.proxy_list
        return None

    async def delete_all(self) -> List | None:
        self.proxy_list = []
        return self.proxy_list

    async def get_proxy_list(self):
        schemas = None
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.proxy-list.download/api/v1/get?type=http") as response:
                text = await response.text()
                text = text.splitlines()
                schemas = [ProxySchema(url=f"http://{ip}") for ip in text]
            async with session.get("https://www.proxy-list.download/api/v1/get?type=socks5") as response:
                text = await response.text()
                text = text.splitlines()
                schemas += [ProxySchema(url=f"socks5://{ip}") for ip in text]
        tasks = [self.check_proxy(proxy) for proxy in schemas]
        result = await gather(*tasks)
        working_proxies = [proxy for proxy, ok in zip(schemas, result) if ok]
        self.proxy_list += working_proxies
        return self.proxy_list

    async def check_proxy(self, proxy: ProxySchema):
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            if proxy.url.startswith("socks5://"):
                connector = ProxyConnector.from_url(proxy.url)
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get("https://www.google.com/") as response:
                        print(f"{proxy.url} -> {response.status}")
                        return response.status == 200
            else:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get("https://www.google.com/", proxy=proxy.url) as response:
                        print(f"{proxy.url} -> {response.status}")
                        return response.status == 200
        except Exception as e:
            print(e)
        return False



    async def get_random_proxy(self) -> ProxySchema:
        proxy = random.choice(self.proxy_list)
        return proxy