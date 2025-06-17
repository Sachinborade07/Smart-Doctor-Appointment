import subprocess
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from database import SessionLocal, engine
import models, schemas
from models import User, DoctorAvailabilitySlot, Appointment
from schemas import UserCreate, Token, TokenData, AppointmentCreate, AppointmentOut
from routers import auth, user, appointment
from doctor_availability import generate_doctor_slots
from sqlalchemy.orm import joinedload 

generate_doctor_slots(doctor_id=3)


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(appointment.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "asdflk"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/slots", response_model=list[AppointmentOut])
def get_slots(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Not authorized")
    today = datetime.today().date()
    slots = db.query(DoctorAvailabilitySlot).filter(
        DoctorAvailabilitySlot.slot_date >= today,
        DoctorAvailabilitySlot.is_booked == False
    ).all()
    return slots

@app.post("/book")
def book_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book")
    slot = db.query(DoctorAvailabilitySlot).filter(
        DoctorAvailabilitySlot.id == appointment.slot_id,
        DoctorAvailabilitySlot.is_booked == False
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not available")
    slot.is_booked = True
    new_appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=slot.doctor_id,
        slot_id=slot.id,
        status="True"
    )
    db.add(new_appointment)
    db.commit()
    return {"message": "Appointment booked"}

    
@app.get("/doctor/slots", response_model=list[AppointmentOut])
def get_doctor_slots(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    today = datetime.today().date()
    
    slots = db.query(DoctorAvailabilitySlot)\
        .options(
            joinedload(DoctorAvailabilitySlot.appointments)
            .joinedload(Appointment.patient)
        )\
        .filter(
            DoctorAvailabilitySlot.doctor_id == current_user.id,
            DoctorAvailabilitySlot.slot_date >= today
        )\
        .all()
    
    return [AppointmentOut.from_orm(slot) for slot in slots]