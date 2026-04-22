from fastapi import Cookie, HTTPException, status
from jwt import InvalidTokenError

from app.db import get_collection
from app.security import decode_access_token


async def get_current_admin(admin_token: str | None = Cookie(default=None)):
    if not admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(admin_token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin = await get_collection("admins").find_one({"username": username})
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")

    return {"username": admin["username"]}
