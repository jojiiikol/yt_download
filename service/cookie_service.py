import aiofiles
import os
from service.cookie_abstract_service import CookieAbstractService
from settings import COOKIES_DIR, POSIX_MEDIA_DIR
from utils.filename_maker import get_posix_path, get_filename


class CookieService(CookieAbstractService):

    async def make_cookie_file(self, cookie_text: str) -> str:
        filename = get_filename("cookie.txt")
        cookies_file_path = os.path.join(COOKIES_DIR, f"{filename}")
        with open(cookies_file_path, "w", encoding="utf-8") as file:
            file.write(cookie_text)
        return cookies_file_path
