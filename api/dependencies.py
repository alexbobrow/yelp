from fastapi import Header, HTTPException
from starlette import status
from starlette.requests import Request


async def token_auth(request: Request, authorization: str = Header(None, alias="Authorization")) -> bool:
    settings = request.app.container.settings()
    expected_token = settings.api_key
    response_header = {"WWW-Authenticate": 'Token realm="Secured API"'}

    if authorization is None or not authorization.startswith("Token "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
            headers=response_header,
        )

    token = authorization[len("Token ") :]

    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers=response_header,
        )

    return True
