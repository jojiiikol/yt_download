from abc import ABC


class CookieAbstractService(ABC):
    @staticmethod
    async def make_cookie_file(cookie_text: str) -> str:
        pass
