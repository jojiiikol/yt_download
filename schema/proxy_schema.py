from pydantic import BaseModel


class ProxySchema(BaseModel):
    url: str
