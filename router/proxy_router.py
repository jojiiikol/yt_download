from typing import List

from fastapi import APIRouter, Depends

from dependences import get_proxy_service, get_cookie_service
from schema.proxy_schema import ProxySchema
from service.cookie_abstract_service import CookieAbstractService
from service.cookie_service import CookieService
from service.proxy_abstract_service import ProxyAbstractService

router = APIRouter(
    prefix="/proxy",
    tags=["proxy"],
)

@router.get("/")
async def get_proxy(proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> List[ProxySchema]:
    result = await proxy_service.get_all()
    return result

@router.post("/")
async def post_proxy(proxy: List[ProxySchema], proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> List[ProxySchema]:
    result = await proxy_service.add_proxy(proxy)
    return result

@router.delete("/all")
async def delete_proxy_all(proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> List | None:
    result = await proxy_service.delete_all()
    return result

@router.delete("/{str}")
async def delete_proxy(url: str, proxy_service: ProxyAbstractService = Depends(get_proxy_service)) -> List[ProxySchema] | None:
    result = await proxy_service.remove_proxy(url)
    return result

@router.get("/get_list")
async def get_list(proxy_service: ProxyAbstractService = Depends(get_proxy_service)):
    result = await proxy_service.get_proxy_list()
    return result

@router.get("/test_cookie")
async def test_cookie(cookie_service: CookieAbstractService = Depends(get_cookie_service)):
    result = await cookie_service.refresh_cookie()
    return result

