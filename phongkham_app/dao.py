from flask_mail import Mail, Message

from phongkham_app.models import Appointment, Schedule, User, UserRoleEnum, Checkup, Medicine, PrescriptionDetails, \
    Prescription, Receipt
from phongkham_app import db, app, mail
from sqlalchemy import func, Column, Date
from datetime import date
from sqlalchemy.orm import joinedload, contains_eager
import hashlib
from sqlalchemy.orm import aliased


def save_appointment(patient_name, sex, birth_date, user):
    appointment = Appointment(patient_name=patient_name, sex=sex, birth_date=birth_date, user=user)
    db.session.add(appointment)
    db.session.commit()
    return


def send_email(patient_name, birth_date, sex, email):
    msg = Message('Xác nhận đặt lịch khám', recipients=[email])
    msg.body = f'Chào {patient_name},\n\nChúng tôi đã nhận được lịch khám của bạn' \
               f'\n\nĐây là thông tin bạn đã cung cấp: Ngày sinh của bạn là {birth_date}.' \
               f'\n\nGiới tính {sex}' \
               f'\n\nCảm ơn bạn đã đặt lịch khám. '

    try:
        mail.send(msg)
        print("Email đã được gửi thành công!")
    except Exception as e:
        print(f"Có lỗi khi gửi email: {str(e)}")


def get_patients_list():
    patients = Appointment.query.filter(Appointment.scheduled.__eq__(False))
    return patients.all()


def get_schedules_list():
    schedules = Schedule.query
    return schedules.all()


def get_schedules_ids():
    schedules_ids = Schedule.query
    return schedules_ids.get('id')


def get_schedules_by_id(schedule_id):
    return Schedule.query.get(schedule_id)


def get_appointment_by_user_id(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        user_appointments = db.session.query(Appointment).filter_by(user=user.id).all()
        return user_appointments
    return None


def get_appointments_and_schedules_by_user(user_id):
    user_alias = aliased(User)
    appointments_and_schedules = (
        db.session.query(Appointment, Schedule)
        .filter(Appointment.user == user_id)
        .join(Schedule, Appointment.schedule_id == Schedule.id)
        .join(user_alias, user_alias.id == user_id)
        .all()
    )
    return appointments_and_schedules


def get_appointments_by_schedule_id(schedule_id):
    appointments = db.session.query(Appointment).filter_by(schedule_id=schedule_id).all()
    return appointments


def save_checkup(symptoms, predict, checkup_user, checkup_date, prescription):
    checkup = Checkup(symptoms=symptoms, predict=predict, checkup_user=checkup_user,
                      checkup_date=checkup_date, prescription=prescription)
    db.session.add(checkup)
    try:
        db.session.commit()
        return checkup
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi lưu đợt khám: {e}")
        return None


def save_schedule(patients):
    schedule = Schedule(appointment_date=date.today(), appointments=patients)
    for patient in patients:
        patient.scheduled = True
        db.session.add(patient)
    db.session.add(schedule)
    db.session.commit()


def get_patients_ids():
    patient_ids = Appointment.query
    return patient_ids.get('id')


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(), username=username.strip(), password=password)
    db.session.add(user)
    db.session.commit()


def is_username_exists(username):
    user = User.query.filter_by(username=username).first()
    return user is not None


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_login_admin(username, password, role=UserRoleEnum.PATIENT):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_medicine_list_in_stock():
    medicine = Medicine.query.filter(Medicine.in_stock.__eq__(True))
    return medicine.all()


def get_medicine_list():
    medicine = Medicine.query
    return medicine.all()


def save_prescription_details(dose, usage, checkup, medicine_id, prescription):
    prescription_details = PrescriptionDetails(dose=dose, usage=usage, checkup=checkup, medicine_id=medicine_id,
                                               prescription=prescription)
    db.session.add(prescription_details)
    db.session.commit()
    return


def save_prescription(prescription_id, receipt):
    prescription = Prescription.query.filter_by(id=prescription_id).first()
    if prescription:
        prescription.receipt = receipt
        db.session.commit()

    return prescription


def get_checkup_by_user_id(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        user_checkup = db.session.query(Checkup).filter_by(checkup_user=user.id).all()
        return user_checkup
    return None


def save_receipt(checkup_date, checkup_fees, medicine_fees):
    receipt = Receipt(checkup_date=checkup_date, checkup_fees=checkup_fees, medicine_fees=medicine_fees)
    db.session.add(receipt)
    db.session.commit()
    return receipt


def get_prescriptions_by_user_id(user_id):
    prescriptions = Prescription.query\
        .join(Checkup, Prescription.checkup)\
        .filter(Checkup.checkup_user == user_id)\
        .options(contains_eager(Prescription.details))\
        .all()

    return prescriptions


def get_prescriptions_list():
    prescriptions = Prescription.query
    return prescriptions.all()


def get_prescriptions_id(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id).first()
    return prescription


def calculate_prescription_cost(prescription_id):
    # Bước 1: Xác định đối tượng Prescription có prescription_id tương ứng
    prescription = Prescription.query.filter_by(id=prescription_id).first()

    if not prescription:
        return None  # Hoặc xử lý lỗi khác tùy thuộc vào yêu cầu của bạn

    # Bước 2: Lấy danh sách chi tiết đơn thuốc liên quan đến prescription
    prescription_details = (
        PrescriptionDetails.query
        .filter_by(prescription=prescription.id)
        .all()
    )

    # Bước 3: Duyệt qua danh sách chi tiết đơn thuốc và tải thông tin thuốc
    total_cost = 0.0
    for prescription_detail in prescription_details:
        # Tải thông tin về thuốc từ bảng Medicine
        medicine = Medicine.query.filter_by(id=prescription_detail.medicine_id).first()

        if medicine:
            # Kiểm tra và chuyển đổi dose thành kiểu số
            try:
                dose_value = float(prescription_detail.dose)
            except ValueError:
                # Xử lý lỗi nếu dose không thể chuyển đổi thành số
                continue

            # Tính tổng tiền cho từng loại thuốc
            medicine_cost = medicine.price * dose_value
            total_cost += medicine_cost

    return total_cost


if __name__ == "__main__":
    with app.app_context():
        db.session.commit()
