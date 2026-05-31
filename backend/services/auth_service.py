import os, random, string
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from models import User, EmailOTP
import bcrypt

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET or JWT_SECRET in ("dev-secret", "change-me", ""):
    raise RuntimeError("FATAL: JWT_SECRET environment variable must be set to a strong random value")
JWT_ALGORITHM = "HS256"
OTP_EXPIRE = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
OTP_MAX = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
OTP_FROM = os.getenv("OTP_FROM", "noreply@hanslabs.xyz")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def generate_otp():
    return "".join(random.choices(string.digits, k=6))

def create_jwt(user_id: int, email: str):
    payload = {"sub": str(user_id), "email": email, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": int(payload["sub"]), "email": payload.get("email")}
    except JWTError:
        return None

async def send_otp_email(email: str, code: str):
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
            json={
                "from": OTP_FROM,
                "to": [email],
                "subject": f"Kode Verifikasi CPNS: {code}",
                "html": f"""<div style="font-family:sans-serif;max-width:400px;margin:0 auto;padding:20px">
                <h2 style="color:#111">Verifikasi Akun CPNS</h2>
                <p>Kode OTP Anda:</p>
                <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#111;background:#f5f5f5;padding:16px;text-align:center;border-radius:8px">{code}</div>
                <p style="color:#666;font-size:13px">Berlaku {OTP_EXPIRE} menit. Jangan bagikan kode ini.</p>
                </div>"""
            }
        )
        return resp.status_code == 200

def request_otp(db: Session, email: str):
    from datetime import datetime as dt
    # Check rate limit (3 per minute)
    recent = db.query(EmailOTP).filter(
        EmailOTP.email == email,
        EmailOTP.created_at > dt.now() - timedelta(minutes=1)
    ).count()
    if recent >= 3:
        return None, "Tunggu 1 menit sebelum minta OTP lagi"

    # Invalidate all previous unused OTPs for this email (prevent brute force accumulation)
    db.query(EmailOTP).filter(
        EmailOTP.email == email,
        EmailOTP.used == False
    ).update({"used": True})

    code = generate_otp()
    otp = EmailOTP(email=email, code=code, expires_at=dt.now() + timedelta(minutes=OTP_EXPIRE))
    db.add(otp)
    db.commit()
    return code, None

def verify_otp_register(db: Session, email: str, code: str, name: str, password: str, phone: str = None, education: str = None, target_instansi: str = None):
    """Verify OTP and complete registration with password."""
    from datetime import datetime as dt
    otp = db.query(EmailOTP).filter(
        EmailOTP.email == email, EmailOTP.used == False, EmailOTP.expires_at > dt.now()
    ).order_by(EmailOTP.id.desc()).first()

    if not otp:
        return None, "OTP tidak ditemukan atau sudah kedaluwarsa"
    if otp.attempts >= OTP_MAX:
        otp.used = True
        db.commit()
        return None, "Terlalu banyak percobaan. Minta OTP baru"
    if otp.code != code:
        otp.attempts += 1
        db.commit()
        return None, f"Kode salah. Sisa percobaan: {OTP_MAX - otp.attempts}"

    otp.used = True
    db.commit()

    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return None, "Email sudah terdaftar. Silakan login."

    # Create user with hashed password
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        phone=phone,
        education=education,
        target_instansi=target_instansi,
        verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create progress record
    from models import Progress
    progress = Progress(user_id=user.id)
    db.add(progress)
    db.commit()

    token = create_jwt(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}}, None

def login_with_password(db: Session, email: str, password: str):
    """Login with email + password (no OTP)."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, "Email atau password salah"
    if not user.password_hash:
        return None, "Akun ini belum set password. Silakan register ulang."
    if not check_password(password, user.password_hash):
        return None, "Email atau password salah"

    token = create_jwt(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email}}, None
