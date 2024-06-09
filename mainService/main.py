from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from flask_migrate import Migrate
import grpc
import tasks_pb2
import tasks_pb2_grpc
from google.protobuf.json_format import MessageToDict

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
channel = grpc.insecure_channel(os.environ.get("GRPC_SERVER_URI"))
grpc_client = tasks_pb2_grpc.TaskServiceStub(channel)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(300))
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

@app.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.json
    task_request = tasks_pb2.CreateTaskRequest(
        title=data['title'],
        description=data['description'],
        deadline=data['deadline'],
        author_id=current_user.id
    )
    try:
        response = grpc_client.CreateTask(task_request)
        task_dict = MessageToDict(response.task, preserving_proto_field_name=True)
        return jsonify(task_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            return jsonify({'message': 'You have not permission to this task'}), 500
        return jsonify({'message': 'Unknown error'}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    data = request.json
    task_request = tasks_pb2.UpdateTaskRequest(
        id=task_id,
        title=data['title'],
        description=data['description'],
        deadline=data['deadline'],
        is_completed=data['is_completed'],
        author_id=current_user.id
    )
    try:
        response = grpc_client.UpdateTask(task_request)
        task_dict = MessageToDict(response.task, preserving_proto_field_name=True)
        return jsonify(task_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            return jsonify({'message': 'You have not permission to this task'}), 500
        return jsonify({'message': 'Unknown error'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    task_request = tasks_pb2.DeleteTaskRequest(id=task_id, author_id=current_user.id)
    try:
        response = grpc_client.DeleteTask(task_request)
        task_dict = MessageToDict(response.task, preserving_proto_field_name=True)
        return jsonify(task_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            return jsonify({'message': 'You have not permission to this task'}), 500
        return jsonify({'message': 'Unknown error'}), 500

@app.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    task_request = tasks_pb2.GetTaskRequest(id=task_id)
    try:
        response = grpc_client.GetTask(task_request)
        task_dict = MessageToDict(response.task, preserving_proto_field_name=True)
        return jsonify(task_dict)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            return jsonify({'message': 'You have not permission to this task'}), 500
        return jsonify({'message': 'Unknown error'}), 500

@app.route('/tasks', methods=['GET'])
@token_required
def list_tasks(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    task_list_request = tasks_pb2.TaskListRequest(page=page, page_size=page_size)
    try:
        response = grpc_client.ListTasks(task_list_request)
        return jsonify({'tasks': [MessageToDict(task, preserving_proto_field_name=True) for task in response.tasks], 'total_count': response.total_count})
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            return jsonify({'message': 'You have not permission to this task'}), 500
        return jsonify({'message': 'Unknown error'}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)