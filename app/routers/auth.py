from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.config import settings
from app.db import get_collection
from app.dependencies import get_current_admin
from app.schemas import AdminPublic, LoginRequest
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    admin = await get_collection("admins").find_one({"username": payload.username})
    if not admin or not verify_password(payload.password, admin["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    token = create_access_token(admin["username"])
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.token_expire_minutes * 60,
    )
    return {"ok": True, "username": admin["username"]}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("admin_token")
    return {"ok": True}


@router.get("/me", response_model=AdminPublic)
async def me(admin=Depends(get_current_admin)):
    return admin


async def ensure_default_admin() -> None:
    admins = get_collection("admins")
    existing = await admins.find_one({"username": settings.admin_username})
    if existing:
        return

    await admins.insert_one(
        {
            "username": settings.admin_username,
            "password_hash": hash_password(settings.admin_password),
            "created_at": datetime.now(timezone.utc),
        }
    )
