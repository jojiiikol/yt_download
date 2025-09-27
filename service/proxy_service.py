import random
from typing import List

from schema.proxy_schema import ProxySchema
from service.proxy_abstract_service import ProxyAbstractService



class ProxyService(ProxyAbstractService):
    proxy_list = [ProxySchema(url="127.0.0.1:8000")]

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