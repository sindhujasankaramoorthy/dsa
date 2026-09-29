from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    user_id: str
    username: str
    role: str  # "Business User" or "Admin"
    email: str
    organization: Optional[str] = "FreshGrade Enterprise"

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema
