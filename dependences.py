
from service.cookie_abstract_service import CookieAbstractService
from service.cookie_service import CookieService
from service.download_abstract_service import DownloadAbstractService
from service.download_service import DownloadYtDlpService
from service.proxy_abstract_service import ProxyAbstractService
from service.proxy_service import ProxyService

proxy_service = ProxyService()


def get_cookie_service():
    return CookieService()

def get_proxy_service() -> ProxyAbstractService:
    return proxy_service


def get_download_ytdlp_service() -> DownloadAbstractService:
    return DownloadYtDlpService(get_proxy_service())

def get_cookie_service() -> CookieAbstractService:
    return CookieService()
