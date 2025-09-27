import random
from typing import List

from schema.proxy_schema import ProxySchema
from service.proxy_abstract_service import ProxyAbstractService



class ProxyService(ProxyAbstractService):
    proxy_list: List[ProxySchema] = [
        ProxySchema(url="http://5.10.245.118:80"),
        ProxySchema(url="http://194.152.44.40:80"),
        ProxySchema(url="http://194.36.55.217:80"),
        ProxySchema(url="socks5://185.93.89.147:4002"),
        ProxySchema(url="socks5://141.11.21.206:1080"),
        ProxySchema(url="socks5://51.210.156.30:51771"),
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


    async def get_random_proxy(self) -> ProxySchema:
        proxy = random.choice(self.proxy_list)
        return proxy