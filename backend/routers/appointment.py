from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import DoctorAvailabilitySlot, Appointment
from schemas import AppointmentOut
from typing import List
from datetime import datetime

router = APIRouter(tags=["Appointment"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/slots", response_model=List[AppointmentOut])
def get_slots(db: Session = Depends(get_db)):
    today = datetime.today().date()
    return db.query(DoctorAvailabilitySlot).filter(DoctorAvailabilitySlot.slot_date >= today).all()

@router.post("/book/{slot_id}")
def book_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = db.query(DoctorAvailabilitySlot).filter(DoctorAvailabilitySlot.id == slot_id).first()
    if not slot or slot.is_booked:
        raise HTTPException(status_code=404, detail="Slot not available")
    slot.is_booked = True
    db.commit()
    return {"msg": "Appointment booked"}

@router.get("/doctor/slots", response_model=List[AppointmentOut])
def doctor_slots(doctor_id: int, db: Session = Depends(get_db)):
    today = datetime.today().date()
    return db.query(DoctorAvailabilitySlot).filter(
        DoctorAvailabilitySlot.doctor_id == doctor_id,
        DoctorAvailabilitySlot.slot_date >= today
    ).all()