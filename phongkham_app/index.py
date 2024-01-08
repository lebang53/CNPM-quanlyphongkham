from functools import wraps
from flask_login import login_user, logout_user, login_required
from phongkham_app import app, dao, login
from flask import render_template, request, redirect, url_for, session
from phongkham_app.admin import *


@app.route("/")
def home():
    return render_template("patient/index.html")


@app.route("/about")
def about():
    return render_template("patient/about.html")


# dang nhap
@app.route('/login', methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.check_login(username=username, password=password)
        session["user_id"] = user.id
        if user:
            if user.user_role.name == 'ADMIN':
                return redirect(url_for('admin_signin'))
            elif user.user_role.name == 'NURSE':
                login_user(user=user)
                return redirect(url_for('nurse'))
            elif user.user_role.name == 'DOCTOR':
                login_user(user=user)
                return redirect(url_for('doctor'))
            elif user.user_role.name == 'CASHIER':
                login_user(user=user)
                return redirect(url_for('cashier'))
            else:
                login_user(user=user)
                return redirect(url_for('home'))
        else:
            err_msg = 'Username or Password is Invalid'

    return render_template('login.html', err_msg=err_msg)


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)


# dang ky
@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ' '
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirmpassword')

        try:
            if password.strip() == confirm.strip():
                if dao.is_username_exists(username):
                    err_msg = 'Username đã tồn tại'
                else:
                    dao.add_user(name=name, username=username, password=password)
                    return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Lỗi ' + str(ex)

    return render_template('register.html', err_msg=err_msg)


# dang xuat
@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/error')
def error_page():
    return render_template('404.html')


@app.route('/create_appointment', methods=['GET', 'POST'])
def create_appointment():
    if request.method == 'POST':
        patient_name = request.form['patientName']
        sex = request.form['sex']
        birth_date = request.form['birthDate']
        user = session.get('user_id')
        email = request.form['email']
        dao.save_appointment(patient_name=patient_name, sex=sex, birth_date=birth_date, user=user)

        dao.send_email(patient_name=patient_name, birth_date=birth_date, sex=sex, email=email)
    return render_template('patient/appointment.html')


@app.route('/my_appointment/<int:user_id>', methods=['GET', 'POST'])
def my_appointment(user_id):
    appointments_and_schedules = dao.get_appointments_and_schedules_by_user(user_id=user_id)
    return render_template('patient/my_appointment.html', appointments_and_schedules=appointments_and_schedules)


@app.route('/my_diagnosis/<int:user_id>', methods=['GET', 'POST'])
def my_diagnosis(user_id):
    # appointments_and_schedules = dao.get_appointments_and_schedules_by_user(user_id=user_id)
    return render_template('patient/my_diagnosis.html')


@app.route('/my_info/<int:user_id>', methods=['GET', 'POST'])
def my_info(user_id):
    # appointments_and_schedules = dao.get_appointments_and_schedules_by_user(user_id=user_id)
    return render_template('patient/my_info.html')


@app.route('/login-admin', methods=['get', 'post'])
def admin_signin():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.check_login_admin(username=username, password=password, role=UserRoleEnum.ADMIN)

        if user:
            login_user(user=user)
    return redirect('/admin')


@app.route('/nurse/create_schedule', methods=['GET', 'POST'])
@login_required
def nurse():
    if current_user.is_authenticated and current_user.user_role.name == 'NURSE':
        patients = dao.get_patients_list()
        return render_template('nurse/create_schedule.html', patients=patients)
    else:
        return redirect(url_for('error_page'))


@app.route('/nurse/create_appointment', methods=['GET', 'POST'])
@login_required
def nurse_create_appointment():
    if current_user.is_authenticated and current_user.user_role.name == 'NURSE':
        if request.method == 'POST':
            patient_name = request.form['patientName']
            sex = request.form['sex']
            birth_date = request.form['birthDate']
            user = session.get('user_id')
            # email = request.form['email']
            dao.save_appointment(patient_name=patient_name, sex=sex, birth_date=birth_date, user=user)

            # dao.send_email(patient_name=patient_name, birth_date=birth_date, sex=sex, email=email)
        return render_template('nurse/create_appointment.html')
    else:
        return redirect(url_for('error_page'))


@app.route('/create_schedule/save_list')
def save_list():
    patients = dao.get_patients_list()
    dao.save_schedule(patients=patients)
    return redirect('/create_schedule')


@app.route('/nurse/see_schedule')
@login_required
def see_schedule():
    if current_user.is_authenticated and current_user.user_role.name == 'NURSE':
        schedules = dao.get_schedules_list()
        return render_template('nurse/see_schedule.html', schedules=schedules)

    return redirect(url_for('error_page'))


@app.route('/see_schedule_details/<int:schedule_id>')
def see_schedule_details(schedule_id):
    if current_user.is_authenticated and current_user.user_role.name == 'NURSE':
        appointments = dao.get_appointments_by_schedule_id(schedule_id=schedule_id)
        return render_template('nurse/see_schedule_details.html', appointments=appointments)

    return redirect(url_for('error_page'))


@app.route('/doctor')
def doctor():
    if current_user.is_authenticated and current_user.user_role.name == 'DOCTOR':
        schedules = dao.get_schedules_list()
        return render_template('doctor/doctor.html', schedules=schedules)

    return redirect(url_for('error_page'))


@app.route('/doctor/list_patient/<int:schedule_id>')
def list_patient(schedule_id):
    if current_user.is_authenticated and current_user.user_role.name == 'DOCTOR':
        appointments = dao.get_appointments_by_schedule_id(schedule_id=schedule_id)
        return render_template('doctor/list_patient.html', appointments=appointments)

    return redirect(url_for('error_page'))


@app.route('/doctor/list_patient/create_checkup/<int:user_id>', methods=['GET', 'POST'])
def create_checkup(user_id):
    if current_user.is_authenticated and current_user.user_role.name == 'DOCTOR':
        if request.method == 'POST':
            symptoms = request.form['symptoms']
            predict = request.form['predict']
            checkup_date = request.form['checkupDate']
            checkup_user = user_id
            dao.save_checkup(symptoms=symptoms, predict=predict, checkup_user=checkup_user, checkup_date=checkup_date)
        user = dao.get_user_by_id(user_id)
        appointment = dao.get_appointments_by_schedule_id(user_id)
        return render_template('doctor/create_checkup.html', user=user, appointment=appointment)

    return redirect(url_for('error_page'))


@app.route('/cashier')
def cashier():
    if current_user.is_authenticated and current_user.user_role.name == 'CASHIER':
        schedules = dao.get_schedules_list()
        return render_template('cashier/checkout.html', schedules=schedules)
    return redirect(url_for('error_page'))


@app.route('/cashier/list_checkout/<int:schedule_id>')
def list_checkout(schedule_id):
    if current_user.is_authenticated and current_user.user_role.name == 'CASHIER':
        appointments = dao.get_appointments_by_schedule_id(schedule_id=schedule_id)
        return render_template('cashier/list_checkout.html', appointments=appointments)

    return redirect(url_for('error_page'))


@app.route('/cashier/list_checkout/create_bill/<int:user_id>', methods=['GET', 'POST'])
def create_bill(user_id):
    if current_user.is_authenticated and current_user.user_role.name == 'CASHIER':
        # if request.method == 'POST':
        #     symptoms = request.form['symptoms']
        #     predict = request.form['predict']
        #     checkup_date = request.form['checkupDate']
        #     checkup_user = user_id
        #     dao.save_checkup(symptoms=symptoms, predict=predict, checkup_user=checkup_user, checkup_date=checkup_date)
        user = dao.get_user_by_id(user_id)
        return render_template('cashier/create_bill.html', user=user)

    return redirect(url_for('error_page'))


if __name__ == "__main__":
    app.run(debug=True)
