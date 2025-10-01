from abc import ABC

from schema.proxy_schema import ProxySchema


class CookieAbstractService(ABC):
    @staticmethod
    async def make_cookie_file(cookie_text: str) -> str:
        pass

    async def get_cookie_path(self, proxy_url: ProxySchema, cookie_text: str):
        pass
