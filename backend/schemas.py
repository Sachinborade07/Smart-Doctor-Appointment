from datetime import date, time
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    hashed_password: str
    role: str  

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None

class AppointmentCreate(BaseModel):
    slot_id: int

class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: date
    slot_id: time
    status: str
    class Config:
        from_attributes = True