from concurrent import futures
import grpc
from datetime import datetime
from models import Task
import database
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание логгера
logger = logging.getLogger("")

import grpc
import concurrent.futures as futures
import tasks_pb2
import tasks_pb2_grpc


class TaskService(tasks_pb2_grpc.TaskServiceServicer):
    def CreateTask(self, request, context):
        new_task = Task(
            title=request.title,
            description=request.description,
            deadline=datetime.strptime(request.deadline, '%Y-%m-%d %H:%M:%S'),
            author_id=request.author_id
        )
        session.add(new_task)
        session.commit()
        return tasks_pb2.TaskResponse(task=new_task.to_proto())

    def UpdateTask(self, request, context):
        task = session.query(Task).get(request.id)
        if task.author_id != request.author_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'You have not permission to this task')

        if task:
            task.title = request.title or task.title
            task.description = request.description or task.description
            task.deadline = datetime.strptime(request.deadline, '%Y-%m-%d %H:%M:%S') if request.deadline else task.deadline
            task.is_completed = request.is_completed
            session.commit()
            return tasks_pb2.TaskResponse(task=task.to_proto())
        context.abort(grpc.StatusCode.NOT_FOUND, 'Task not found')

    def DeleteTask(self, request, context):
        task = session.query(Task).get(request.id)
        if task.author_id != request.author_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'You have not permission to this task')

        if task:
            session.delete(task)
            session.commit()
            return tasks_pb2.TaskResponse(task=task.to_proto())
        context.abort(grpc.StatusCode.NOT_FOUND, 'Task not found')
        
    def GetTask(self, request, context):
        task = session.query(Task).get(request.id)
        if task:
            return tasks_pb2.TaskResponse(task=task.to_proto())
        context.abort(grpc.StatusCode.NOT_FOUND, 'Task not found')

    def ListTasks(self, request, context):
        tasks_query = session.query(Task)
        total_count = tasks_query.count()
        tasks_query = tasks_query.offset((request.page - 1) * request.page_size).limit(request.page_size)
        tasks = tasks_query.all()
        return tasks_pb2.TaskListResponse(tasks=[t.to_proto() for t in tasks], total_count=total_count)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tasks_pb2_grpc.add_TaskServiceServicer_to_server(TaskService(), server)
    server.add_insecure_port('[::]:5005')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    session = database.get_db_session()
    serve()