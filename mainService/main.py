from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    birthdate = db.Column(db.Date)
    email = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))

def token_required(f):
    @wraps(f)
    def token_check(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message':'No token'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message':'Invalid token'}), 403

        return f(user, *args, **kwargs)

    return token_check

@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'password' not in data or 'username' not in data:
        return jsonify({'message':'No username or password'}), 400
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16)

    new_user = User(username=data['username'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({'message':'Username is occupied'}), 400
    

    return jsonify({'message':'User registered successfully'}), 200

@app.route('/api/users/auth', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'message':'User not found'}), 404

    if check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'auth token': token}), 200

    return jsonify({'message':'Wrong credentials'}), 401

@app.route('/api/users/me', methods=['PUT'])
@token_required
def update_user(user):
    data = request.get_json()

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'birthdate' in data:
        user.phone_number = data['birthdate']
    if 'email' in data:
        user.email = data['email']
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
        

    db.session.commit()

    return jsonify({'message':'User data updated successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)