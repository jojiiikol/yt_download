from abc import ABC, abstractmethod
from typing import List

from schema.proxy_schema import ProxySchema


class ProxyAbstractService(ABC):
    @abstractmethod
    async def get_all(self) -> List[ProxySchema]:
        pass

    @abstractmethod
    async def add_proxy(self, proxy: List[ProxySchema]) -> List[ProxySchema]:
        pass

    @abstractmethod
    async def remove_proxy(self, url: str) -> List[ProxySchema]:
        pass

    @abstractmethod
    async def delete_all(self) -> List:
        pass

    @abstractmethod
    async def get_proxy(self, proxy_url: str | None = None) -> ProxySchema:
        pass