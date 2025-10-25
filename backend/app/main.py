from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import onboarding
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Onboarding API",
    description="API for user onboarding with Clerk authentication",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        # GCP 배포 URL 추가
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(onboarding.router)


@app.get("/")
async def root():
    return {"message": "Onboarding API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}