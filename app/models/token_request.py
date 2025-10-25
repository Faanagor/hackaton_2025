from pydantic import BaseModel


class TokenRequest(BaseModel):
    device_id: str
