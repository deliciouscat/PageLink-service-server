from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional
from clerk_backend_api import Clerk
import os

router = APIRouter(prefix="/api", tags=["onboarding"])

# Clerk 클라이언트 초기화
clerk_client = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))


class OnboardingRequest(BaseModel):
    applicationName: str = Field(..., min_length=1, max_length=100)
    applicationType: str = Field(..., min_length=1, max_length=50)


class OnboardingResponse(BaseModel):
    message: str
    success: bool


async def verify_clerk_session(authorization: str = Header(...)) -> str:
    """
    Clerk 세션 토큰을 검증하고 userId를 반환합니다.
    """
    try:
        # Bearer 토큰에서 실제 토큰 추출
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="Invalid authorization header format"
            )
        
        token = authorization.replace("Bearer ", "")
        
        # Clerk 세션 검증
        session = clerk_client.sessions.verify_session(
            session_id=token,
        )
        
        if not session or not session.user_id:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        return session.user_id
        
    except Exception as e:
        print(f"Session verification error: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/complete-onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    user_id: str = Depends(verify_clerk_session)
):
    """
    사용자의 온보딩을 완료하고 publicMetadata를 업데이트합니다.
    """
    try:
        # Clerk 사용자 메타데이터 업데이트
        clerk_client.users.update(
            user_id=user_id,
            public_metadata={
                "onboardingComplete": True,
                "applicationName": request.applicationName,
                "applicationType": request.applicationType,
            }
        )
        
        return OnboardingResponse(
            message="User metadata updated successfully",
            success=True
        )
        
    except Exception as e:
        print(f"Error updating user metadata: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error updating user metadata"
        )


@router.get("/onboarding-status")
async def get_onboarding_status(
    user_id: str = Depends(verify_clerk_session)
):
    """
    사용자의 온보딩 상태를 확인합니다.
    """
    try:
        user = clerk_client.users.get(user_id=user_id)
        
        public_metadata = user.public_metadata or {}
        onboarding_complete = public_metadata.get("onboardingComplete", False)
        
        return {
            "onboardingComplete": onboarding_complete,
            "applicationName": public_metadata.get("applicationName"),
            "applicationType": public_metadata.get("applicationType")
        }
        
    except Exception as e:
        print(f"Error fetching user data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching user data"
        )