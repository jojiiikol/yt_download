from fastapi import HTTPException
from starlette import status



def connect_exception():
    raise HTTPException(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        detail={"The connection was interrupted."}
    )