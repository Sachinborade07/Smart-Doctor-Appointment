from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable = False)
    email = Column(String, unique=True, nullable = False)
    hashed_password = Column(String,nullable = False)
    role = Column(String, nullable=False)


class DoctorAvailabilitySlot(Base):
    __tablename__ = "doctor_availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    slot_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    is_booked = Column(Boolean, default=False)
    doctor = relationship("User", foreign_keys=[doctor_id])


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    slot_id = Column(Integer, ForeignKey("doctor_availability_slots.id"))
    status = Column(String)
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    slot = relationship("DoctorAvailabilitySlot")