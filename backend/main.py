import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=get_client_ip)
app = FastAPI(title="CPNS 2026 API", version="1.0.0")
app.state.limiter = limiter

SCRAPE_PROTECTED_PREFIXES = ("/api/questions", "/api/simulations")
BLOCKED_USER_AGENT_PARTS = (
    "curl", "wget", "python-requests", "python-urllib", "httpx",
    "aiohttp", "scrapy", "go-http-client", "java/", "okhttp",
    "libwww-perl", "phpcrawl", "headlesschrome",
)


@app.middleware("http")
async def anti_scraping_guard(request: Request, call_next):
    path = request.url.path
    protected = path.startswith(SCRAPE_PROTECTED_PREFIXES)
    if protected:
        user_agent = request.headers.get("User-Agent", "").strip().lower()
        auth = request.headers.get("Authorization", "")
        authenticated = False
        if auth.startswith("Bearer "):
            try:
                from services.auth_service import decode_jwt
                authenticated = decode_jwt(auth[7:]) is not None
            except Exception:
                authenticated = False
        if not authenticated and (not user_agent or any(part in user_agent for part in BLOCKED_USER_AGENT_PARTS)):
            return JSONResponse(status_code=403, content={"ok": False, "error": "Forbidden"})
    response = await call_next(request)
    if protected:
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response.headers["Cache-Control"] = "private, no-store"
    return response

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Terlalu banyak request. Coba lagi nanti."})

ALLOWED_ORIGINS = [
    "https://cpns.hanslabs.xyz",
    "http://localhost:3050",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

from routers import auth_router, user_router, question_router, simulation_router, checklist_router, progress_router, leaderboard_router, admin_router, feedback_router

app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/api/users", tags=["Users"])
app.include_router(question_router.router, prefix="/api/questions", tags=["Questions"])
app.include_router(simulation_router.router, prefix="/api/simulations", tags=["Simulations"])
app.include_router(checklist_router.router, prefix="/api/checklists", tags=["Checklists"])
app.include_router(progress_router.router, prefix="/api/progress", tags=["Progress"])
app.include_router(leaderboard_router.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])
app.include_router(feedback_router.router, prefix="/api/feedback", tags=["Feedback"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "cpns-2026"}

