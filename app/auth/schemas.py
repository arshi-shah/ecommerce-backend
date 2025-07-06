from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal, Optional
import re

class UserCreate(BaseModel):
    name: str= Field(..., min_length=3,max_length=30)
    email: EmailStr
    password: str= Field(..., min_length=6)
    role: Literal["admin", "user"]  # Restrict role to allowed values

    @validator("email")
    def validate_gmail(cls, value):
        pattern = r"^[a-zA-Z][\w.-]*@gmail\.com$"
        if not re.match(pattern, value):
            raise ValueError("Email must be a valid Gmail address, starting with a letter and no special characters.")
        return value

    @validator("name")
    def validate_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces.")
        return value

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str= Field(..., min_length=6)