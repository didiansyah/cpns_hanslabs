from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from db import get_db
from services.auth_service import (
    FRONTEND_URL,
    create_password_reset,
    decode_jwt,
    login_with_password,
    request_otp,
    reset_password_with_token,
    send_otp_email,
    send_password_reset_email,
    verify_otp_register,
)
from main import limiter

router = APIRouter()

class RegisterReq(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str | None = None
    education: str | None = None
    target_instansi: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password minimal 6 karakter")
        if len(v) > 128:
            raise ValueError("Password maksimal 128 karakter")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and len(v) > 20:
            raise ValueError("Phone must be max 20 characters")
        return v

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordReq(BaseModel):
    email: EmailStr

class ResetPasswordReq(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password minimal 6 karakter")
        if len(v) > 128:
            raise ValueError("Password maksimal 128 karakter")
        return v

class VerifyRegisterReq(BaseModel):
    email: EmailStr
    code: str
    name: str
    password: str
    phone: str | None = None
    education: str | None = None
    target_instansi: str | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP code must be exactly 6 digits")
        return v

@router.post("/register")
@limiter.limit("5/minute")
async def register(req: RegisterReq, request: Request, db: Session = Depends(get_db)):
    """Step 1: Validate data + send OTP for registration."""
    from models import User
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        return {"ok": False, "error": "Email sudah terdaftar"}

    code, err = request_otp(db, req.email)
    if err:
        return {"ok": False, "error": err}

    await send_otp_email(req.email, code)
    return {"ok": True, "message": "OTP dikirim ke email. Silakan verifikasi untuk menyelesaikan registrasi."}

@router.post("/verify-register")
@limiter.limit("10/minute")
def verify_register(req: VerifyRegisterReq, request: Request, db: Session = Depends(get_db)):
    """Step 2: Verify OTP and complete registration with password."""
    result, err = verify_otp_register(
        db, req.email, req.code, req.name, req.password,
        req.phone, req.education, req.target_instansi
    )
    if err:
        return {"ok": False, "error": err}
    return {"ok": True, "data": result}

@router.post("/login")
@limiter.limit("10/minute")
def login(req: LoginReq, request: Request, db: Session = Depends(get_db)):
    """Login with email + password (no OTP)."""
    result, err = login_with_password(db, req.email, req.password)
    if err:
        return {"ok": False, "error": err}
    return {"ok": True, "data": result}

@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(req: ForgotPasswordReq, request: Request, db: Session = Depends(get_db)):
    """Request a one-time password reset link. Response is generic to avoid email enumeration."""
    token, err = create_password_reset(db, req.email)
    if err:
        return {"ok": False, "error": err}
    if token:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        await send_password_reset_email(str(req.email), reset_url)
    return {"ok": True, "message": "Jika email terdaftar, link reset password sudah dikirim."}

@router.post("/reset-password")
@limiter.limit("10/minute")
def reset_password(req: ResetPasswordReq, request: Request, db: Session = Depends(get_db)):
    """Reset password using one-time token from email."""
    result, err = reset_password_with_token(db, req.token, req.password)
    if err:
        return {"ok": False, "error": err}
    return {"ok": True, "data": result}

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    data = decode_jwt(auth[7:])
    if not data:
        return None
    from models import User
    return db.query(User).filter(User.id == data["user_id"]).first()
