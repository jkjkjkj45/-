import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'

AUTH_SERVICE_URL = "http://127.0.0.1:5001"
APPOINTMENT_SERVICE_URL = "http://127.0.0.1:5002"

@app.route('/')
def index():
    try:
        user = session.get('user')
        return render_template('Главная.html', user=user)
    except Exception as e:
        return f"Ошибка при загрузке шаблона Главная.html: {e}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        data = {'name': name, 'email': email, 'password': password}
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=data)
        
        if response.status_code == 201:
             flash('Регистрация успешна! Пожалуйста, войдите.', 'registration')
             return redirect(url_for('login'))
        else:
            flash(response.json().get('message', 'Ошибка регистрации. Попробуйте снова'), 'registration')
            return redirect(url_for('register'))
    try:
        return render_template('Регистрация.html')
    except Exception as e:
        return f"Ошибка при загрузке шаблона Регистрация.html: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = {'email': email, 'password': password}
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=data)
        
        if response.status_code == 200:
            session['user'] = response.json()['user']
            return redirect(url_for('index'))
        else:
            flash('Неправильный email или пароль. Пожалуйста, попробуйте снова.')
            return redirect(url_for('login'))
    try:
        return render_template('Вход.html')
    except Exception as e:
        return f"Ошибка при загрузке шаблона Вход.html: {e}"

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы.', 'log_out')
    return redirect(url_for('index'))

@app.route('/doctors')
def doctors():
    try:
        user = session.get('user')
        response = requests.get(f"{APPOINTMENT_SERVICE_URL}/appointments")
        appointments = response.json().get('appointments', [])
        return render_template('Врачи.html', user=user, appointments=appointments)
    except Exception as e:
        return f"Ошибка при загрузке шаблона Врачи.html: {e}"

@app.route('/my_appointments')
def my_appointments():
     if 'user' not in session:
        flash('Вам нужно войти, чтобы посмотреть свои записи.')
        return redirect(url_for('login'))
     try:
        user_email = session['user']['email']
        response = requests.get(f"{APPOINTMENT_SERVICE_URL}/appointments")
        if response.status_code == 200:
             all_appointments = response.json().get('appointments', [])
             user_appointments = [appt for appt in all_appointments if appt['user_email'] == user_email]
             return render_template('МоиЗаписи.html', appointments=user_appointments)
        else:
            flash(f'Ошибка загрузки записей. Пожалуйста, попробуйте позже', 'error_loading_appointments')
            return redirect(url_for('index'))
     except Exception as e:
        return f"Ошибка при загрузке шаблона МоиЗаписи.html: {e}"


@app.route('/appointment', methods=['POST'])
def appointment():
     if 'user' not in session:
          return jsonify(success=False, message='Вам нужно войти, чтобы записаться на приём.')
     try:
        data = request.get_json()
        if not data or 'doctor_name' not in data or 'appointment_time' not in data:
             return jsonify(success=False, message="Неверные данные запроса."), 400
        doctor_name = data['doctor_name']
        appointment_time = data['appointment_time']
        user_email = session['user']['email']
        payload = {'doctor_name': doctor_name, 'appointment_time': appointment_time, 'user_email': user_email}
        response = requests.post(f"{APPOINTMENT_SERVICE_URL}/appointments", json=payload)
        
        if response.status_code == 201:
             return jsonify(success=True)
        else:
             return jsonify(success=False, message=response.json().get('message','Ошибка при создании записи')), response.status_code
     except Exception as e:
         return jsonify(success=False, message=f'Произошла ошибка: {e}'), 500

if __name__ == '__main__':
    app.run(debug=True)
