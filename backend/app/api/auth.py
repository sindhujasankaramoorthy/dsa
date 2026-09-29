from fastapi import APIRouter, HTTPException
from backend.app.schemas.user import LoginRequest, AuthToken, UserSchema

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=AuthToken)
def login(req: LoginRequest):
    # Simulated authentication for demo & business user access
    role = "Admin" if req.username.lower() in ["admin", "manager"] else "Business User"
    user = UserSchema(
        user_id=f"usr_{req.username}",
        username=req.username,
        role=role,
        email=f"{req.username}@freshgrade.ai",
        organization="FreshGrade Quality Operations"
    )
    return AuthToken(
        access_token=f"freshgrade_token_{req.username}_2026",
        token_type="bearer",
        user=user
    )

@router.post("/register", response_model=AuthToken)
def register(req: LoginRequest):
    user = UserSchema(
        user_id=f"usr_{req.username}",
        username=req.username,
        role="Business User",
        email=f"{req.username}@freshgrade.ai",
        organization="FreshGrade Enterprise"
    )
    return AuthToken(
        access_token=f"freshgrade_token_{req.username}_2026",
        token_type="bearer",
        user=user
    )
