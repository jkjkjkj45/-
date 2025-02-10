import json
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class DataFacade:
    @staticmethod
    def load_appointments():
        try:
            with open('appointments.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def save_appointments(appointments):
        with open('appointments.json', 'w', encoding='utf-8') as file:
            json.dump(appointments, file, ensure_ascii=False)
            
# паттерн Строитель для создания объекта записи к врачу
class Appointment:
    def __init__(self, doctor_name, appointment_time, user_email):
        self.doctor_name = doctor_name
        self.appointment_time = appointment_time
        self.user_email = user_email

    def __repr__(self):
        return f"Appointment(doctor_name={self.doctor_name}, appointment_time={self.appointment_time}, user_email={self.user_email})"

class AppointmentBuilder:
    def __init__(self):
        self._appointment = Appointment(None, None, None)

    def set_doctor_name(self, doctor_name):
        self._appointment.doctor_name = doctor_name
        return self

    def set_appointment_time(self, appointment_time):
        self._appointment.appointment_time = appointment_time
        return self

    def set_user_email(self, user_email):
        self._appointment.user_email = user_email
        return self

    def build(self):
        return self._appointment

@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = DataFacade.load_appointments()
    return jsonify(appointments=appointments)


@app.route('/appointments', methods=['POST'])
def appointment():
    appointments = DataFacade.load_appointments()
    data = request.get_json()
    if not data or 'doctor_name' not in data or 'appointment_time' not in data or 'user_email' not in data:
        return jsonify(success=False, message="Неверные данные запроса."), 400

    doctor_name = data['doctor_name']
    appointment_time = data['appointment_time']
    user_email = data['user_email']


    # Проверяем, не занято ли уже время
    for appt in appointments:
        if appt['doctor_name'] == doctor_name and appt['appointment_time'] == appointment_time:
            return jsonify(success=False, message='Это время уже занято. Пожалуйста, выберите другое время.'), 409

    # Используем Builder для создания новой записи
    builder = AppointmentBuilder()
    new_appointment = (builder
                       .set_doctor_name(doctor_name)
                       .set_appointment_time(appointment_time)
                       .set_user_email(user_email)
                       .build())
    
    appointments.append(new_appointment.__dict__)
    DataFacade.save_appointments(appointments)
    
    return jsonify(success=True, message='Запись успешно создана.'), 201

if __name__ == '__main__':
    app.run(debug=True, port=5002)
