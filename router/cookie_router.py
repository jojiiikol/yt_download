from fastapi import APIRouter
from fastapi.params import Body, Depends

from dependences import get_cookie_service
from service.cookie_abstract_service import CookieAbstractService

router = APIRouter(
    prefix="/cookie",
    tags=["cookie"],
)

@router.post("/")
async def create_cookie(cookies_text: None | str = Body(None, media_type="text/plain"),
                        cookie_service: CookieAbstractService = Depends(get_cookie_service)):
    await cookie_service.rewrite_cookie(cookies_text)
    return "Success"
