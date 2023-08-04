from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    expires_at: int
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
