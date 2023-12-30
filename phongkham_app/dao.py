from flask_mail import Mail, Message

from phongkham_app.models import Appointment, Schedule, User, UserRoleEnum
from phongkham_app import db, app, mail
from sqlalchemy import func, Column, Date
from datetime import date
import hashlib


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


if __name__ == "__main__":
    with app.app_context():
        a = Appointment(patient_name="Phan", sex="Female", birth_date=date(1945, 11, 5))
        db.session.add(a)
        db.session.commit()
