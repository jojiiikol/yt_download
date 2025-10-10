from urllib.error import URLError

from fastapi import FastAPI, Request

from starlette.responses import JSONResponse



def register_exception_handler(app: FastAPI):
    @app.exception_handler(URLError)
    async def url_exception_handler(request: Request, exc: URLError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Host dont respond"},
        )

