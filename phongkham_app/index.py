from flask_login import login_user, logout_user

from phongkham_app import app, dao, login
from flask import render_template, request, redirect, url_for, session


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


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
            elif user.user_role.name == 'CASHER':
                login_user(user=user)
                return redirect(url_for('casher'))
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
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirmpassword')
        try:
            if password.strip().__eq__(confirm.strip()):
                dao.add_user(name=name, username=username, password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Password not match'
        except Exception as ex:
            err_msg = 'Request Error ' + str(ex)
    return render_template('register.html', err_msg=err_msg)


# dang xuat
@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect(url_for('home'))


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
    return render_template('appointment.html')


@app.route('/login-admin', methods=['get', 'post'])
def admin_signin():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.check_login_admin(username=username, password=password, role=UserRoleEnum.ADMIN)

        if user:
            login_user(user=user)
    return redirect('/admin')


@app.route('/checkup')
def create_checkup():
    return render_template('create_checkup.html')


@app.route('/create_schedule', methods=['GET', 'POST'])
def nurse():
    patients = dao.get_patients_list()
    return render_template('create_schedule.html', patients=patients)


@app.route('/nurse/create_appointment', methods=['GET', 'POST'])
def nurse_create_appointment():
    if request.method == 'POST':
        patient_name = request.form['patientName']
        sex = request.form['sex']
        birth_date = request.form['birthDate']
        user = session.get('user_id')
        # email = request.form['email']
        dao.save_appointment(patient_name=patient_name, sex=sex, birth_date=birth_date, user=user)

        # dao.send_email(patient_name=patient_name, birth_date=birth_date, sex=sex, email=email)
    return render_template('create_appointment.html')


@app.route('/create_schedule/save_list')
def save_list():
    patients = dao.get_patients_list()
    dao.save_schedule(patients=patients)
    return redirect('/create_schedule')


@app.route('/see_schedule')
def see_schedule():
    schedules = dao.get_schedules_list()
    return render_template('see_schedule.html', schedules=schedules)


@app.route('/see_schedule_details/<int:schedule_id>')
def see_schedule_details(schedule_id):
    schedule = dao.get_schedules_by_id(schedule_id=schedule_id)
    appointments = dao.get_appointments_by_schedule_id(schedule_id=schedule_id)
    return render_template('see_schedule_details.html', appointments=appointments)


@app.route('/create_schedule')
def doctor():
    return render_template('create_schedule.html')


@app.route('/create_schedule')
def casher():
    return render_template('create_schedule.html')


if __name__ == "__main__":
    from phongkham_app.admin import *
    app.run(debug=True)
