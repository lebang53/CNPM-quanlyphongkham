from sqlalchemy import Column, Integer, Boolean, Float, Date, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from phongkham_app import app, db
from enum import Enum as UserEnum
from datetime import datetime, date
from flask_login import UserMixin


class UserRoleEnum(UserEnum):
    PATIENT = 1
    DOCTOR = 2
    NURSE = 3
    CASHIER = 4
    ADMIN = 5


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.PATIENT)
    active = Column(Boolean, default=True)
    address = Column(String(50), nullable=True)
    phone = Column(String(11), nullable=True)
    checkups = relationship('Checkup', backref='user_checkup', lazy=True)
    appointment = relationship('Appointment', backref='user_appointment', lazy=True)

    def __str__(self):
        return self.name

    def get_prescriptions(self):
        return Prescription.query.join(Checkup).filter(Checkup.checkup_user == self.id).all()


class Medicine(BaseModel):
    name = Column(String(50), nullable=False)
    unit = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Integer, nullable=False)
    exp_date = Column(Date)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    prescription = relationship('PrescriptionDetails', backref='prescription_medicine', lazy=False)

    def __str__(self):
        return self.name


class MedicineCategory(BaseModel):
    __tablename__ = 'category'
    name = Column(String(50), nullable=False)
    medicine = relationship('Medicine', backref='category', lazy=False)

    def __str__(self):
        return self.name


class Appointment(BaseModel):
    patient_name = Column(String(50), nullable=False)
    sex = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=False)
    scheduled = Column(Boolean, default=False)
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    user = Column(Integer, ForeignKey("user.id"))

    def __str__(self):
        return self.patient_name


class Schedule(BaseModel):
    appointment_date = Column(Date, nullable=False)
    appointments = relationship('Appointment', backref='schedule', lazy=False)


class Receipt(BaseModel):
    checkup_date = Column(Date, nullable=False)
    checkup_fees = Column(Float, nullable=False)
    medicine_fees = Column(Float, nullable=False)
    prescription = relationship('Prescription', backref='receipt_prescription', lazy=True)


class Checkup(BaseModel):
    checkup_date = Column(Date, nullable=False)
    symptoms = Column(String(100), nullable=False)
    predict = Column(String(100), nullable=False)
    checkup_user = Column(Integer, ForeignKey('user.id'))
    prescription = Column(Integer, ForeignKey('prescription.id'))
    prescription_details = relationship('PrescriptionDetails', backref='prescription_details_checkup', lazy=False)


class Prescription(BaseModel):
    details = relationship('PrescriptionDetails', backref='prescription_detail', lazy=True)
    checkup = relationship('Checkup', backref='prescription_checkup', lazy=True)
    receipt = Column(Integer, ForeignKey("receipt.id"))

    @classmethod
    def create_prescription(cls, receipt_id=None):
        new_prescription = cls()

        # Thêm logic để gán receipt_id nếu được truyền vào
        if receipt_id is not None:
            new_prescription.receipt = receipt_id

        db.session.add(new_prescription)
        db.session.commit()

        return new_prescription


class PrescriptionDetails(BaseModel):
    dose = Column(String(100), nullable=False)
    usage = Column(String(100), nullable=False)
    checkup = Column(Integer, ForeignKey("checkup.id"))
    prescription = Column(Integer, ForeignKey("prescription.id"))
    medicine_id = Column(Integer, ForeignKey("medicine.id"))


if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        db.session.commit()
