from sqlalchemy.orm import Session
import models
from datetime import date

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_available_slots(db: Session, doctor_id: int):
    return db.query(models.Slot).filter(
        models.Slot.doctor_id == doctor_id,
        models.Slot.is_booked == False
    ).order_by(models.Slot.slot_date, models.Slot.start_time).all()

def book_slot(db: Session, slot_id: int, patient_id: int):
    slot = db.query(models.Slot).filter(
        models.Slot.id == slot_id, models.Slot.is_booked == False
    ).first()

    if not slot:
        return None

    slot.is_booked = True
    appointment = models.Appointment(
        doctor_id=slot.doctor_id,
        patient_id=patient_id,
        slot_id=slot.id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

def get_today_slots_by_doctor(db: Session, doctor_id: int):
    today = date.today()
    return db.query(models.Slot).filter(
        models.Slot.doctor_id == doctor_id,
        models.Slot.slot_date == today
    ).order_by(models.Slot.start_time).all()
