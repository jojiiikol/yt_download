import json
import os
import random
from typing import List

import aiohttp

from asyncio import gather

from aiohttp_socks import ProxyConnector
from dotenv import load_dotenv
from fastapi import HTTPException

from schema.proxy_schema import ProxySchema
from service.proxy_abstract_service import ProxyAbstractService

load_dotenv()

class ProxyService(ProxyAbstractService):
    proxy_list: List[ProxySchema] = [

    ]


    async def get_all(self) -> List[ProxySchema]:
        return self.proxy_list


    async def add_proxy(self, proxy: List[ProxySchema]) -> List[ProxySchema]:
        self.proxy_list += proxy
        return self.proxy_list


    async def remove_proxy(self, url: str) -> List[ProxySchema] | None:
        print("delete ", url)
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
            async with session.get(f"http://htmlweb.ru/json/proxy/get?short=2&country_not=RU&perpage=100&api_key={os.getenv("PROXY_API_KEY")}") as response:
                text = await response.json()
                schemas = []
                for i in range(0, 100):
                    try:
                        if text[str(i)].find("://") == -1:
                            schemas.append(ProxySchema(url=f"http://{text[str(i)]}"))
                        else:
                            schemas.append(ProxySchema(url=f"{text[str(i)]}"))
                    except Exception as e:
                        HTTPException(status_code=500, detail="Proxy API doesnt working")
        tasks = [self.check_proxy(proxy) for proxy in schemas]
        result = await gather(*tasks)
        working_proxies = [proxy for proxy, ok in zip(schemas, result) if ok]
        print(working_proxies)
        self.proxy_list += working_proxies
        return self.proxy_list

    async def check_proxy(self, proxy: ProxySchema):
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            if proxy.url.startswith("socks5://"):
                connector = ProxyConnector.from_url(proxy.url)
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get("https://www.youtube.com/") as response:
                        print(f"{proxy.url} -> {response.status}")
                        return response.status == 200
            else:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get("https://www.youtube.com/", proxy=proxy.url) as response:
                        print(f"{proxy.url} -> {response.status}")
                        return response.status == 200
        except Exception as e:
            print(e)
        return False

    async def get_http_proxies(self):
        proxy_list = [proxy for proxy in self.proxy_list if proxy.url.startswith("http://") or proxy.url.startswith("https://")]
        return proxy_list

    async def get_proxy(self, proxy_url: str | None = None) -> ProxySchema:
        if proxy_url is not None:
            proxy_check = await self.check_proxy(ProxySchema(url=proxy_url))
            if proxy_check:
                return ProxySchema(url=proxy_url)
            else:
                raise HTTPException(status_code=402, detail=f"Invalid proxy for YouTube: {proxy_url}")
        if len(self.proxy_list) == 0:
            await self.get_proxy_list()
            if len(self.proxy_list) == 0:
                raise HTTPException(status_code=402, detail=f"Empty proxy pool")
        proxy = random.choice(self.proxy_list)
        return proxy