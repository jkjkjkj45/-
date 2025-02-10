import json
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

#Factory Method (Фабричный Метод): Используем для создания объектов, таких как пользователи.
class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class UserFactory:
    @staticmethod
    def create_user(name, email, password):
        return User(name, email, password)

class DataFacade:
    @staticmethod
    def load_users():
        try:
            with open('usersClinic.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    @staticmethod
    def save_users(users):
        with open('usersClinic.json', 'w', encoding='utf-8') as file:
            json.dump(users, file, ensure_ascii=False)

#Strategy (Стратегия): Можно использовать для различных стратегий аутентификации пользователей.
class AuthenticationStrategy:
    def authenticate(self, email, password):
        raise NotImplementedError

class SimpleAuth(AuthenticationStrategy):
    def authenticate(self, email, password):
        users = DataFacade.load_users()
        if email in users and users[email]['password'] == password:
            return users[email]
        return None

class AuthContext:
    def __init__(self, strategy: AuthenticationStrategy):
        self._strategy = strategy

    def authenticate(self, email, password):
        return self._strategy.authenticate(email, password)

@app.route('/register', methods=['POST'])
def register():
    users = DataFacade.load_users()
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify(success=False, message="Неверные данные запроса."), 400

    name = data['name']
    email = data['email']
    password = data['password']

    if email in users:
        return jsonify(success=False, message='Этот email уже зарегистрирован.'), 400
    
    user = UserFactory.create_user(name, email, password)
    users[email] = {'name': user.name, 'email': user.email, 'password': user.password}
    DataFacade.save_users(users)
    return jsonify(success=True, message='Регистрация успешна!'), 201

@app.route('/login', methods=['POST'])
def login():
    auth_context = AuthContext(SimpleAuth())
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(success=False, message="Неверные данные запроса."), 400
        
    email = data['email']
    password = data['password']
    user = auth_context.authenticate(email, password)
    if user:
        return jsonify(success=True, user=user), 200
    else:
        return jsonify(success=False, message='Неверный email или пароль.'), 401
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)
