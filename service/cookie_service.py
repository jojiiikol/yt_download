import time
from typing import List
from urllib.parse import urlparse

import os

from playwright.sync_api import sync_playwright, Cookie, ProxySettings

from schema.proxy_schema import ProxySchema
from service.cookie_abstract_service import CookieAbstractService
from settings import COOKIES_DIR, BROWSER_PROFILE_DIR
from utils.filename_maker import get_filename
import asyncio


class CookieService(CookieAbstractService):

    def normalize_proxy(self, proxy_url: ProxySchema):
        proxy_url = proxy_url.url
        proxy_dict = urlparse(proxy_url)
        proxy_conf = {
            "server": f"{proxy_dict.scheme}://{proxy_dict.hostname}:{proxy_dict.port}"
        }

        if proxy_dict.username:
            proxy_conf["username"] = proxy_dict.username
        if proxy_dict.password:
            proxy_conf["password"] = proxy_dict.password

        return proxy_conf

    async def get_cookie_path(self, proxy_url: ProxySchema, cookie_text: str | None = None) -> str:
        if cookie_text is not None:
            return await self.make_cookie_file(cookie_text)
        else:
            cookie_path = os.path.join(COOKIES_DIR, "cookie.txt")
            return cookie_path

    async def rewrite_cookie(self, cookie_text: str | None = None):
        cookie_path = os.path.join(COOKIES_DIR, "cookie.txt")
        with open(cookie_path, "w", encoding="utf-8") as file:
            file.write(cookie_text)


    async def make_cookie_file(self, cookie_text: str) -> str:
        filename = get_filename("cookie.txt")
        cookies_file_path = os.path.join(COOKIES_DIR, f"{filename}")
        with open(cookies_file_path, "w", encoding="utf-8") as file:
            file.write(cookie_text)
        return cookies_file_path

    async def save_cookie_to_netscape(self, cookies: List[Cookie], cookie_path: str):
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = cookie.get("domain", "")
                flag = "TRUE" if domain.startswith(".") else "FALSE"
                path = cookie.get("path", "/")
                secure = "TRUE" if cookie.get("secure", False) else "FALSE"
                expires = str(int(cookie.get("expires", 0)))
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                line = "\t".join([domain, flag, path, secure, expires, name, value])
                f.write(line + "\n")

    async def refresh_cookie_2(self, proxy_url: ProxySchema, cookie_path: str | None = None):
        proxy_conf = self.normalize_proxy(proxy_url)
        print("Refreshing cookie")



        def sync_refresh_cookie(cookie_path: str):
            with sync_playwright() as p:
                context = p.firefox.launch_persistent_context(
                    user_data_dir=BROWSER_PROFILE_DIR,
                    headless=True,
                    proxy=ProxySettings(**proxy_conf)
                )

                page = context.new_page()
                page.goto("https://www.youtube.com/")
                time.sleep(2)
                cookie = context.cookies()
            return cookie

        if not os.path.exists(BROWSER_PROFILE_DIR):
            raise FileNotFoundError()
        else:
            cookie = await asyncio.to_thread(sync_refresh_cookie, cookie_path)
            await self.save_cookie_to_netscape(cookie, cookie_path)
            return cookie_path


