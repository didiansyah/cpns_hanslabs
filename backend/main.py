import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CPNS 2026 API", version="1.0.0")
app.state.limiter = limiter

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

from routers import auth_router, user_router, question_router, simulation_router, checklist_router, progress_router, leaderboard_router

app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/api/users", tags=["Users"])
app.include_router(question_router.router, prefix="/api/questions", tags=["Questions"])
app.include_router(simulation_router.router, prefix="/api/simulations", tags=["Simulations"])
app.include_router(checklist_router.router, prefix="/api/checklists", tags=["Checklists"])
app.include_router(progress_router.router, prefix="/api/progress", tags=["Progress"])
app.include_router(leaderboard_router.router, prefix="/api/leaderboard", tags=["Leaderboard"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "cpns-2026"}
